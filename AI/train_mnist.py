#!/usr/bin/env python3
"""Train a ternary neural network on MNIST with configurable depth.

Uses the installed `trinary.ai` package (run `pip install -e .` first).
Hill-climbing for small models, STE gradient descent for larger ones.

Usage:
    python AI/train_mnist.py                           # default: 784→32→10, STE
    python AI/train_mnist.py --method hill --trials 50 # hill-climbing
    python AI/train_mnist.py --layers 2 --width 64     # deeper, wider
    python AI/train_mnist.py --eval-only                # test saved model
"""

import argparse
import json
import os
import random
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODELS_DIR = os.path.join(_HERE, "models")


def load_mnist_ternary(train_samples=1000, test_samples=200, seed=42):
    """Load MNIST from trinary.ai package, ternary-encoded."""
    try:
        from trinary.ai.mnist import load_mnist
    except ImportError:
        print("Run 'pip install -e .' first to install the trinary package")
        sys.exit(1)

    train_full, test_full = load_mnist(ternary=True)
    rng = random.Random(seed)
    train = rng.sample(train_full, min(train_samples, len(train_full)))
    test = rng.sample(test_full, min(test_samples, len(test_full)))
    return train, test


# ---------------------------------------------------------------------------
# Reuse the hill-climbing trainer from train.py for small MNIST models
# ---------------------------------------------------------------------------

def _import_train():
    import importlib.util
    spec = importlib.util.spec_from_file_location("train",
        os.path.join(_HERE, "train.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def train_hillclimb_mnist(train_data, test_data, layer_sizes,
                          trials=100, epochs=500, seed=42, verbose=False):
    tmod = _import_train()
    from train import TernaryNN, _copy_net, _mutate_net

    n_in = layer_sizes[0]
    best_acc, best_test = 0.0, 0.0
    best_model = None

    for trial in range(trials):
        model = TernaryNN.build(layer_sizes, seed=seed + trial)
        cur = _copy_net(model)
        cur_acc = tmod.accuracy(cur, train_data)

        for ep in range(epochs):
            cand = _copy_net(cur)
            _mutate_net(cand)

            cand_acc = tmod.accuracy(cand, train_data)
            if cand_acc > cur_acc:
                cur = cand
                cur_acc = cand_acc

            if cur_acc > best_acc:
                best_acc = cur_acc
                best_model = _copy_net(cur)
                best_test = tmod.accuracy(best_model, test_data)
                if verbose:
                    print(f"  trial {trial+1:3d}/{trials} ep {ep+1:4d} — "
                          f"train {best_acc:.1%} test {best_test:.1%}")
            if best_acc >= 1.0:
                break
        if best_acc >= 1.0:
            break

    return best_model, best_acc, best_test


def train_ste_mnist(train_data, test_data, layer_sizes,
                    epochs=50, lr=0.01, batch_size=64, seed=42, verbose=False):
    """Straight-Through Estimator training (real-valued weights, ternary fwd)."""
    from trinary.ai.activations import signed_to_trit, trit_to_signed, ternary_step
    import math

    rng = random.Random(seed)
    n_layers = len(layer_sizes) - 1

    # Init real-valued weights
    w = []
    b = []
    for i in range(n_layers):
        ni, no = layer_sizes[i], layer_sizes[i + 1]
        scale = math.sqrt(2.0 / ni)
        w.append([[rng.gauss(0, scale) for _ in range(ni)] for _ in range(no)])
        b.append([0.0 for _ in range(no)])

    def ternarize(v):
        return 0 if v < -0.33 else 2 if v > 0.33 else 1

    def ternarize_all():
        tw = [[[ternarize(v) for v in row] for row in layer_w] for layer_w in w]
        tb = [[ternarize(v) for v in layer_b] for layer_b in b]
        return tw, tb

    def forward(inputs, ternary_w=True):
        cur = [x - 1 for x in inputs]
        tw, tb = ternarize_all() if ternary_w else (w, b)
        for li in range(n_layers):
            nxt = []
            for k in range(len(tw[li])):
                total = (tb[li][k] - 1) if ternary_w else tb[li][k]
                for j in range(len(cur)):
                    w_signed = (tw[li][k][j] - 1) if ternary_w else max(-1, min(1, tw[li][k][j]))
                    total += cur[j] * w_signed
                nxt.append(ternary_step(int(total)) if ternary_w else math.tanh(total))
            cur = nxt
        return cur

    def argmax(v):
        return max(range(len(v)), key=lambda i: v[i])

    def accuracy_ste(data):
        correct = 0
        for ins, tgt in data:
            out = forward(ins, True)
            correct += 1 if argmax(out) == argmax(tgt) else 0
        return correct / len(data)

    best_acc, best_test = 0.0, 0.0
    best_snapshot = None

    for ep in range(epochs):
        shuffled = list(train_data)
        random.shuffle(shuffled)

        for start in range(0, len(shuffled), batch_size):
            batch = shuffled[start:start + batch_size]
            w_grad = [[[0.0] * len(w[li][k]) for k in range(len(w[li]))] for li in range(n_layers)]
            b_grad = [[0.0] * len(b[li]) for li in range(n_layers)]

            for ins, tgt in batch:
                tw, tb = ternarize_all()
                layer_outs = [[x - 1 for x in ins]]
                for li in range(n_layers):
                    cur = []
                    inp = layer_outs[-1]
                    for k in range(len(tw[li])):
                        total = tb[li][k] - 1
                        for j in range(len(inp)):
                            total += inp[j] * (tw[li][k][j] - 1)
                        cur.append(ternary_step(int(total)))
                    layer_outs.append(cur)

                output = layer_outs[-1]
                if output == tgt:
                    continue

                tgt_class = argmax(tgt)
                out_class = argmax(output)
                out_error = [0.0] * len(output)
                out_error[tgt_class] = 1.0
                if out_class != tgt_class:
                    out_error[out_class] = -1.0

                errors = [None] * n_layers
                errors[-1] = out_error
                for li in range(n_layers - 2, -1, -1):
                    curr_err = []
                    for j in range(len(w[li])):
                        err = sum(errors[li + 1][k] * max(-1, min(1, w[li + 1][k][j])) for k in range(len(w[li + 1])))
                        curr_err.append(err)
                    errors[li] = curr_err

                for li in range(n_layers):
                    inp = layer_outs[li]
                    for k in range(len(w[li])):
                        e = errors[li][k]
                        if abs(e) < 1e-10:
                            continue
                        for j in range(len(w[li][k])):
                            w_grad[li][k][j] += inp[j] * e
                        b_grad[li][k] += e

            for li in range(n_layers):
                for k in range(len(w[li])):
                    for j in range(len(w[li][k])):
                        grad = w_grad[li][k][j] / len(batch)
                        if abs(grad) > 1e-10:
                            w[li][k][j] += lr * grad
                            w[li][k][j] = max(-1, min(1, w[li][k][j]))
                    grad_b = b_grad[li][k] / len(batch)
                    if abs(grad_b) > 1e-10:
                        b[li][k] += lr * grad_b
                        b[li][k] = max(-1, min(1, b[li][k]))

        acc = accuracy_ste(train_data)
        te = accuracy_ste(test_data)
        if acc > best_acc:
            best_acc = acc
            best_test = te
            best_snapshot = ([list(list(row) for row in layer_w) for layer_w in w],
                             [list(layer_b) for layer_b in b])
        if verbose:
            print(f"  epoch {ep+1:3d}/{epochs} — train {acc:.1%} test {te:.1%}")

    # Build a TernaryNN from the best ternary weights
    if best_snapshot:
        bw, bb = best_snapshot
        tw, tb = ternarize_all()
        best_w = [[[ternarize(v) for v in row] for row in layer_w] for layer_w in bw]
        best_b = [[ternarize(v) for v in layer_b] for layer_b in bb]
    else:
        tw, tb = ternarize_all()
        best_w, best_b = tw, tb

    from train import TernaryNN, Perceptron
    layers = []
    for li in range(n_layers):
        neurons = []
        for k in range(len(best_w[li])):
            neurons.append(Perceptron(best_w[li][k], best_b[li][k]))
        layers.append(neurons)
    model = TernaryNN(layers)
    return model, best_acc, best_test


def main():
    ap = argparse.ArgumentParser(description="Train ternary NN on MNIST")
    ap.add_argument("--method", choices=["ste", "hill"], default="ste")
    ap.add_argument("--layers", type=int, default=1)
    ap.add_argument("--width", type=int, default=32)
    ap.add_argument("--train-size", type=int, default=1000)
    ap.add_argument("--test-size", type=int, default=200)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--trials", type=int, default=100)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--eval-only", action="store_true")
    ap.add_argument("--model", default=os.path.join(_MODELS_DIR, "mnist_best.json"))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    random.seed(args.seed)
    os.makedirs(_MODELS_DIR, exist_ok=True)

    if args.eval_only:
        from train import TernaryNN
        model = TernaryNN.load(args.model)
        _, test = load_mnist_ternary(train_samples=10, test_samples=200, seed=args.seed)
        acc = sum(1 for ins, tgt in test if model.forward(ins) == tgt) / len(test)
        print(f"Model: {args.model}")
        print(f"Architecture: {[model.layers[0][0].weights.__len__()] + [len(l) for l in model.layers]}")
        print(f"Test accuracy: {acc:.1%}")
        return

    print(f"Loading MNIST ({args.train_size} train, {args.test_size} test)...")
    train, test = load_mnist_ternary(
        train_samples=args.train_size,
        test_samples=args.test_size,
        seed=args.seed,
    )
    n_in = len(train[0][0])
    n_out = len(train[0][1])
    layer_sizes = [n_in] + [args.width] * args.layers + [n_out]
    print(f"Architecture: {' × '.join(str(s) for s in layer_sizes)}")

    t0 = time.time()
    if args.method == "hill":
        model, train_acc, test_acc = train_hillclimb_mnist(
            train, test, layer_sizes,
            trials=args.trials,
            epochs=args.epochs,
            seed=args.seed,
            verbose=args.verbose,
        )
    else:
        model, train_acc, test_acc = train_ste_mnist(
            train, test, layer_sizes,
            epochs=args.epochs,
            lr=args.lr,
            seed=args.seed,
            verbose=args.verbose,
        )

    dt = time.time() - t0
    print(f"\nTrain accuracy: {train_acc:.1%}")
    print(f"Test accuracy:  {test_acc:.1%}")
    print(f"Parameters: {model.num_params}")
    print(f"Time: {dt:.1f}s")

    model.save(args.model, test_acc)
    print(f"Saved to {args.model}")


if __name__ == "__main__":
    main()

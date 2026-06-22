#!/usr/bin/env python3
"""Train ternary neural network on MNIST — CPU or GPU.

GPU uses PyTorch CUDA for batched matrix operations (10-100× faster).
CPU uses pure-Python hill-climbing (tiny models) or STE loop.

Usage:
    python AI/train_mnist.py                              # auto-detect GPU
    python AI/train_mnist.py --backend cpu                 # force CPU
    python AI/train_mnist.py --layers 2 --width 128        # deeper, wider
    python AI/train_mnist.py --train-size 5000 --epochs 100
    python AI/train_mnist.py --eval-only                   # test saved model
"""

import argparse
import json
import os
import random
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODELS_DIR = os.path.join(_HERE, "models")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load_mnist_ternary(train_samples=1000, test_samples=200, seed=42):
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


def _make_batches(data, batch_size):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]


# ---------------------------------------------------------------------------
# GPU trainer (PyTorch STE) — fast, batched, vectorized
# ---------------------------------------------------------------------------

def train_gpu(train_data, test_data, layer_sizes,
              epochs=100, lr=0.01, batch_size=128, seed=42, verbose=False):
    import torch
    import torch.nn as nn

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(seed)
    n_layers = len(layer_sizes) - 1

    # ── STE autograd: ternary in forward, identity in backward ──
    class TernarizeFn(torch.autograd.Function):
        @staticmethod
        def forward(ctx, x):
            return torch.where(x < -0.33, -1.0, torch.where(x > 0.33, 1.0, 0.0))
        @staticmethod
        def backward(ctx, grad_output):
            return grad_output

    ternarize = TernarizeFn.apply

    class ClampFn(torch.autograd.Function):
        @staticmethod
        def forward(ctx, x):
            return torch.where(x > 0, 1.0, torch.where(x < 0, -1.0, 0.0))
        @staticmethod
        def backward(ctx, grad_output):
            return grad_output

    clamp = ClampFn.apply

    # ── Data ──
    def to_tensor(data):
        xs = torch.tensor([[x - 1 for x in ins] for ins, _ in data],
                          dtype=torch.float32, device=device)
        ys = torch.tensor([tgt.index(2) for _, tgt in data],
                          dtype=torch.long, device=device)
        return xs, ys

    X_train, y_train = to_tensor(train_data)
    X_test, y_test = to_tensor(test_data)
    n_train = X_train.shape[0]

    # ── Real-valued network ──
    layers = []
    for i in range(n_layers):
        ni, no = layer_sizes[i], layer_sizes[i + 1]
        lin = nn.Linear(ni, no, bias=True).to(device)
        nn.init.normal_(lin.weight, std=2.0 / ni ** 0.5)
        nn.init.zeros_(lin.bias)
        layers.append(lin)

    optim = torch.optim.SGD(
        [p for lin in layers for p in [lin.weight, lin.bias]], lr=lr)

    # ── STE forward pass ──
    def forward_ste(x):
        h = x
        for i, lin in enumerate(layers):
            w = ternarize(lin.weight)
            b = ternarize(lin.bias)
            h = h @ w.t() + b
            if i < n_layers - 1:
                h = clamp(h)  # ternary activation
        return h  # logits (no output activation)

    def accuracy(X, y):
        with torch.no_grad():
            logits = forward_ste(X)
            return (logits.argmax(dim=1) == y).float().mean().item()

    best_train, best_test = 0.0, 0.0
    best_state = None

    for ep in range(epochs):
        perm = torch.randperm(n_train, device=device)
        epoch_loss = 0.0
        n_batches = 0

        for i in range(0, n_train, batch_size):
            idx = perm[i:i + batch_size]
            xb, yb = X_train[idx], y_train[idx]

            logits = forward_ste(xb)
            loss = nn.functional.cross_entropy(logits, yb)

            optim.zero_grad()
            loss.backward()
            optim.step()

            epoch_loss += loss.item()
            n_batches += 1

        train_acc = accuracy(X_train, y_train)
        test_acc = accuracy(X_test, y_test)

        if train_acc > best_train:
            best_train = train_acc
            best_test = test_acc
            best_state = [{k: v.clone().cpu()
                          for k, v in lin.state_dict().items()}
                          for lin in layers]

        if verbose:
            print(f"  epoch {ep+1:3d}/{epochs} — train {train_acc:.1%} "
                  f"test {test_acc:.1%} loss {epoch_loss/n_batches:.4f}")

        if best_train >= 1.0:
            break

    # ── Extract best ternary weights into TernaryNN ──
    from train import TernaryNN, Perceptron
    ternary_layers = []
    for li in range(n_layers):
        sd = best_state[li]
        w = ternarize(sd["weight"])
        b = ternarize(sd["bias"])
        neurons = []
        for k in range(w.shape[0]):
            ws = [int(x) for x in (w[k] + 1).tolist()]
            bs = int(b[k] + 1)
            neurons.append(Perceptron(ws, bs))
        ternary_layers.append(neurons)
    model = TernaryNN(ternary_layers)
    return model, best_train, best_test


# ---------------------------------------------------------------------------
# CPU hill-climber (tiny models only — 784 inputs makes it very slow)
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

    best_acc, best_test = 0.0, 0.0
    best_model = None

    for trial in range(trials):
        model = TernaryNN.build(layer_sizes, seed=seed + trial)
        cur = _copy_net(model)
        cur_acc = tmod.accuracy(cur, train_data)

        for ep in range(epochs):
            cand = _copy_net(cur)
            for layer in cand.layers:
                for n in layer:
                    for i in range(len(n.weights)):
                        if random.random() < 0.1:
                            n.weights[i] = random.choice([0, 1, 2])
                    if random.random() < 0.1:
                        n.bias = random.choice([0, 1, 2])

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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Train ternary NN on MNIST")
    ap.add_argument("--backend", choices=["cpu", "gpu"], default=None,
                    help="Training backend (default: gpu if CUDA available)")
    ap.add_argument("--layers", type=int, default=1)
    ap.add_argument("--width", type=int, default=32)
    ap.add_argument("--train-size", type=int, default=1000)
    ap.add_argument("--test-size", type=int, default=200)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--eval-only", action="store_true")
    ap.add_argument("--model", default=os.path.join(_MODELS_DIR, "mnist_best.json"))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    random.seed(args.seed)
    os.makedirs(_MODELS_DIR, exist_ok=True)

    import torch
    has_cuda = torch.cuda.is_available()
    backend = args.backend or ("gpu" if has_cuda else "cpu")

    if args.eval_only:
        from train import TernaryNN
        model = TernaryNN.load(args.model)
        _, test = load_mnist_ternary(train_samples=10, test_samples=200, seed=args.seed)
        acc = sum(1 for ins, tgt in test
                  if model.forward(ins) == tgt) / len(test)
        layers_info = [len(l[0].weights) for l in model.layers] + [len(l) for l in model.layers]
        print(f"Model: {args.model}")
        print(f"Architecture: {layers_info}")
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
    print(f"Backend: {backend.upper()}")
    t0 = time.time()

    if backend == "gpu":
        model, train_acc, test_acc = train_gpu(
            train, test, layer_sizes,
            epochs=args.epochs, lr=args.lr, batch_size=args.batch_size,
            seed=args.seed, verbose=args.verbose,
        )
    elif args.layers == 0 and args.width == 0:
        from train import train_single, Perceptron
        p = Perceptron([random.choice([0, 1, 2]) for _ in range(n_in)],
                       random.choice([0, 1, 2]))
        train_single(p, train, epochs=min(args.epochs, 300))
        from train import TernaryNN
        model = TernaryNN([[p]])
        train_acc = sum(1 for ins, tgt in train if model.forward(ins) == tgt) / len(train)
        test_acc = sum(1 for ins, tgt in test if model.forward(ins) == tgt) / len(test)
    else:
        model, train_acc, test_acc = train_hillclimb_mnist(
            train, test, layer_sizes,
            trials=10, epochs=args.epochs,
            seed=args.seed, verbose=args.verbose,
        )

    dt = time.time() - t0
    total_params = sum(
        layer_sizes[i] * layer_sizes[i + 1] + layer_sizes[i + 1]
        for i in range(len(layer_sizes) - 1)
    )
    print(f"\nTrain accuracy: {train_acc:.1%}")
    print(f"Test accuracy:  {test_acc:.1%}")
    print(f"Parameters: {total_params}")
    print(f"Time: {dt:.1f}s")

    model.save(args.model, test_acc)
    print(f"Saved to {args.model}")


if __name__ == "__main__":
    main()

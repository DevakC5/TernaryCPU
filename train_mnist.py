#!/usr/bin/env python3
"""Train a ternary neural network on MNIST using Straight-Through Estimator (STE).

Maintains real-valued weights during training, ternarized for forward pass.
This is the standard approach from BNN/TNN literature.

Usage:
    python train_mnist.py                               # CPU, default
    python train_mnist.py --epochs 200 --hidden 64      # deeper
    python train_mnist.py --train-size 5000             # more data
    python train_mnist.py --load models/foo.json --eval-only
"""

import argparse
import json
import math
import os
import random
import time

from trinary.ai.mnist import load_mnist
from trinary.ai.activations import trit_to_signed, signed_to_trit, ternary_step


def ternarize(v):
    """Convert a real value to ternary digit {0, 1, 2}.
     v < -0.33 → 0, |v| <= 0.33 → 1, v > 0.33 → 2
    """
    if v < -0.33:
        return 0
    elif v > 0.33:
        return 2
    return 1


def signed(v):
    """Convert real or ternary digit to signed {-1, 0, 1}."""
    if isinstance(v, float):
        return max(-1, min(1, v))
    return v - 1


class STENetwork:
    """Real-valued network trained with STE for ternary inference.

    Stores real-valued weights, ternarizes for forward pass.
    """

    def __init__(self, layer_sizes, seed=42):
        rng = random.Random(seed)
        self.layer_sizes = layer_sizes
        # Real-valued weights and biases (Gaussian initialization)
        self.w = []
        self.b = []
        for i in range(len(layer_sizes) - 1):
            ni, no = layer_sizes[i], layer_sizes[i + 1]
            scale = math.sqrt(2.0 / ni)
            w = [[rng.gauss(0, scale) for _ in range(ni)] for _ in range(no)]
            b = [0.0 for _ in range(no)]
            self.w.append(w)
            self.b.append(b)

    def ternarize_weights(self):
        """Return ternarized copies of weights and biases."""
        tw = []
        tb = []
        for layer_w, layer_b in zip(self.w, self.b):
            tw.append([[ternarize(v) for v in row] for row in layer_w])
            tb.append([ternarize(v) for v in layer_b])
        return tw, tb

    def forward(self, inputs, ternary=False):
        """Forward pass. If ternary=True, use ternarized weights."""
        current = [x - 1 for x in inputs]  # signed inputs
        for li in range(len(self.layer_sizes) - 1):
            if ternary:
                tw, tb = self.ternarize_weights()
                w, b = tw[li], tb[li]
            else:
                w, b = self.w[li], self.b[li]

            n_out = len(w)
            next_out = []
            for k in range(n_out):
                total = signed(b[k])
                for j in range(len(current)):
                    total += current[j] * signed(w[k][j])
                # Use tanh-like activation for real-valued, ternary_step for ternary
                if ternary:
                    next_out.append(ternary_step(int(total)))
                else:
                    out_val = math.tanh(total)
                    next_out.append(out_val)
            current = next_out

        if ternary:
            return current  # list of ternarized outputs (0/1/2)
        return current  # list of floats (-1 to 1)

    def predict(self, inputs):
        """Return ternary prediction."""
        out = self.forward(inputs, ternary=True)
        # Find max activation
        best = max(range(len(out)), key=lambda i: out[i])
        return [0] * best + [2] + [0] * (9 - best)

    def predict_raw(self, inputs):
        """Return raw output vector without ternarization."""
        return self.forward(inputs, ternary=True)

    def accuracy(self, data):
        correct = 0
        for inputs, target in data:
            if self.predict(inputs) == target:
                correct += 1
        return correct / len(data)

    def save(self, filepath):
        """Save ternarized weights to JSON."""
        tw, tb = self.ternarize_weights()
        data = {
            "format": "ste_ternary_v1",
            "layer_sizes": self.layer_sizes,
            "real_weights": self.w,
            "real_biases": self.b,
            "ternary_weights": tw,
            "ternary_biases": tb,
        }
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath):
        with open(filepath) as f:
            data = json.load(f)
        net = cls.__new__(cls)
        net.layer_sizes = data["layer_sizes"]
        net.w = data["real_weights"]
        net.b = data["real_biases"]
        return net


def train_epoch_ste(net, train_data, lr=0.01, batch_size=64):
    """One epoch of STE training with proper gradient propagation.

    Forward pass uses ternarized weights and ternary_step activation.
    Backward pass uses STE: identity approximation through activation.
    """
    shuffled = list(train_data)
    random.shuffle(shuffled)
    n_layers = len(net.layer_sizes) - 1
    correct = 0

    for start in range(0, len(shuffled), batch_size):
        batch = shuffled[start:start + batch_size]

        w_grad = [[[0.0] * len(net.w[li][k]) for k in range(len(net.w[li]))]
                  for li in range(n_layers)]
        b_grad = [[0.0] * len(net.b[li]) for li in range(n_layers)]

        for inputs, target in batch:
            # Forward pass with ternarized weights, store all layer outputs
            tw, tb = net.ternarize_weights()
            layer_outputs = [[x - 1 for x in inputs]]  # signed inputs as first layer output
            for li in range(n_layers):
                cur = []
                w, b = tw[li], tb[li]
                inp = layer_outputs[-1]
                for k in range(len(w)):
                    total = signed(b[k])
                    for j in range(len(inp)):
                        total += inp[j] * signed(w[k][j])
                    cur.append(ternary_step(int(total)))
                layer_outputs.append(cur)

            output = layer_outputs[-1]

            if output == target:
                correct += 1
                continue

            tgt_class = target.index(2)

            # Compute output error in signed space
            out_error = []
            for k in range(len(output)):
                e = signed(target[k]) - signed(output[k])
                out_error.append(max(-1, min(1, e)))

            # Backprop through all layers (STE: identity activation derivative)
            errors = [None] * n_layers
            errors[-1] = out_error
            for li in range(n_layers - 2, -1, -1):
                curr_err = []
                for j in range(len(net.w[li])):
                    err = 0.0
                    for k in range(len(net.w[li + 1])):
                        w_kj = net.w[li + 1][k][j]  # use real-valued weight
                        err += errors[li + 1][k] * max(-1, min(1, w_kj))
                    curr_err.append(err)
                errors[li] = curr_err

            # Accumulate gradients using STE: dL/dW = inp * error
            for li in range(n_layers):
                inp = layer_outputs[li]  # signed input to this layer
                for k in range(len(net.w[li])):
                    e = errors[li][k]
                    if abs(e) < 1e-10:
                        continue
                    for j in range(len(net.w[li][k])):
                        w_grad[li][k][j] += inp[j] * e
                    b_grad[li][k] += e

        # Apply accumulated gradients
        for li in range(n_layers):
            for k in range(len(net.w[li])):
                for j in range(len(net.w[li][k])):
                    grad = w_grad[li][k][j] / len(batch)
                    if abs(grad) > 1e-10:
                        net.w[li][k][j] += lr * grad
                        net.w[li][k][j] = max(-1, min(1, net.w[li][k][j]))
                grad_b = b_grad[li][k] / len(batch)
                if abs(grad_b) > 1e-10:
                    net.b[li][k] += lr * grad_b
                    net.b[li][k] = max(-1, min(1, net.b[li][k]))

    return correct / len(train_data)


def main():
    parser = argparse.ArgumentParser(description="Train ternary NN on MNIST (STE)")
    parser.add_argument("--epochs", type=int, default=100, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.01, help="Learning rate")
    parser.add_argument("--hidden", type=int, default=32, help="Hidden layer size (0=linear)")
    parser.add_argument("--train-size", type=int, default=1000, help="Training samples")
    parser.add_argument("--test-size", type=int, default=200, help="Test samples")
    parser.add_argument("--output", default="models/mnist_model.json", help="Output path")
    parser.add_argument("--load", default=None, help="Load existing model")
    parser.add_argument("--eval-only", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    out_dir = os.path.dirname(args.output) or "."
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading MNIST ({args.train_size} train, {args.test_size} test)...")
    train_full, test_full = load_mnist(ternary=True)
    rng = random.Random(args.seed)
    train_data = rng.sample(train_full, min(args.train_size, len(train_full)))
    test_data = rng.sample(test_full, min(args.test_size, len(test_full)))
    print(f"  Train: {len(train_data)}, Test: {len(test_data)}")

    if args.load:
        print(f"Loading model from {args.load}")
        net = STENetwork.load(args.load)
        print(f"  Architecture: {net.layer_sizes}")
    else:
        arch = [784, args.hidden, 10] if args.hidden > 0 else [784, 10]
        print(f"Creating network: {' -> '.join(str(s) for s in arch)}")
        net = STENetwork(arch, seed=args.seed)

    total_params = sum(len(r) for l in net.w for r in l) + sum(len(l) for l in net.b)
    print(f"  Parameters: {total_params}")

    if args.eval_only:
        tr_acc = net.accuracy(train_data)
        te_acc = net.accuracy(test_data)
        print(f"\nTrain acc: {tr_acc:.4f} | Test acc: {te_acc:.4f}")
        return

    print(f"\nTraining {args.epochs} epochs (lr={args.lr}, batch={args.batch_size})...")
    print(f"{'Epoch':>6}  {'Train':>8}  {'Test':>8}  {'Time':>8}")
    print("-" * 32)

    best_test = 0.0
    best_ep = 0

    for ep in range(1, args.epochs + 1):
        t0 = time.time()
        _ = train_epoch_ste(net, train_data, lr=args.lr, batch_size=args.batch_size)
        tr_acc = net.accuracy(train_data)
        te_acc = net.accuracy(test_data)
        dt = time.time() - t0

        improved = te_acc > best_test
        if improved:
            best_test = te_acc
            best_ep = ep
            net.save(args.output.replace(".json", "_best.json"))

        if ep == 1 or ep == args.epochs or improved or ep % max(1, args.epochs // 10) == 0:
            print(f"{ep:>6}  {tr_acc:>8.4f}  {te_acc:>8.4f}  {dt:>7.2f}s{' *' if improved else ''}")

        if te_acc >= 1.0:
            break

    print(f"\nBest: epoch {best_ep}, test accuracy = {best_test:.4f}")
    net.save(args.output)
    print(f"Saved to {args.output}")

    # Also save as TernaryNeuralNetwork-compatible JSON
    tw, tb = net.ternarize_weights()
    tnn_data = {
        "format": "ternary_nn_v1",
        "layer_sizes": net.layer_sizes,
        "layers": [
            [{"weights": tw[li][k], "bias": int(tb[li][k])} for k in range(len(tw[li]))]
            for li in range(len(tw))
        ],
    }
    tnn_path = args.output.replace(".json", "_tnn.json")
    with open(tnn_path, "w") as f:
        json.dump(tnn_data, f, indent=2)
    print(f"TNN-compatible model saved to {tnn_path}")


if __name__ == "__main__":
    main()

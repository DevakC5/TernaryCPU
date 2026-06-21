#!/usr/bin/env python3
"""Self-contained ternary neural network trainer.

Supports single perceptrons (AND/OR/NAND) and multi-layer networks
trained via hill-climbing for harder problems (XOR, EQUALITY, patterns).

Usage:
    python AI/train.py                               # all gate demos
    python AI/train.py --dataset equality            # 9-example ternary equality
    python AI/train.py --dataset patterns            # 9-input pattern matching
    python AI/train.py --gate xor --hidden 4         # custom XOR width
    python AI/train.py --dataset equality --layers 3 --width 8  # deep dense
"""

import argparse
import os
import random
import json
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODELS_DIR = os.path.join(_HERE, "models")


# ---------------------------------------------------------------------------
# Ternary math
# ---------------------------------------------------------------------------

def signed(t):
    return t - 1  # 0→-1, 1→0, 2→+1

def to_trit(v):
    return 0 if v < -0.33 else 2 if v > 0.33 else 1

def ternary_step(v):
    return 1 if v == 0 else (2 if v > 0 else 0)


# ---------------------------------------------------------------------------
# Perceptron
# ---------------------------------------------------------------------------

class Perceptron:
    def __init__(self, weights, bias=1):
        self.weights = list(weights)
        self.bias = bias

    def forward(self, inputs):
        total = signed(self.bias)
        for x, w in zip(inputs, self.weights):
            total += signed(x) * signed(w)
        return ternary_step(total)

    def copy(self):
        return Perceptron(list(self.weights), self.bias)


# ---------------------------------------------------------------------------
# Multi-layer network
# ---------------------------------------------------------------------------

class TernaryNN:
    def __init__(self, layers):
        self.layers = layers  # list of list of Perceptron

    def forward(self, inputs):
        cur = list(inputs)
        for layer in self.layers:
            cur = [n.forward(cur) for n in layer]
        return cur

    @property
    def num_params(self):
        return sum(len(n.weights) + 1 for layer in self.layers for n in layer)

    def save(self, path, acc=0.0, loss=None):
        data = {
            "format": "ternary_nn_v1",
            "accuracy": acc,
            "loss": loss,
            "architecture": [len(layer) for layer in self.layers],
            "layers": [
                [{"weights": n.weights, "bias": n.bias} for n in layer]
                for layer in self.layers
            ],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path):
        with open(path) as f:
            data = json.load(f)
        layers = [
            [Perceptron(nd["weights"], nd["bias"]) for nd in layer]
            for layer in data["layers"]
        ]
        return cls(layers)

    @classmethod
    def build(cls, layer_sizes, seed=None):
        rng = random.Random(seed)
        layers = []
        for i in range(len(layer_sizes) - 1):
            n_in = layer_sizes[i]
            n_out = layer_sizes[i + 1]
            neurons = []
            for _ in range(n_out):
                w = [rng.choice([0, 1, 2]) for _ in range(n_in)]
                b = rng.choice([0, 1, 2])
                neurons.append(Perceptron(w, b))
            layers.append(neurons)
        return cls(layers)


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------

AND = [([0, 0], [0]), ([0, 2], [0]), ([2, 0], [0]), ([2, 2], [2])]
OR  = [([0, 0], [0]), ([0, 2], [2]), ([2, 0], [2]), ([2, 2], [2])]
XOR = [([0, 0], [0]), ([0, 2], [2]), ([2, 0], [2]), ([2, 2], [0])]
NAND = [([0, 0], [2]), ([0, 2], [2]), ([2, 0], [2]), ([2, 2], [0])]

TERNARY_EQUALITY = [
    ([0, 0], [2]), ([0, 1], [0]), ([0, 2], [0]),
    ([1, 0], [0]), ([1, 1], [2]), ([1, 2], [0]),
    ([2, 0], [0]), ([2, 1], [0]), ([2, 2], [2]),
]

TERNARY_TRUTH_TABLE = [
    ([0, 0], [1]), ([0, 1], [1]), ([0, 2], [1]),
    ([1, 0], [1]), ([1, 1], [1]), ([1, 2], [1]),
    ([2, 0], [1]), ([2, 1], [1]), ([2, 2], [1]),
]

TINY_PATTERNS = [
    ([2, 0, 2, 0, 2, 0, 2, 0, 2], [2]),
    ([0, 2, 0, 2, 0, 2, 0, 2, 0], [0]),
]

PATTERN_CROSS = [
    ([0, 2, 0, 2, 2, 2, 0, 2, 0], [2]),
    ([2, 0, 2, 0, 2, 0, 2, 0, 2], [0]),
]

DATASETS = {
    "and": AND, "or": OR, "xor": XOR, "nand": NAND,
    "equality": TERNARY_EQUALITY,
    "truth_table": TERNARY_TRUTH_TABLE,
    "patterns": TINY_PATTERNS,
    "cross": PATTERN_CROSS,
}


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def accuracy(model, dataset):
    correct = 0
    for ins, tgt in dataset:
        out = model.forward(ins)
        if isinstance(out, list):
            correct += 1 if out == tgt else 0
        else:
            correct += 1 if [out] == tgt else 0
    return correct / len(dataset)


def classification_error(model, dataset):
    total = 0.0
    for ins, tgt in dataset:
        out = model.forward(ins)
        out_list = out if isinstance(out, list) else [out]
        total += sum(abs(signed(o) - signed(t)) for o, t in zip(out_list, tgt))
    return total / len(dataset)


def split_dataset(dataset, ratio=0.75, seed=None):
    rng = random.Random(seed)
    items = list(dataset)
    rng.shuffle(items)
    split = max(1, int(len(items) * ratio))
    return items[:split], items[split:]


# ---------------------------------------------------------------------------
# Single perceptron trainer (batch SGD)
# ---------------------------------------------------------------------------

def train_single(model, dataset, epochs=300):
    best_acc, best_w, best_b = 0.0, None, None
    for ep in range(epochs):
        dw = [0] * len(model.weights)
        db = 0
        for ins, tgt in dataset:
            pred = model.forward(ins)
            err = max(-1, min(1, signed(tgt[0]) - signed(pred)))
            si = [signed(x) for x in ins]
            for i in range(len(model.weights)):
                dw[i] += si[i] * err
            db += err
        for i in range(len(model.weights)):
            d = max(-1, min(1, dw[i]))
            nw = max(-1, min(1, signed(model.weights[i]) + d))
            model.weights[i] = to_trit(nw)
        d = max(-1, min(1, db))
        nb = max(-1, min(1, signed(model.bias) + d))
        model.bias = to_trit(nb)

        acc = accuracy(model, dataset)
        if acc > best_acc:
            best_acc, best_w, best_b = acc, list(model.weights), model.bias
        if acc >= 1.0:
            break
    if best_w:
        model.weights = best_w
        model.bias = best_b
    return best_acc


# ---------------------------------------------------------------------------
# Hill-climbing trainer for multi-layer networks
# ---------------------------------------------------------------------------

def _mutate(p, rate=0.3):
    for i in range(len(p.weights)):
        if random.random() < rate:
            p.weights[i] = random.choice([0, 1, 2])
    if random.random() < rate:
        p.bias = random.choice([0, 1, 2])


def _copy_net(model):
    layers = [[Perceptron(list(n.weights), n.bias) for n in layer]
              for layer in model.layers]
    return TernaryNN(layers)


def _mutate_net(model, rate=0.3):
    for layer in model.layers:
        for n in layer:
            _mutate(n, rate)


def train_hillclimb(dataset, layer_sizes, trials=200, epochs=500, seed=None,
                    test_split=0.0, verbose=False):
    """Hill-climbing trainer for multi-layer ternary networks.

    Returns (best_model, best_train_acc, best_test_acc, best_loss).
    """
    if test_split > 0:
        train_data, test_data = split_dataset(dataset, ratio=1 - test_split, seed=seed)
    else:
        train_data = dataset
        test_data = []

    best_acc, best_test_acc, best_loss = 0.0, 0.0, float("inf")
    best_model = None
    rng = random.Random

    for trial in range(trials):
        model = TernaryNN.build(layer_sizes, seed=(seed or 0) + trial)
        cur = _copy_net(model)
        cur_acc = accuracy(cur, train_data)

        for ep in range(epochs):
            candidate = _copy_net(cur)
            _mutate_net(candidate, rate=0.3)

            cand_acc = accuracy(candidate, train_data)
            if cand_acc > cur_acc or (cand_acc == cur_acc and
                                        classification_error(candidate, train_data) <
                                        classification_error(cur, train_data)):
                cur = candidate
                cur_acc = cand_acc

            if cur_acc > best_acc or (cur_acc == best_acc and
                                       classification_error(cur, train_data) < best_loss):
                best_acc = cur_acc
                best_loss = classification_error(cur, train_data)
                best_model = _copy_net(cur)
                best_test_acc = accuracy(best_model, test_data) if test_data else best_acc
                if verbose:
                    te = best_test_acc if test_data else best_acc
                    print(f"  trial {trial+1:3d}/{trials} ep {ep+1:4d} — "
                          f"train {best_acc:.0%} test {te:.0%} loss {best_loss:.2f}")

            if best_acc >= 1.0:
                break
        if best_acc >= 1.0:
            break

    return best_model, best_acc, best_test_acc, best_loss


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Ternary neural network trainer")
    ap.add_argument("--gate", choices=[k for k in DATASETS if k != "equality"],
                    help="Train a specific logic gate")
    ap.add_argument("--dataset", choices=list(DATASETS),
                    default=None, help="Dataset to train on")
    ap.add_argument("--layers", type=int, default=0,
                    help="Hidden layers (0 = single perceptron)")
    ap.add_argument("--width", type=int, default=4,
                    help="Neurons per hidden layer")
    ap.add_argument("--epochs", type=int, default=1000)
    ap.add_argument("--trials", type=int, default=300)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--test", type=float, default=0.0,
                    help="Test split ratio (e.g. 0.25)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    random.seed(args.seed)
    os.makedirs(_MODELS_DIR, exist_ok=True)

    dataset_name = args.dataset or args.gate or "all"
    if dataset_name == "all":
        targets = list(DATASETS)
    else:
        targets = [dataset_name]

    for name in targets:
        ds = DATASETS[name]
        n_in = len(ds[0][0])
        n_out = len(ds[0][1])

        can_single = name in ("and", "or", "nand")
        use_single = can_single and args.layers == 0

        if use_single:
            # Single perceptron with batch SGD
            print(f"\n=== {name.upper()} (single perceptron) ===")
            p = Perceptron([random.choice([0, 1, 2]) for _ in range(n_in)],
                           random.choice([0, 1, 2]))
            acc = train_single(p, ds, epochs=min(args.epochs, 300))
            loss = classification_error(p, ds)
            print(f"  Weights: {p.weights}, Bias: {p.bias}")
            print(f"  Accuracy: {acc:.0%}  Error: {loss:.2f}")
            for ins, _ in ds:
                print(f"    {ins} → [{p.forward(ins)}]")
            model = TernaryNN([[p]])
            model.save(os.path.join(_MODELS_DIR, f"{name}.json"), acc, loss)

        else:
            # Multi-layer hill-climbing
            if name in ("and", "or", "nand") and args.layers == 0:
                continue

            layer_sizes = [n_in]
            if args.layers > 0:
                layer_sizes.extend([args.width] * args.layers)
            layer_sizes.append(n_out)

            print(f"\n=== {name.upper()} ({' × '.join(str(s) for s in layer_sizes)}) ===")
            t0 = time.time()
            model, train_acc, test_acc, loss = train_hillclimb(
                ds, layer_sizes,
                trials=args.trials,
                epochs=args.epochs,
                seed=args.seed,
                test_split=args.test,
                verbose=args.verbose,
            )
            dt = time.time() - t0
            params = model.num_params
            print(f"  Architecture: {' × '.join(str(s) for s in layer_sizes)}")
            print(f"  Parameters: {params}")
            print(f"  Train accuracy: {train_acc:.0%}  Test accuracy: {test_acc:.0%}")
            print(f"  Error: {loss:.2f}  Time: {dt:.1f}s")
            for ins, _ in ds:
                print(f"    {ins} → {model.forward(ins)}")
            model.save(os.path.join(_MODELS_DIR, f"{name}.json"), max(train_acc, test_acc), loss)

    print(f"\nDone. Models in {_MODELS_DIR}")


if __name__ == "__main__":
    main()

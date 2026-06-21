#!/usr/bin/env python3
"""Self-contained ternary neural network — train on logic gates.

Usage:
    python AI/train.py               # train all gates
    python AI/train.py --gate xor    # train XOR (needs 2-layer network)
    python AI/train.py --gate and    # single perceptron is enough
"""

import argparse
import os
import random
import math
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODELS_DIR = os.path.join(_HERE, "models")


# ---------------------------------------------------------------------------
# Ternary helpers
# ---------------------------------------------------------------------------

def signed(trit):
    return trit - 1  # 0→-1, 1→0, 2→+1


def to_trit(v):
    return 0 if v < -0.33 else 2 if v > 0.33 else 1


def ternary_step(v):
    return 1 if v == 0 else (2 if v > 0 else 0)


# ---------------------------------------------------------------------------
# Perceptron — one ternary neuron
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

    def save(self, path, acc=0.0):
        data = {
            "format": "ternary_nn_v1",
            "accuracy": acc,
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


# ---------------------------------------------------------------------------
# Datasets (ternary digits 0/1/2)
# ---------------------------------------------------------------------------

AND = [([0, 0], [0]), ([0, 2], [0]), ([2, 0], [0]), ([2, 2], [2])]
OR  = [([0, 0], [0]), ([0, 2], [2]), ([2, 0], [2]), ([2, 2], [2])]
XOR = [([0, 0], [0]), ([0, 2], [2]), ([2, 0], [2]), ([2, 2], [0])]
NAND = [([0, 0], [2]), ([0, 2], [2]), ([2, 0], [2]), ([2, 2], [0])]

GATES = {"and": AND, "or": OR, "xor": XOR, "nand": NAND}


# ---------------------------------------------------------------------------
# Training
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


def train_single(model, dataset, epochs=100):
    """Train a single perceptron (batch SGD in ternary space)."""
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
            delta = max(-1, min(1, dw[i]))
            new_w = max(-1, min(1, signed(model.weights[i]) + delta))
            model.weights[i] = to_trit(new_w)
        delta_b = max(-1, min(1, db))
        new_b = max(-1, min(1, signed(model.bias) + delta_b))
        model.bias = to_trit(new_b)

        acc = accuracy(model, dataset)
        if acc > best_acc:
            best_acc, best_w, best_b = acc, list(model.weights), model.bias
        if acc >= 1.0:
            break

    if best_w:
        model.weights = best_w
        model.bias = best_b
    return best_acc


def rand_weights(n):
    return [random.choice([0, 1, 2]) for _ in range(n)]


def _mutate(p, rate=0.3):
    """Randomly flip weights/bias with given probability."""
    for i in range(len(p.weights)):
        if random.random() < rate:
            p.weights[i] = random.choice([0, 1, 2])
    if random.random() < rate:
        p.bias = random.choice([0, 1, 2])


def _copy_net(model):
    layers = [[Perceptron(list(n.weights), n.bias) for n in layer] for layer in model.layers]
    return TernaryNN(layers)


def train_xor(epochs=500):
    """Hill-climbing search for XOR since ternary gradient is too sparse."""
    best_acc, best_model = 0.0, None

    for trial in range(200):
        hidden = [Perceptron(rand_weights(2), random.choice([0, 1, 2]))
                  for _ in range(2)]
        out = Perceptron(rand_weights(2), random.choice([0, 1, 2]))
        model = TernaryNN([hidden, [out]])
        cur = _copy_net(model)
        cur_acc = accuracy(cur, XOR)

        for ep in range(epochs):
            candidate = _copy_net(cur)
            for n in candidate.layers[0]:
                _mutate(n)
            _mutate(candidate.layers[1][0])

            cand_acc = accuracy(candidate, XOR)
            if cand_acc >= cur_acc:
                cur = candidate
                cur_acc = cand_acc

            if cur_acc > best_acc:
                best_acc = cur_acc
                best_model = _copy_net(cur)
            if best_acc >= 1.0:
                break
        if best_acc >= 1.0:
            break

    return best_model, best_acc


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Train ternary neural network on logic gates")
    ap.add_argument("--gate", choices=list(GATES) + ["all"], default="all")
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)

    gates_to_run = list(GATES) if args.gate == "all" else [args.gate]

    os.makedirs(_MODELS_DIR, exist_ok=True)

    for name in gates_to_run:
        ds = GATES[name]
        if name == "xor":
            print(f"\n=== XOR (2-layer network) ===")
            model, acc = train_xor(epochs=args.epochs)
            print(f"  Test accuracy: {acc:.0%}")
            if acc >= 1.0:
                for ins, _ in ds:
                    print(f"    {ins} → {model.forward(ins)}")
            model.save(os.path.join(_MODELS_DIR, f"{name}.json"), acc)
        else:
            print(f"\n=== {name.upper()} (single perceptron) ===")
            p = Perceptron(rand_weights(2), random.choice([0, 1, 2]))
            acc = train_single(p, ds, epochs=args.epochs)
            print(f"  Weights: {p.weights}, Bias: {p.bias}")
            print(f"  Test accuracy: {acc:.0%}")
            for ins, _ in ds:
                print(f"    {ins} → [{p.forward(ins)}]")
            model = TernaryNN([[p]])
            model.save(os.path.join(_MODELS_DIR, f"{name}.json"), acc)

    # Summary
    print("\nDone. Models saved to AI/models/")

if __name__ == "__main__":
    main()

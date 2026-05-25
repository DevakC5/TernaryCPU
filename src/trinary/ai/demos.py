"""Training demos for the ternary neural network system.

Each demo function trains a model, prints progress, and shows
the learned weights and predictions.
"""

from trinary.ai.perceptron import Perceptron
from trinary.ai.ternary_nn import TernaryNeuralNetwork
from trinary.ai.trainer import TernaryTrainer
from trinary.ai.optimizers import TernaryHillClimber
from trinary.ai.datasets import (
    AND_DATASET,
    OR_DATASET,
    XOR_DATASET,
    TERNARY_EQUALITY,
)
from trinary.ai.learning_visualizer import (
    print_training_progress,
    print_weight_heatmap,
    print_confusion_matrix,
)
from trinary.ai.losses import classification_error


def train_and_demo():
    """Train a single perceptron on the AND dataset."""
    print()
    print("=" * 55)
    print("  AND Gate — Single Perceptron Training")
    print("=" * 55)
    p = Perceptron([1, 1], bias=1)
    trainer = TernaryTrainer(p, learning_rate=1, max_epochs=20, verbose=True)
    trainer.fit_and()
    print_weight_heatmap(p)
    print("  Predictions:")
    for inputs, target in AND_DATASET:
        pred = p.forward(inputs)
        err = classification_error(pred, target[0])
        status = "✓" if err == 0 else "✗"
        print(f"    {inputs} → {pred} (target {target[0]}) {status}")
    print()


def train_or_demo():
    """Train a single perceptron on the OR dataset."""
    print()
    print("=" * 55)
    print("  OR Gate — Single Perceptron Training")
    print("=" * 55)
    p = Perceptron([1, 1], bias=1)
    trainer = TernaryTrainer(p, learning_rate=1, max_epochs=20, verbose=True)
    trainer.fit_or()
    print_weight_heatmap(p)
    print("  Predictions:")
    for inputs, target in OR_DATASET:
        pred = p.forward(inputs)
        err = classification_error(pred, target[0])
        status = "✓" if err == 0 else "✗"
        print(f"    {inputs} → {pred} (target {target[0]}) {status}")
    print()


def xor_perceptron_demo():
    """Demonstrate that a single perceptron CANNOT learn XOR.

    This is a key educational result — XOR is not linearly
    separable, so a single perceptron will never converge.
    """
    print()
    print("=" * 55)
    print("  XOR — Single Perceptron (will fail)")
    print("=" * 55)
    print("  A single perceptron cannot learn XOR because")
    print("  XOR is not linearly separable.")
    print()
    p = Perceptron([1, 1], bias=1)
    trainer = TernaryTrainer(
        p, learning_rate=1, max_epochs=50, verbose=True
    )
    trainer.fit_xor()
    print_weight_heatmap(p)
    print("  Final predictions:")
    correct = 0
    for inputs, target in XOR_DATASET:
        pred = p.forward(inputs)
        err = classification_error(pred, target[0])
        if err == 0:
            correct += 1
        status = "✓" if err == 0 else "✗"
        print(f"    {inputs} → {pred} (target {target[0]}) {status}")
    print(f"  Accuracy: {correct}/{len(XOR_DATASET)}")
    print("  (As expected, a single layer cannot model XOR.)")
    print()


def xor_multi_layer_demo():
    """Train a multi-layer network on XOR using hill climbing.

    A multi-layer network CAN learn XOR because it can represent
    non-linear decision boundaries (e.g., NAND + OR → AND).
    """
    print()
    print("=" * 55)
    print("  XOR — Multi-Layer Network (hill climbing)")
    print("=" * 55)
    print("  A 2-layer network CAN learn XOR by combining")
    print("  non-linear transformations.")
    print()
    net = TernaryNeuralNetwork([
        [Perceptron([1, 1], bias=1),
         Perceptron([1, 1], bias=1)],
        [Perceptron([1, 1], bias=1)],
    ])
    climber = TernaryHillClimber(max_attempts=20, improvement_threshold=0.0)
    trainer = TernaryTrainer(
        net, max_epochs=200, optimizer=climber, verbose=True
    )
    trainer.fit_xor()
    print_weight_heatmap(net)
    print("  Final predictions:")
    correct = 0
    for inputs, target in XOR_DATASET:
        pred = net.forward(inputs)
        err = classification_error(pred, target)
        if err == 0:
            correct += 1
        status = "✓" if err == 0 else "✗"
        print(f"    {inputs} → {pred} (target {target}) {status}")
    print(f"  Accuracy: {correct}/{len(XOR_DATASET)}")
    if correct == len(XOR_DATASET):
        print("  ✓ Multi-layer network successfully learned XOR!")
    else:
        print("  (XOR convergence may need more epochs or restarts.)")
    print()


def ternary_equality_demo():
    """Train a network on the ternary equality dataset.

    TERNARY_EQUALITY maps pairs of ternary digits to 2 if
    equal, 0 if different.
    """
    print()
    print("=" * 55)
    print("  Ternary Equality — Multi-Layer Training")
    print("=" * 55)
    net = TernaryNeuralNetwork([
        [Perceptron([1, 1], bias=1),
         Perceptron([1, 1], bias=1)],
        [Perceptron([1, 1], bias=1)],
    ])
    climber = TernaryHillClimber(max_attempts=30, improvement_threshold=0.0)
    trainer = TernaryTrainer(
        net, max_epochs=300, optimizer=climber, verbose=True
    )
    trainer.train(TERNARY_EQUALITY)
    print_weight_heatmap(net)
    print("  Predictions:")
    correct = 0
    for inputs, target in TERNARY_EQUALITY:
        pred = net.forward(inputs)
        ok = pred == target
        if ok:
            correct += 1
        status = "✓" if ok else "✗"
        print(f"    {inputs} → {pred} (target {target}) {status}")
    print(f"  Accuracy: {correct}/{len(TERNARY_EQUALITY)}")
    print()


def run_all():
    """Run all demos in sequence."""
    train_and_demo()
    train_or_demo()
    xor_perceptron_demo()
    xor_multi_layer_demo()
    ternary_equality_demo()


if __name__ == "__main__":
    run_all()

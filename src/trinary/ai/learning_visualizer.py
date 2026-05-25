"""ASCII visualization tools for ternary neural network training.

Provides text-based rendering of training progress, weight
matrices, accuracy charts, and confusion matrices.
"""

from trinary.ai.activations import trit_to_signed
from trinary.ai.perceptron import Perceptron
from trinary.ai.ternary_nn import TernaryNeuralNetwork


def _signed_char(trit):
    return {0: "-1", 1: " 0", 2: "+1"}.get(trit, " ?")


def _bar_chart(value, width=20):
    filled = int(value * width)
    return "[" + "#" * filled + "." * (width - filled) + "]"


def print_training_progress(history, label="Training Progress"):
    """Print an ASCII training progress chart.

    Shows accuracy per epoch as a bar chart with key statistics.

    Args:
        history: List of float accuracy values per epoch.
        label: Optional heading label.
    """
    print()
    print("=" * 50)
    print(f"  {label}")
    print("=" * 50)
    if not history:
        print("  (no training data)")
        print()
        return
    best = max(history)
    final = history[-1]
    epochs = len(history)
    step = max(1, epochs // 10)
    for i in range(0, epochs, step):
        pct = history[i] * 100
        bar = _bar_chart(history[i])
        marker = " <-- best" if history[i] == best else ""
        print(f"  Epoch {i + 1:4d}: {bar} {pct:5.1f}%{marker}")
    if (epochs - 1) % step != 0:
        pct = history[-1] * 100
        bar = _bar_chart(history[-1])
        marker = " <-- best" if history[-1] == best else ""
        print(f"  Epoch {epochs:4d}: {bar} {pct:5.1f}%{marker}")
    print()
    print(f"  Best:   {best:.3f} ({best * 100:.1f}%)")
    print(f"  Final:  {final:.3f} ({final * 100:.1f}%)")
    print(f"  Epochs: {epochs}")
    print()


def print_weight_heatmap(model, label="Weight Heatmap"):
    """Print an ASCII weight heatmap for a Perceptron or network.

    Shows signed weight values in a grid layout.

    Args:
        model: A Perceptron or TernaryNeuralNetwork instance.
        label: Optional heading label.
    """
    print()
    print("=" * 50)
    print(f"  {label}")
    print("=" * 50)
    if isinstance(model, Perceptron):
        print(f"  Bias: {_signed_char(model.bias)}")
        print(f"  Weights ({len(model.weights)}):")
        for i, w in enumerate(model.weights):
            print(f"    w[{i}] = {_signed_char(w)}")
        print()
    elif isinstance(model, TernaryNeuralNetwork):
        for li, layer in enumerate(model.layers):
            print(f"  Layer {li} ({len(layer)} neurons):")
            header = "        " + "  ".join(
                f"w{j:2d}" for j in range(len(layer[0].weights))
            )
            print(header)
            for ni, neuron in enumerate(layer):
                row = f"  N{ni}:  "
                row += "  ".join(_signed_char(w) for w in neuron.weights)
                row += f"  | bias={_signed_char(neuron.bias)}"
                print(row)
            print()
    print()


def print_accuracy_chart(history):
    """Alias for print_training_progress."""
    print_training_progress(history, label="Accuracy Chart")


def print_confusion_matrix(model, dataset, label="Confusion Matrix"):
    """Print an ASCII confusion matrix for a model on a dataset.

    Rows are true classes, columns are predicted classes. Works
    for binary classification (0 and 2) as well as ternary.

    Args:
        model: A Perceptron or TernaryNeuralNetwork.
        dataset: List of (inputs, target) tuples.
        label: Optional heading label.
    """
    classes = sorted(set(
        t[0] if isinstance(t, list) else t
        for _, t in dataset
    ))
    class_map = {c: i for i, c in enumerate(classes)}
    n = len(classes)
    matrix = [[0] * n for _ in range(n)]

    for inputs, target in dataset:
        true_val = target[0] if isinstance(target, list) else target
        if isinstance(model, Perceptron):
            pred = model.forward(inputs)
        else:
            pred_list = model.forward(inputs)
            pred = pred_list[0] if pred_list else 1
        true_idx = class_map[true_val]
        pred_idx = class_map.get(pred, 0)
        matrix[true_idx][pred_idx] += 1

    print()
    print("=" * 50)
    print(f"  {label}")
    print("=" * 50)
    header = "      " + "  ".join(f"{c:3d}" for c in classes)
    print(header)
    for ri, c_true in enumerate(classes):
        row = f"  {c_true:3d}  "
        row += "  ".join(f"{matrix[ri][ci]:3d}" for ci in range(n))
        print(row)
    print()

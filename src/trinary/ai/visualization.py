"""ASCII visualization utilities for ternary neural network components.

Provides simple text-based printing for TritTensor, Perceptron weights,
and network architecture summaries.
"""

from trinary.ai.activations import trit_to_signed
from trinary.ai.trit_tensor import TritTensor
from trinary.ai.perceptron import Perceptron
from trinary.ai.ternary_nn import TernaryNeuralNetwork


def _trit_to_char(trit):
    """Convert a ternary digit to a signed display character."""
    mapping = {0: "-1", 1: " 0", 2: "+1"}
    return mapping.get(trit, " ?")


def print_tensor(tensor, label=None):
    """Print a TritTensor as an ASCII grid.

    Args:
        tensor: A TritTensor instance.
        label: Optional label string printed before the tensor.
    """
    if label:
        print(label)
    if tensor.is_vector():
        signed = [_trit_to_char(x) for x in tensor.data]
        print("[" + " ".join(signed) + "]")
    else:
        for row in tensor.data:
            signed = [_trit_to_char(x) for x in row]
            print("[" + " ".join(signed) + "]")
    print()


def print_weights(perceptron, label=None):
    """Print a Perceptron's weights and bias as signed values.

    Args:
        perceptron: A Perceptron instance.
        label: Optional label string.
    """
    if label:
        print(label)
    signed_w = [_trit_to_char(w) for w in perceptron.weights]
    print(f"  weights: [{', '.join(signed_w)}]")
    print(f"  bias:    {_trit_to_char(perceptron.bias)}")
    print()


def print_network_summary(network):
    """Print an ASCII summary of a TernaryNeuralNetwork.

    Shows each layer: number of inputs, number of neurons, and a
    compact weight table for each neuron.

    Args:
        network: A TernaryNeuralNetwork instance.
    """
    print("=" * 50)
    print("Ternary Neural Network — Summary")
    print("=" * 50)
    print(f"  Layers: {network.num_layers}")
    print()
    for i, layer in enumerate(network.layers):
        n_inputs = len(layer[0].weights) if layer else 0
        n_neurons = len(layer)
        print(f"  Layer {i}: {n_inputs} inputs × {n_neurons} neurons")
        print("-" * 40)
        for j, neuron in enumerate(layer):
            w_str = ", ".join(_trit_to_char(w) for w in neuron.weights)
            b_str = _trit_to_char(neuron.bias)
            print(f"    N{j}: w=[{w_str}], b={b_str}")
        print()
    print("=" * 50)

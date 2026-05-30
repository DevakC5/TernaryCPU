"""TernaryNeuralNetwork — a minimal feedforward network of ternary perceptrons.

Supports a list of layers, where each layer is a list of Perceptron
instances. The forward pass propagates through layers sequentially.
"""

import json
import os

from trinary.ai.perceptron import Perceptron


class TernaryNeuralNetwork:
    """A minimal feedforward ternary neural network.

    The network is defined as a list of layers. Each layer is a list
    of Perceptron instances. The output of one layer becomes the
    input to the next.

    Args:
        layers: List of lists of Perceptron. Each inner list is one layer.

    Raises:
        ValueError: If layers is empty or any layer is empty.
    """

    def __init__(self, layers):
        if not layers:
            raise ValueError("Network must have at least one layer")
        for i, layer in enumerate(layers):
            if not layer:
                raise ValueError(f"Layer {i} is empty")
            for j, p in enumerate(layer):
                if not isinstance(p, Perceptron):
                    raise ValueError(
                        f"Layer {i}, neuron {j} is not a Perceptron"
                    )
        self.layers = layers

    @property
    def num_layers(self):
        """Return the number of layers."""
        return len(self.layers)

    @property
    def layer_sizes(self):
        """Return a list of (inputs, outputs) per layer."""
        sizes = []
        for layer in self.layers:
            if layer:
                sizes.append((len(layer[0].weights), len(layer)))
            else:
                sizes.append((0, 0))
        return sizes

    def forward(self, inputs):
        """Run the forward pass through all layers.

        Args:
            inputs: List of ternary digits (0/1/2) for the input layer.

        Returns:
            List of ternary digits (0/1/2), the output of the final layer.

        Raises:
            ValueError: If input length mismatches the first layer's
                weight count, or inputs contain invalid digits.
        """
        current = list(inputs)
        for layer in self.layers:
            outputs = []
            for neuron in layer:
                outputs.append(neuron.forward(current))
            current = outputs
        return current

    def save(self, filepath):
        """Save network weights to a JSON file.

        Args:
            filepath: Path to save the model.
        """
        data = {
            "format": "ternary_nn_v1",
            "layer_sizes": self.layer_sizes,
            "layers": [],
        }
        for layer in self.layers:
            layer_data = []
            for neuron in layer:
                layer_data.append({
                    "weights": list(neuron.weights),
                    "bias": neuron.bias,
                })
            data["layers"].append(layer_data)

        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath):
        """Load a network from a JSON file.

        Args:
            filepath: Path to the saved model.

        Returns:
            TernaryNeuralNetwork instance.
        """
        with open(filepath, "r") as f:
            data = json.load(f)

        layers = []
        for layer_data in data["layers"]:
            layer = []
            for neuron_data in layer_data:
                layer.append(Perceptron(
                    weights=list(neuron_data["weights"]),
                    bias=neuron_data["bias"],
                ))
            layers.append(layer)

        return cls(layers)

    def __repr__(self):
        return (
            f"TernaryNeuralNetwork(layers={self.num_layers}, "
            f"sizes={self.layer_sizes})"
        )

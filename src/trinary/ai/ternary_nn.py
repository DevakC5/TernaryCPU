"""TernaryNeuralNetwork — a minimal feedforward network of ternary perceptrons.

Supports a list of layers, where each layer is a list of Perceptron
instances. The forward pass propagates through layers sequentially.
"""

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

    def __repr__(self):
        return (
            f"TernaryNeuralNetwork(layers={self.num_layers}, "
            f"sizes={self.layer_sizes})"
        )

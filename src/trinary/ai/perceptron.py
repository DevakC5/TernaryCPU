"""Perceptron — a single ternary neuron for inference.

The perceptron stores ternary digit weights and a bias, then performs
a forward pass by converting to signed values, computing a weighted
sum, and applying a ternary activation function.
"""

from trinary.ai.activations import (
    trit_to_signed,
    signed_to_trit,
    ternary_step,
)


class Perceptron:
    """A single ternary perceptron.

    The perceptron holds weights as ternary digits (0/1/2) and
    computes: output = ternary_step(Σ(input_i * weight_i) + bias)

    Args:
        weights: List of ternary digits (0/1/2), one per input.
        bias: Ternary digit bias term (default 1, meaning 0 in signed).

    Raises:
        ValueError: If weights or bias contain invalid digits.
    """

    def __init__(self, weights, bias=1):
        for i, w in enumerate(weights):
            if w not in (0, 1, 2):
                raise ValueError(f"Invalid weight {w} at index {i}")
        if bias not in (0, 1, 2):
            raise ValueError(f"Invalid bias {bias}")
        self.weights = list(weights)
        self.bias = bias

    @property
    def signed_weights(self):
        """Return weights as signed values (-1, 0, +1)."""
        return [trit_to_signed(w) for w in self.weights]

    @property
    def signed_bias(self):
        """Return bias as a signed value (-1, 0, +1)."""
        return trit_to_signed(self.bias)

    def forward(self, inputs):
        """Compute the perceptron output as a ternary digit.

        Inference pipeline:
        1. Convert ternary digits to signed values
        2. Compute weighted sum: Σ(input_i × weight_i) + bias
        3. Apply ternary_step activation
        4. Return ternary digit (0, 1, or 2)

        Args:
            inputs: List of ternary digits (0/1/2).

        Returns:
            Ternary digit 0, 1, or 2.

        Raises:
            ValueError: If input length mismatches weights,
                or inputs contain invalid digits.
        """
        if len(inputs) != len(self.weights):
            raise ValueError(
                f"Expected {len(self.weights)} inputs, got {len(inputs)}"
            )
        for i, x in enumerate(inputs):
            if x not in (0, 1, 2):
                raise ValueError(f"Invalid input {x} at index {i}")
        signed_inputs = [trit_to_signed(x) for x in inputs]
        signed_w = self.signed_weights
        total = self.signed_bias
        for i in range(len(signed_inputs)):
            total += signed_inputs[i] * signed_w[i]
        return ternary_step(total)

    def predict(self, inputs):
        """Alias for forward()."""
        return self.forward(inputs)

    def __repr__(self):
        return f"Perceptron(weights={self.weights}, bias={self.bias})"

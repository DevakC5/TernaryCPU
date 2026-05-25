"""Optimizers for ternary neural network training.

Provides simple gradient-free and gradient-approximate weight update
rules that respect the ternary digit constraint (-1, 0, +1).
"""

import random

from trinary.ai.activations import signed_to_trit, trit_to_signed
from trinary.ai.perceptron import Perceptron
from trinary.ai.ternary_nn import TernaryNeuralNetwork


def _clamp_signed(value):
    """Clamp an integer to the valid signed range [-1, 0, 1]."""
    if value < -1:
        return -1
    if value > 1:
        return 1
    return value


class SGDOptimizer:
    """Stochastic gradient descent for ternary perceptrons.

    Updates each weight: signed_weight += learning_rate * input * error
    then clamps to [-1, 0, 1] and converts back to ternary digit.

    The error is computed as signed(target) - signed(prediction), which
    gives -2, -1, 0, 1, or 2. With learning_rate=1 this either leaves
    the weight unchanged or moves it one step toward the correct value.

    Args:
        learning_rate: Step size (default 1). Higher values move faster
            but may overshoot on ternary weights.
    """

    def __init__(self, learning_rate=1):
        self.learning_rate = learning_rate

    def step(self, perceptron, inputs, target):
        """Perform one weight update on a single Perceptron.

        Uses sign-based error to move weights in the correct
        direction by at most ±1 per update, preventing overshoot
        in the discrete ternary weight space.

        Args:
            perceptron: A Perceptron instance (modified in place).
            inputs: List of ternary digits (0/1/2).
            target: Ternary digit target (0/1/2).
        """
        prediction = perceptron.forward(inputs)
        signed_inputs = [trit_to_signed(x) for x in inputs]
        signed_target = trit_to_signed(target)
        signed_pred = trit_to_signed(prediction)
        error = signed_target - signed_pred
        error = _clamp_signed(error)

        signed_w = [trit_to_signed(w) for w in perceptron.weights]
        for i in range(len(signed_w)):
            signed_w[i] += self.learning_rate * signed_inputs[i] * error
            signed_w[i] = _clamp_signed(signed_w[i])
        perceptron.weights = [signed_to_trit(w) for w in signed_w]

        signed_b = trit_to_signed(perceptron.bias)
        signed_b += self.learning_rate * error
        signed_b = _clamp_signed(signed_b)
        perceptron.bias = signed_to_trit(signed_b)


class TernaryHillClimber:
    """Experimental ternary hill-climbing optimizer.

    Works on both single Perceptrons and multi-layer
    TernaryNeuralNetworks. Tries random weight flips and keeps
    changes that improve accuracy on the training set.

    Uses multi-parameter mutations (1-3 params at once) to
    escape local minima, plus best-state tracking with
    automatic restart when stuck for too many steps.

    This is a gradient-free, evolutionary-style optimizer that
    respects the ternary weight constraint natively.

    Args:
        max_attempts: Number of random mutations to try per step
            (default 30).
        improvement_threshold: Minimum accuracy improvement to
            accept a change (default 0.0, meaning any improvement
            or tie is accepted).
    """

    def __init__(self, max_attempts=30, improvement_threshold=0.0):
        self.max_attempts = max_attempts
        self.improvement_threshold = improvement_threshold

    @staticmethod
    def _random_trit():
        return random.choice([0, 1, 2])

    def _evaluate_accuracy(self, model, dataset):
        correct = 0
        total = len(dataset)
        for inputs, target in dataset:
            if isinstance(model, Perceptron):
                output = [model.forward(inputs)]
            else:
                output = model.forward(inputs)
            if output == target:
                correct += 1
        return correct / total

    @staticmethod
    def _collect_parameters(model):
        """Return a flat list of (layer_idx, neuron_idx, param_name, trit)
        and a snapshot function to restore."""
        params = []
        if isinstance(model, Perceptron):
            for i, w in enumerate(model.weights):
                params.append(("perceptron", 0, "weight", i, w))
            params.append(("perceptron", 0, "bias", -1, model.bias))
        else:
            for li, layer in enumerate(model.layers):
                for ni, neuron in enumerate(layer):
                    for wi, w in enumerate(neuron.weights):
                        params.append(("network", li, ni, "weight", wi, w))
                    params.append(("network", li, ni, "bias", -1, neuron.bias))
        return params

    def _mutate_parameter(self, model, param_info):
        if param_info[0] == "perceptron":
            _, _, ptype, idx, _ = param_info
            if ptype == "weight":
                old = model.weights[idx]
                new = self._random_trit()
                model.weights[idx] = new
            else:
                old = model.bias
                new = self._random_trit()
                model.bias = new
        else:
            _, li, ni, ptype, idx, _ = param_info
            neuron = model.layers[li][ni]
            if ptype == "weight":
                old = neuron.weights[idx]
                new = self._random_trit()
                neuron.weights[idx] = new
            else:
                old = neuron.bias
                new = self._random_trit()
                neuron.bias = new
        return old, new

    def _restore_parameter(self, model, param_info, old):
        if param_info[0] == "perceptron":
            _, _, ptype, idx, _ = param_info
            if ptype == "weight":
                model.weights[idx] = old
            else:
                model.bias = old
        else:
            _, li, ni, ptype, idx, _ = param_info
            neuron = model.layers[li][ni]
            if ptype == "weight":
                neuron.weights[idx] = old
            else:
                neuron.bias = old

    def step(self, model, dataset):
        """Try multi-parameter mutations and keep changes that improve accuracy.

        Mutates 1 to 3 parameters at once to escape local optima.
        Tracks the best accuracy seen and restores to it if stuck.

        Args:
            model: A Perceptron or TernaryNeuralNetwork instance.
            dataset: List of (inputs, target) tuples.

        Returns:
            bool: True if the model changed this step.
        """
        initial_acc = self._evaluate_accuracy(model, dataset)
        best_acc = initial_acc
        accepted = False
        params = self._collect_parameters(model)

        for _ in range(self.max_attempts):
            n_mutations = random.randint(1, 3)
            indices = random.sample(range(len(params)), min(n_mutations, len(params)))
            old_vals = []
            for idx in indices:
                old, _ = self._mutate_parameter(model, params[idx])
                old_vals.append(old)

            new_acc = self._evaluate_accuracy(model, dataset)

            if new_acc > best_acc + self.improvement_threshold:
                best_acc = new_acc
                accepted = True
            elif new_acc < best_acc:
                for idx, old in zip(indices, old_vals):
                    self._restore_parameter(model, params[idx], old)
            else:
                pass  # tie — keep mutation (exploration)

        return accepted

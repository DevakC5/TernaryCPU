"""Optimizers for ternary neural network training.

Provides SGD for single perceptrons and true backpropagation
for multi-layer TernaryNeuralNetworks, all operating within
the signed integer space {-1, 0, +1}.
"""

import random

from trinary.ai.activations import signed_to_trit, trit_to_signed, ternary_step
from trinary.ai.perceptron import Perceptron
from trinary.ai.ternary_nn import TernaryNeuralNetwork


def _clamp_signed(value):
    if value < -1:
        return -1
    if value > 1:
        return 1
    return value


class SGDOptimizer:
    """Stochastic gradient descent for a single ternary perceptron.

    Updates each weight: signed_weight += learning_rate * input * error
    then clamps to [-1, 0, +1] and converts back to ternary digit.

    Args:
        learning_rate: Step size (default 1).
    """

    def __init__(self, learning_rate=1):
        self.learning_rate = learning_rate

    def step(self, perceptron, inputs, target):
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


class BackpropOptimizer:
    """True backpropagation optimizer for multi-layer TernaryNeuralNetworks.

    Computes gradients through all hidden layers using the chain rule,
    operating entirely in the signed integer space {-1, 0, +1}.
    Uses Straight-Through Estimator (STE) for the step activation
    function — the gradient passes through unchanged.

    Args:
        learning_rate: Step size (default 1).
    """

    def __init__(self, learning_rate=1):
        self.learning_rate = learning_rate

    def _forward_with_activations(self, network, inputs):
        """Forward pass, storing each layer's signed output.

        Returns:
            list of list of int: signed activations per layer [layer0, ..., layerN].
        """
        signed_inputs = [trit_to_signed(x) for x in inputs]
        activations = [signed_inputs]
        current = list(inputs)
        for layer in network.layers:
            layer_out = []
            for neuron in layer:
                raw = 0
                for wi, w in enumerate(neuron.weights):
                    raw += trit_to_signed(w) * trit_to_signed(current[wi])
                raw += trit_to_signed(neuron.bias)
                raw = _clamp_signed(raw)
                out_trit = ternary_step(raw)
                layer_out.append(out_trit)
            current = layer_out
            activations.append([trit_to_signed(x) for x in layer_out])
        return activations

    def step(self, network, inputs, target):
        """Perform one backpropagation weight update on the network.

        Args:
            network: A TernaryNeuralNetwork instance.
            inputs: List of ternary digits (0/1/2).
            target: List of ternary digits (0/1/2), the expected output.
        """
        if isinstance(network, Perceptron):
            return SGDOptimizer(learning_rate=self.learning_rate).step(
                network, inputs, target[0] if isinstance(target, list) else target
            )

        signed_target = [trit_to_signed(t) for t in target]

        activations = self._forward_with_activations(network, inputs)

        signed_output = activations[-1]
        deltas = [None] * len(network.layers)

        deltas[-1] = [
            _clamp_signed(signed_target[i] - signed_output[i])
            for i in range(len(signed_output))
        ]

        for li in range(len(network.layers) - 2, -1, -1):
            layer = network.layers[li + 1]
            next_delta = deltas[li + 1]
            delta = []
            for ni in range(len(network.layers[li])):
                err = 0
                for nj, neuron in enumerate(layer):
                    w_signed = trit_to_signed(neuron.weights[ni])
                    err += w_signed * next_delta[nj]
                delta.append(_clamp_signed(err))
            deltas[li] = delta

        for li, layer in enumerate(network.layers):
            for ni, neuron in enumerate(layer):
                signed_w = [trit_to_signed(w) for w in neuron.weights]
                for wi in range(len(signed_w)):
                    signed_w[wi] += self.learning_rate * activations[li][wi] * deltas[li][ni]
                    signed_w[wi] = _clamp_signed(signed_w[wi])
                neuron.weights = [signed_to_trit(w) for w in signed_w]

                signed_b = trit_to_signed(neuron.bias)
                signed_b += self.learning_rate * deltas[li][ni]
                signed_b = _clamp_signed(signed_b)
                neuron.bias = signed_to_trit(signed_b)


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
                pass

        return accepted

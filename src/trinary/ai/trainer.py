"""TernaryTrainer — supervised learning for ternary neural networks.

Supports training single Perceptrons and multi-layer
TernaryNeuralNetworks with configurable optimizers, epoch
loops, accuracy tracking, and verbose output.
"""

import random

from trinary.ai.activations import signed_to_trit, trit_to_signed, ternary_step
from trinary.ai.perceptron import Perceptron
from trinary.ai.ternary_nn import TernaryNeuralNetwork
from trinary.ai.optimizers import SGDOptimizer, TernaryHillClimber
from trinary.ai.losses import classification_error
from trinary.ai.datasets import (
    AND_DATASET,
    OR_DATASET,
    XOR_DATASET,
    get_dataset,
)


def _random_ternary_weights(n):
    return [random.choice([0, 1, 2]) for _ in range(n)]


class TernaryTrainer:
    """Supervised trainer for ternary neural networks.

    Trains a Perceptron or TernaryNeuralNetwork on a dataset of
    (inputs, target) pairs using the configured optimizer.

    Args:
        model: A Perceptron or TernaryNeuralNetwork instance.
        learning_rate: Step size for SGD updates (default 1).
        max_epochs: Maximum training epochs (default 100).
        optimizer: Optional pre-configured optimizer instance.
            If None, an SGDOptimizer is created from learning_rate.
        verbose: Print progress during training (default True).

    Raises:
        TypeError: If model is not a Perceptron or TernaryNeuralNetwork.
    """

    def __init__(
        self,
        model,
        learning_rate=1,
        max_epochs=100,
        optimizer=None,
        verbose=True,
    ):
        if not isinstance(model, (Perceptron, TernaryNeuralNetwork)):
            raise TypeError(
                "Model must be a Perceptron or TernaryNeuralNetwork"
            )
        if optimizer is not None:
            self.optimizer = optimizer
        else:
            self.optimizer = SGDOptimizer(learning_rate=learning_rate)
        self.model = model
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        self.verbose = verbose
        self.history = []
        self.best_weights = None
        self.best_accuracy = 0.0

    def _save_best(self, accuracy):
        if accuracy > self.best_accuracy:
            self.best_accuracy = accuracy
            self.best_weights = self._capture_weights()

    def _capture_weights(self):
        if isinstance(self.model, Perceptron):
            return {
                "type": "perceptron",
                "weights": list(self.model.weights),
                "bias": self.model.bias,
            }
        layers = []
        for layer in self.model.layers:
            layer_data = []
            for neuron in layer:
                layer_data.append({
                    "weights": list(neuron.weights),
                    "bias": neuron.bias,
                })
            layers.append(layer_data)
        return {"type": "network", "layers": layers}

    def _restore_weights(self, snapshot):
        if snapshot["type"] == "perceptron":
            self.model.weights = list(snapshot["weights"])
            self.model.bias = snapshot["bias"]
        else:
            for li, layer in enumerate(snapshot["layers"]):
                for ni, neuron_data in enumerate(layer):
                    self.model.layers[li][ni].weights = list(
                        neuron_data["weights"]
                    )
                    self.model.layers[li][ni].bias = neuron_data["bias"]

    def _predict_single(self, inputs):
        if isinstance(self.model, Perceptron):
            return [self.model.forward(inputs)]
        return self.model.forward(inputs)

    def accuracy(self, dataset):
        """Compute classification accuracy on a dataset.

        Args:
            dataset: List of (inputs, target) tuples.

        Returns:
            Float accuracy (0.0 to 1.0).
        """
        correct = 0
        for inputs, target in dataset:
            output = self._predict_single(inputs)
            if output == target:
                correct += 1
        return correct / len(dataset)

    def _train_epoch_sgd(self, dataset):
        shuffled = list(dataset)
        random.shuffle(shuffled)
        if isinstance(self.model, Perceptron):
            batch_w = [0] * len(self.model.weights)
            batch_b = 0
            n = len(shuffled)
            for inputs, target in shuffled:
                prediction = self.model.forward(inputs)
                signed_in = [trit_to_signed(x) for x in inputs]
                signed_t = trit_to_signed(target[0])
                signed_p = trit_to_signed(prediction)
                err = max(-1, min(1, signed_t - signed_p))
                for i in range(len(batch_w)):
                    batch_w[i] += signed_in[i] * err
                batch_b += err
            for i in range(len(batch_w)):
                if batch_w[i] > 0:
                    delta = 1
                elif batch_w[i] < 0:
                    delta = -1
                else:
                    delta = 0
                signed_w = trit_to_signed(self.model.weights[i])
                signed_w += delta
                signed_w = max(-1, min(1, signed_w))
                self.model.weights[i] = signed_to_trit(signed_w)
            if batch_b > 0:
                delta = 1
            elif batch_b < 0:
                delta = -1
            else:
                delta = 0
            signed_b = trit_to_signed(self.model.bias)
            signed_b += delta
            signed_b = max(-1, min(1, signed_b))
            self.model.bias = signed_to_trit(signed_b)
        else:
            for layer in self.model.layers:
                for neuron in layer:
                    for inputs, target in shuffled:
                        self.optimizer.step(neuron, inputs, target[0])

    def _train_epoch_hillclimb(self, dataset):
        if isinstance(self.optimizer, TernaryHillClimber):
            self.optimizer.step(self.model, dataset)

    def train(self, dataset, epochs=None):
        """Train the model on a dataset.

        Args:
            dataset: List of (inputs, target) tuples.
            epochs: Number of epochs (defaults to max_epochs).

        Returns:
            self, for chaining.
        """
        if epochs is None:
            epochs = self.max_epochs
        for epoch in range(epochs):
            if isinstance(self.optimizer, TernaryHillClimber):
                self._train_epoch_hillclimb(dataset)
            else:
                self._train_epoch_sgd(dataset)
            acc = self.accuracy(dataset)
            self._save_best(acc)
            self.history.append(acc)
            if self.verbose and (epoch % max(1, epochs // 10) == 0 or epoch == epochs - 1):
                print(
                    f"  Epoch {epoch + 1:5d}/{epochs} — "
                    f"accuracy: {acc:.3f}"
                )
            if acc >= 1.0:
                if self.verbose:
                    print(f"  Early stop at epoch {epoch + 1} — 100% accuracy")
                break
        return self

    def evaluate(self, dataset):
        """Evaluate the model and return accuracy and loss.

        Args:
            dataset: List of (inputs, target) tuples.

        Returns:
            Tuple of (accuracy, mean_classification_error).
        """
        acc = self.accuracy(dataset)
        total_err = 0.0
        for inputs, target in dataset:
            output = self._predict_single(inputs)
            total_err += classification_error(output, target)
        mean_err = total_err / len(dataset)
        return acc, mean_err

    def predict(self, inputs):
        """Predict output for a single set of inputs.

        Args:
            inputs: List of ternary digits (0/1/2).

        Returns:
            List of ternary digits (0/1/2).
        """
        return self._predict_single(inputs)

    def fit_xor(self, epochs=None):
        """Convenience: train on the XOR dataset.

        For single Perceptrons this will demonstrate the classic
        XOR limitation. For multi-layer networks it should converge.

        Args:
            epochs: Number of epochs (defaults to max_epochs).

        Returns:
            self.
        """
        return self.train(XOR_DATASET, epochs=epochs)

    def fit_and(self, epochs=None):
        """Convenience: train on the AND dataset.

        Args:
            epochs: Number of epochs (defaults to max_epochs).

        Returns:
            self.
        """
        return self.train(AND_DATASET, epochs=epochs)

    def fit_or(self, epochs=None):
        """Convenience: train on the OR dataset.

        Args:
            epochs: Number of epochs (defaults to max_epochs).

        Returns:
            self.
        """
        return self.train(OR_DATASET, epochs=epochs)

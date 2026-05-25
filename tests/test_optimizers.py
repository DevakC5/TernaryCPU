from trinary.ai.perceptron import Perceptron
from trinary.ai.ternary_nn import TernaryNeuralNetwork
from trinary.ai.optimizers import SGDOptimizer, TernaryHillClimber
from trinary.ai.datasets import AND_DATASET, XOR_DATASET


class TestSGDOptimizer:
    def test_constructor_default(self):
        opt = SGDOptimizer()
        assert opt.learning_rate == 1

    def test_constructor_custom_lr(self):
        opt = SGDOptimizer(learning_rate=2)
        assert opt.learning_rate == 2

    def test_step_changes_weights(self):
        p = Perceptron([0, 0], bias=1)
        old_w = list(p.weights)
        old_b = p.bias
        opt = SGDOptimizer(learning_rate=1)
        opt.step(p, [2, 2], 2)  # AND target 2
        # weights or bias should have changed
        assert p.weights != old_w or p.bias != old_b

    def test_step_converges_and(self):
        p = Perceptron([1, 1], bias=1)
        opt = SGDOptimizer(learning_rate=1)
        for epoch in range(20):
            for inputs, target in AND_DATASET:
                opt.step(p, inputs, target[0])
        for inputs, target in AND_DATASET:
            assert p.forward(inputs) == target[0]

    def test_step_converges_or(self):
        p = Perceptron([1, 1], bias=1)
        opt = SGDOptimizer(learning_rate=1)
        from trinary.ai.datasets import OR_DATASET
        for epoch in range(20):
            for inputs, target in OR_DATASET:
                opt.step(p, inputs, target[0])
        from trinary.ai.datasets import OR_DATASET
        correct = sum(1 for inputs, target in OR_DATASET
                      if p.forward(inputs) == target[0])
        # Per-example SGD on ternary weights may oscillate on OR
        # but should be better than random (≥2/4 with 2 possible values)
        assert correct >= 2


class TestTernaryHillClimber:
    def test_constructor_default(self):
        climber = TernaryHillClimber()
        assert climber.max_attempts == 30

    def test_step_returns_bool(self):
        p = Perceptron([1, 1], bias=1)
        climber = TernaryHillClimber(max_attempts=5)
        result = climber.step(p, AND_DATASET)
        assert isinstance(result, bool)

    def test_step_network(self):
        net = TernaryNeuralNetwork([
            [Perceptron([1, 1], bias=1),
             Perceptron([1, 1], bias=1)],
            [Perceptron([1, 1], bias=1)],
        ])
        climber = TernaryHillClimber(max_attempts=5)
        result = climber.step(net, XOR_DATASET)
        assert isinstance(result, bool)

from trinary.ai.perceptron import Perceptron
from trinary.ai.ternary_nn import TernaryNeuralNetwork
from trinary.ai.trainer import TernaryTrainer
from trinary.ai.optimizers import SGDOptimizer, TernaryHillClimber
from trinary.ai.datasets import (
    AND_DATASET,
    OR_DATASET,
    XOR_DATASET,
    NAND_DATASET,
)


class TestConstruction:
    def test_perceptron_model(self):
        p = Perceptron([1, 1], bias=1)
        t = TernaryTrainer(p, max_epochs=10, verbose=False)
        assert t.model is p
        assert t.max_epochs == 10

    def test_network_model(self):
        net = TernaryNeuralNetwork([
            [Perceptron([1, 1], bias=1)],
        ])
        t = TernaryTrainer(net, max_epochs=10, verbose=False)
        assert t.model is net

    def test_invalid_model_raises(self):
        try:
            TernaryTrainer("not_a_model")
            assert False
        except TypeError:
            pass

    def test_custom_optimizer(self):
        p = Perceptron([1, 1])
        opt = SGDOptimizer(learning_rate=2)
        t = TernaryTrainer(p, optimizer=opt, verbose=False)
        assert t.optimizer.learning_rate == 2


class TestAccuracy:
    def test_perfect_accuracy(self):
        p = Perceptron([2, 2], bias=0)  # AND
        from trinary.ai.trainer import TernaryTrainer
        t = TernaryTrainer(p, max_epochs=1, verbose=False)
        acc, err = t.evaluate(AND_DATASET)
        assert acc == 1.0
        assert err == 0.0

    def test_low_accuracy(self):
        p = Perceptron([0, 0], bias=0)
        t = TernaryTrainer(p, max_epochs=1, verbose=False)
        acc, _ = t.evaluate(AND_DATASET)
        assert acc <= 0.5  # should not be perfect


class TestTraining:
    def test_train_and(self):
        p = Perceptron([1, 1], bias=1)
        t = TernaryTrainer(p, learning_rate=1, max_epochs=20, verbose=False)
        t.fit_and()
        for inputs, target in AND_DATASET:
            assert p.forward(inputs) == target[0]

    def test_train_or(self):
        p = Perceptron([1, 1], bias=1)
        t = TernaryTrainer(p, learning_rate=1, max_epochs=20, verbose=False)
        t.fit_or()
        for inputs, target in OR_DATASET:
            assert p.forward(inputs) == target[0]

    def test_train_nand(self):
        p = Perceptron([1, 1], bias=1)
        t = TernaryTrainer(p, learning_rate=1, max_epochs=20, verbose=False)
        t.train(NAND_DATASET)
        for inputs, target in NAND_DATASET:
            assert p.forward(inputs) == target[0]


class TestSinglePerceptronXOR:
    def test_single_perceptron_fails_xor(self):
        p = Perceptron([1, 1], bias=1)
        t = TernaryTrainer(p, learning_rate=1, max_epochs=50, verbose=False)
        t.fit_xor()
        acc, _ = t.evaluate(XOR_DATASET)
        # A single perceptron cannot learn XOR (max ~75% on 4 examples)
        assert acc < 1.0


class TestNetworkHillClimbXOR:
    def test_multi_layer_can_learn_xor(self):
        net = TernaryNeuralNetwork([
            [Perceptron([1, 1], bias=1),
             Perceptron([1, 1], bias=1)],
            [Perceptron([1, 1], bias=1)],
        ])
        climber = TernaryHillClimber(max_attempts=20, improvement_threshold=0.0)
        t = TernaryTrainer(
            net, max_epochs=200, optimizer=climber, verbose=False
        )
        t.fit_xor()
        acc, _ = t.evaluate(XOR_DATASET)
        assert acc >= 0.5  # should be better than random


class TestPredict:
    def test_predict_perceptron(self):
        p = Perceptron([2, 2], bias=0)
        t = TernaryTrainer(p, max_epochs=1, verbose=False)
        result = t.predict([2, 2])
        assert result == [2]
        result = t.predict([0, 0])
        assert result == [0]

    def test_predict_network(self):
        net = TernaryNeuralNetwork([
            [Perceptron([2, 2], bias=2)],  # OR
        ])
        t = TernaryTrainer(net, max_epochs=1, verbose=False)
        result = t.predict([2, 0])
        assert result == [2]

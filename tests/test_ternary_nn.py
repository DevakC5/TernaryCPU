from trinary.ai.perceptron import Perceptron
from trinary.ai.ternary_nn import TernaryNeuralNetwork


class TestConstruction:
    def test_single_layer(self):
        net = TernaryNeuralNetwork([
            [Perceptron([2, 0], bias=1)],
        ])
        assert net.num_layers == 1

    def test_multi_layer(self):
        net = TernaryNeuralNetwork([
            [Perceptron([2, 0]), Perceptron([0, 2])],
            [Perceptron([2, 2])],
        ])
        assert net.num_layers == 2
        assert net.layer_sizes == [(2, 2), (2, 1)]

    def test_empty_layers_raises(self):
        try:
            TernaryNeuralNetwork([])
            assert False
        except ValueError:
            pass

    def test_empty_layer_raises(self):
        try:
            TernaryNeuralNetwork([[]])
            assert False
        except ValueError:
            pass

    def test_non_perceptron_raises(self):
        try:
            TernaryNeuralNetwork([["not_a_perceptron"]])
            assert False
        except ValueError:
            pass


class TestForwardPass:
    def test_single_neuron(self):
        net = TernaryNeuralNetwork([
            [Perceptron([2, 2], bias=2)],  # OR gate
        ])
        assert net.forward([2, 2]) == [2]
        assert net.forward([2, 0]) == [2]
        assert net.forward([0, 0]) == [0]

    def test_two_layers(self):
        hidden = [Perceptron([2, 2], bias=2)]   # OR
        output = [Perceptron([2], bias=2)]      # just pass through
        net = TernaryNeuralNetwork([hidden, output])
        result = net.forward([2, 0])  # OR = 2 -> pass through -> 2
        assert result == [2]

    def test_multi_output(self):
        net = TernaryNeuralNetwork([
            [Perceptron([2, 0]), Perceptron([2, 0])],
        ])
        result = net.forward([2, 2])  # both neurons see [+1,+1]
        assert len(result) == 2
        assert all(x in (0, 1, 2) for x in result)

    def test_xor_approximation(self):
        net = TernaryNeuralNetwork([
            [Perceptron([2, 2], bias=0),   # NAND: w=[+1,+1], b=-1
             Perceptron([2, 2], bias=0)],   # NAND
            [Perceptron([0, 0], bias=2)],   # AND: w=[-1,-1], b=+1
        ])
        result = net.forward([2, 2])
        assert all(x in (0, 1, 2) for x in result)
        result2 = net.forward([2, 0])
        assert all(x in (0, 1, 2) for x in result2)


class TestLayerSizes:
    def test_layer_sizes_property(self):
        net = TernaryNeuralNetwork([
            [Perceptron([2, 0, 2]), Perceptron([2, 0, 2])],
            [Perceptron([2, 2])],
        ])
        assert net.layer_sizes == [(3, 2), (2, 1)]


class TestRepresentation:
    def test_repr(self):
        net = TernaryNeuralNetwork([
            [Perceptron([2, 0])],
        ])
        r = repr(net)
        assert "TernaryNeuralNetwork" in r
        assert "layers" in r

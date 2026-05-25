from trinary.ai.perceptron import Perceptron


class TestConstruction:
    def test_valid_weights(self):
        p = Perceptron([0, 1, 2])
        assert p.weights == [0, 1, 2]

    def test_default_bias(self):
        p = Perceptron([0, 1])
        assert p.bias == 1

    def test_custom_bias(self):
        p = Perceptron([0, 1], bias=2)
        assert p.bias == 2

    def test_invalid_weight_raises(self):
        try:
            Perceptron([0, 3])
            assert False
        except ValueError:
            pass

    def test_invalid_bias_raises(self):
        try:
            Perceptron([0, 1], bias=3)
            assert False
        except ValueError:
            pass


class TestInference:
    def test_and_gate(self):
        p = Perceptron([2, 2], bias=0)   # w=[+1,+1], b=-1
        # Input: [+1,+1] -> sum = 1+1-1 = 1 -> positive -> 2
        assert p.forward([2, 2]) == 2
        # Input: [+1,-1] -> sum = 1-1-1 = -1 -> negative -> 0
        assert p.forward([2, 0]) == 0
        # Input: [-1,+1] -> sum = -1+1-1 = -1 -> negative -> 0
        assert p.forward([0, 2]) == 0
        # Input: [-1,-1] -> sum = -1-1-1 = -3 -> negative -> 0
        assert p.forward([0, 0]) == 0

    def test_or_gate(self):
        p = Perceptron([2, 2], bias=2)  # w=[+1,+1], b=+1
        # (+1)+(+1)+(+1) = +3 -> 2
        assert p.forward([2, 2]) == 2
        # (+1)+(-1)+(+1) = +1 -> 2
        assert p.forward([2, 0]) == 2
        # (-1)+(+1)+(+1) = +1 -> 2
        assert p.forward([0, 2]) == 2
        # (-1)+(-1)+(+1) = -1 -> 0
        assert p.forward([0, 0]) == 0

    def test_predict_alias(self):
        p = Perceptron([2], bias=1)
        assert p.predict([2]) == p.forward([2])

    def test_input_count_mismatch_raises(self):
        p = Perceptron([0, 1, 2])
        try:
            p.forward([0, 1])
            assert False
        except ValueError:
            pass

    def test_invalid_input_raises(self):
        p = Perceptron([0, 1])
        try:
            p.forward([0, 3])
            assert False
        except ValueError:
            pass


class TestSignedProperties:
    def test_signed_weights(self):
        p = Perceptron([0, 1, 2])
        assert p.signed_weights == [-1, 0, 1]

    def test_signed_bias(self):
        p = Perceptron([0, 1], bias=2)
        assert p.signed_bias == 1
        p2 = Perceptron([0, 1], bias=0)
        assert p2.signed_bias == -1


class TestRepresentation:
    def test_repr(self):
        p = Perceptron([0, 2], bias=1)
        r = repr(p)
        assert "Perceptron" in r
        assert "weights" in r
        assert "bias" in r

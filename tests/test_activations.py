from trinary.ai.activations import (
    trit_to_signed,
    signed_to_trit,
    ternary_step,
    ternary_sign,
    ternary_relu,
)


class TestTritToSigned:
    def test_0_returns_neg1(self):
        assert trit_to_signed(0) == -1

    def test_1_returns_0(self):
        assert trit_to_signed(1) == 0

    def test_2_returns_1(self):
        assert trit_to_signed(2) == 1

    def test_invalid_raises(self):
        try:
            trit_to_signed(3)
            assert False
        except ValueError:
            pass
        try:
            trit_to_signed(-1)
            assert False
        except ValueError:
            pass


class TestSignedToTrit:
    def test_neg1_returns_0(self):
        assert signed_to_trit(-1) == 0

    def test_0_returns_1(self):
        assert signed_to_trit(0) == 1

    def test_1_returns_2(self):
        assert signed_to_trit(1) == 2

    def test_invalid_raises(self):
        try:
            signed_to_trit(2)
            assert False
        except ValueError:
            pass
        try:
            signed_to_trit(-2)
            assert False
        except ValueError:
            pass


class TestTernaryStep:
    def test_negative_returns_0(self):
        assert ternary_step(-5) == 0
        assert ternary_step(-1) == 0

    def test_zero_returns_1(self):
        assert ternary_step(0) == 1

    def test_positive_returns_2(self):
        assert ternary_step(1) == 2
        assert ternary_step(100) == 2


class TestTernarySign:
    def test_same_as_step(self):
        assert ternary_sign(-3) == ternary_step(-3)
        assert ternary_sign(0) == ternary_step(0)
        assert ternary_sign(7) == ternary_step(7)


class TestTernaryReLU:
    def test_negative_returns_1(self):
        assert ternary_relu(-5) == 1
        assert ternary_relu(-1) == 1

    def test_zero_returns_1(self):
        assert ternary_relu(0) == 1

    def test_positive_returns_2(self):
        assert ternary_relu(1) == 2
        assert ternary_relu(100) == 2


class TestRoundTrip:
    def test_all_digits_round_trip(self):
        for d in (0, 1, 2):
            assert signed_to_trit(trit_to_signed(d)) == d

    def test_all_signed_round_trip(self):
        for s in (-1, 0, 1):
            assert trit_to_signed(signed_to_trit(s)) == s

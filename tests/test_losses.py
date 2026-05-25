from trinary.ai.losses import (
    ternary_mse,
    ternary_absolute_error,
    classification_error,
)


class TestTernaryMSE:
    def test_perfect_match_single(self):
        assert ternary_mse(2, 2) == 0.0

    def test_perfect_match_list(self):
        assert ternary_mse([2, 1, 0], [2, 1, 0]) == 0.0

    def test_max_error_single(self):
        # 2(+1) vs 0(-1): diff = 2, squared = 4
        assert ternary_mse(2, 0) == 4.0

    def test_half_error_list(self):
        # [2(+1),0(-1)] vs [0(-1),2(+1)]: (2^2 + 2^2)/2 = 4
        assert ternary_mse([2, 0], [0, 2]) == 4.0

    def test_length_mismatch_raises(self):
        try:
            ternary_mse([0, 1], [0])
            assert False
        except ValueError:
            pass


class TestTernaryAbsoluteError:
    def test_perfect_match_single(self):
        assert ternary_absolute_error(2, 2) == 0.0

    def test_perfect_match_list(self):
        assert ternary_absolute_error([0, 1, 2], [0, 1, 2]) == 0.0

    def test_max_error_single(self):
        assert ternary_absolute_error(2, 0) == 2.0

    def test_length_mismatch_raises(self):
        try:
            ternary_absolute_error([0, 1], [0])
            assert False
        except ValueError:
            pass


class TestClassificationError:
    def test_correct_single(self):
        assert classification_error(2, 2) == 0.0

    def test_incorrect_single(self):
        assert classification_error(2, 0) == 1.0

    def test_half_correct_list(self):
        err = classification_error([2, 0], [2, 2])
        assert err == 0.5

    def test_all_correct_list(self):
        assert classification_error([2, 0, 1], [2, 0, 1]) == 0.0

    def test_length_mismatch_raises(self):
        try:
            classification_error([0, 1], [0])
            assert False
        except ValueError:
            pass

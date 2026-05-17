from trinary.arithmetic import add_ternary, subtract_ternary, multiply_ternary, divide_ternary


class TestAdd:
    def test_simple(self):
        assert add_ternary("1", "2") == "10"

    def test_with_carry(self):
        assert add_ternary("2", "2") == "11"

    def test_negative(self):
        assert add_ternary("-1", "1") == "0"


class TestSubtract:
    def test_positive_result(self):
        assert subtract_ternary("10", "1") == "2"

    def test_negative_result(self):
        assert subtract_ternary("1", "10") == "-2"

    def test_zero(self):
        assert subtract_ternary("10", "10") == "0"


class TestMultiply:
    def test_simple(self):
        assert multiply_ternary("2", "2") == "11"

    def test_negative(self):
        assert multiply_ternary("-2", "2") == "-11"


class TestDivide:
    def test_exact(self):
        assert divide_ternary("10", "2") == "1"

    def test_floor(self):
        assert divide_ternary("10", "2") == "1"

    def test_by_zero(self):
        try:
            divide_ternary("1", "0")
            assert False
        except ValueError:
            pass

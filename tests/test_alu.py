from trinary.alu import alu


class TestALUAdd:
    def test_add(self):
        result, _ = alu("ADD", "102", "21")
        assert result == "200"

    def test_add_with_negative(self):
        result, _ = alu("ADD", "10", "-1")
        assert result == "2"


class TestALUSub:
    def test_sub(self):
        result, _ = alu("SUB", "102", "21")
        assert result == "11"

    def test_sub_negative_result(self):
        result, _ = alu("SUB", "1", "10")
        assert result == "-2"


class TestALUMul:
    def test_mul(self):
        result, _ = alu("MUL", "2", "2")
        assert result == "11"

    def test_mul_by_zero(self):
        result, _ = alu("MUL", "102", "0")
        assert result == "0"


class TestALUDiv:
    def test_div(self):
        result, _ = alu("DIV", "10", "2")
        assert result == "1"

    def test_div_by_zero(self):
        try:
            alu("DIV", "1", "0")
            assert False
        except ValueError:
            pass


class TestALUAnd:
    def test_and(self):
        result, _ = alu("AND", "102", "21")
        assert result == "001"

    def test_and_zeros(self):
        result, _ = alu("AND", "000", "111")
        assert result == "000"


class TestALUOr:
    def test_or(self):
        result, _ = alu("OR", "102", "21")
        assert result == "122"


class TestALUNot:
    def test_not(self):
        result, _ = alu("NOT", "102")
        assert result == "120"


class TestALUCmp:
    def test_eq(self):
        result, _ = alu("CMP", "10", "10")
        assert result == "EQ"

    def test_gt(self):
        result, _ = alu("CMP", "10", "1")
        assert result == "GT"

    def test_lt(self):
        result, _ = alu("CMP", "1", "10")
        assert result == "LT"

    def test_negative_lt(self):
        result, _ = alu("CMP", "-10", "1")
        assert result == "LT"

    def test_negative_eq(self):
        result, _ = alu("CMP", "-10", "-10")
        assert result == "EQ"

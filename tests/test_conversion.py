from trinary.conversion import (
    Trit, binary_to_decimal, decimal_to_ternary, ternary_to_decimal,
    decimal_to_binary, ternary_to_binary, validate_ternary,
)


class TestTrit:
    def test_valid_values(self):
        for v in (0, 1, 2):
            assert Trit(v).value == v

    def test_invalid_values(self):
        for v in (-1, 3, "0"):
            try:
                Trit(v)
                assert False, f"should raise for {v}"
            except ValueError:
                pass


class TestDecimalToTernary:
    def test_zero(self):
        assert decimal_to_ternary(0) == "0"

    def test_positive(self):
        assert decimal_to_ternary(1) == "1"
        assert decimal_to_ternary(3) == "10"
        assert decimal_to_ternary(11) == "102"

    def test_negative(self):
        assert decimal_to_ternary(-1) == "-1"
        assert decimal_to_ternary(-3) == "-10"
        assert decimal_to_ternary(-11) == "-102"


class TestTernaryToDecimal:
    def test_zero(self):
        assert ternary_to_decimal("0") == 0

    def test_positive(self):
        assert ternary_to_decimal("1") == 1
        assert ternary_to_decimal("10") == 3
        assert ternary_to_decimal("102") == 11

    def test_negative(self):
        assert ternary_to_decimal("-1") == -1
        assert ternary_to_decimal("-10") == -3
        assert ternary_to_decimal("-102") == -11


class TestRoundtrip:
    def test_positive(self):
        for d in range(0, 100):
            assert ternary_to_decimal(decimal_to_ternary(d)) == d

    def test_negative(self):
        for d in range(-99, 0):
            assert ternary_to_decimal(decimal_to_ternary(d)) == d


class TestValidateTernary:
    def test_valid(self):
        assert validate_ternary("0")
        assert validate_ternary("102")
        assert validate_ternary("-1")
        assert validate_ternary("-102")

    def test_invalid(self):
        for s in ("", "3", "-", "1-0", "abc"):
            try:
                validate_ternary(s)
                assert False, f"should raise for {s!r}"
            except ValueError:
                pass


class TestBinaryConverters:
    def test_binary_to_decimal(self):
        assert binary_to_decimal("0") == 0
        assert binary_to_decimal("1010") == 10
        assert binary_to_decimal("1111") == 15

    def test_decimal_to_binary(self):
        assert decimal_to_binary(0) == "0"
        assert decimal_to_binary(10) == "1010"
        assert decimal_to_binary(15) == "1111"

    def test_ternary_to_binary(self):
        assert ternary_to_binary("0") == "0"
        assert ternary_to_binary("10") == "11"

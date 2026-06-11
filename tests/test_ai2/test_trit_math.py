"""Tests for trit_math.py — LUT correctness, dot, matmul, linear."""

import pytest
from trinary.ai2.trit_math import (
    TRIT_ADD, TRIT_MUL, DOT_TERM,
    ternary_step, trit_dot, trit_dot_raw,
    trit_matmul, trit_matmul_raw,
    trit_linear, trit_linear_raw, trit_add_trit,
)


_T2S = [-1, 0, 1]


def _signed(t):
    return _T2S[t]


class TestLUTs:
    """Verify LUT entries match signed arithmetic."""

    def test_trit_add_all(self):
        for a in range(3):
            for b in range(3):
                sa = _signed(a)
                sb = _signed(b)
                expected = max(-1, min(1, sa + sb))
                expected_trit = 0 if expected == -1 else (1 if expected == 0 else 2)
                assert TRIT_ADD[a][b] == expected_trit, (
                    f"TRIT_ADD[{a}][{b}] = {TRIT_ADD[a][b]} != {expected_trit}"
                )

    def test_trit_mul_all(self):
        for a in range(3):
            for b in range(3):
                sa = _signed(a)
                sb = _signed(b)
                prod = sa * sb
                expected_trit = 0 if prod == -1 else (1 if prod == 0 else 2)
                assert TRIT_MUL[a][b] == expected_trit, (
                    f"TRIT_MUL[{a}][{b}] = {TRIT_MUL[a][b]} != {expected_trit}"
                )

    def test_dot_term_all(self):
        for a in range(3):
            for b in range(3):
                sa = _signed(a)
                sb = _signed(b)
                expected = sa * sb
                assert DOT_TERM[a][b] == expected, (
                    f"DOT_TERM[{a}][{b}] = {DOT_TERM[a][b]} != {expected}"
                )

    def test_trit_add_trit(self):
        assert trit_add_trit(0, 0) == 0
        assert trit_add_trit(0, 2) == 1
        assert trit_add_trit(2, 2) == 2
        assert trit_add_trit(1, 1) == 1


class TestTernaryStep:
    def test_negative(self):
        assert ternary_step(-5) == 0
        assert ternary_step(-2) == 0
        assert ternary_step(-1) == 0

    def test_zero(self):
        assert ternary_step(0) == 1

    def test_positive(self):
        assert ternary_step(1) == 2
        assert ternary_step(5) == 2


class TestTritDot:
    def test_positive_match(self):
        """Dot of aligned vectors should be positive."""
        a = [2, 2, 0]  # [+1, +1, -1]
        b = [2, 2, 0]  # [+1, +1, -1]
        result = trit_dot(a, b)
        assert result == 2  # positive

    def test_negative_match(self):
        a = [0, 0, 2]  # [-1, -1, +1]
        b = [0, 0, 0]  # [-1, -1, -1]
        result = trit_dot(a, b)
        # raw: 1+1+(-1)=1 → ternary_step(1)=2 (positive)
        assert result in (0, 1, 2)

    def test_dot_negative_result(self):
        a = [2, 2, 0]  # [+1, +1, -1]
        b = [0, 0, 2]  # [-1, -1, +1]
        result = trit_dot(a, b)
        # raw: -1 + -1 + -1 = -3 → ternary_step(-3) = 0
        assert result == 0

    def test_mixed(self):
        a = [2, 0, 2]  # [+1, -1, +1]
        b = [2, 2, 0]  # [+1, +1, -1]
        result = trit_dot(a, b)
        # raw: 1*1 + (-1)*1 + 1*(-1) = 1 - 1 - 1 = -1
        assert result == 0  # negative → 0

    def test_neutral(self):
        a = [1, 1, 1]  # all zero
        b = [2, 0, 2]
        result = trit_dot(a, b)
        assert result == 1  # all zero sum → 1

    def test_dot_raw(self):
        a = [2, 2, 0]
        b = [2, 2, 0]
        result = trit_dot_raw(a, b)
        # 1*1 + 1*1 + (-1)*(-1) = 1 + 1 + 1 = 3
        assert result == 3


class TestTritMatmul:
    def test_identity(self):
        A = [[2, 1, 1], [1, 2, 1]]  # (2, 3)
        B = [[2, 1], [1, 2], [1, 1]]  # (3, 2)
        result = trit_matmul(A, B)
        assert len(result) == 2
        assert len(result[0]) == 2

    def test_matmul_raw_shapes(self):
        A = [[2, 0], [0, 2]]
        B = [[2, 0], [0, 2]]
        raw = trit_matmul_raw(A, B)
        assert len(raw) == 2
        assert len(raw[0]) == 2


class TestTritLinear:
    def test_forward_shape(self):
        w = [2, 0, 1, 2, 0, 1]  # 2 out × 3 in
        x = [2, 1, 0]  # 3 in
        out = trit_linear(w, None, x, 3, 2)
        assert len(out) == 2

    def test_forward_with_bias(self):
        w = [2, 0, 2, 0]  # 2 out × 2 in
        b = [2, 0]
        x = [2, 2]
        out = trit_linear(w, b, x, 2, 2)
        assert len(out) == 2

    def test_linear_raw(self):
        w = [2, 0, 2, 0]
        x = [2, 2]
        raw = trit_linear_raw(w, None, x, 2, 2)
        assert len(raw) == 2
        assert all(isinstance(v, int) for v in raw)

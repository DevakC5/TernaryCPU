"""
Tests for the native C backend.

Verifies that Python and C implementations produce identical results
across a range of inputs including edge cases.
"""

import pytest

from trinary.native_backend import (
    NATIVE_AVAILABLE,
    native_add,
    native_sub,
    native_mul,
    native_div,
    native_full_adder,
)
from trinary.conversion import ternary_to_decimal, decimal_to_ternary
from trinary.arithmetic import add_ternary, subtract_ternary, multiply_ternary, divide_ternary
from trinary.adder import full_adder as py_full_adder


pytestmark = pytest.mark.skipif(
    not NATIVE_AVAILABLE,
    reason="Native backend not available. Run: cd src/trinary/native && make",
)


# ── ADD ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("a,b,expected", [
    (0, 0, 0),
    (1, 2, 3),
    (-1, 1, 0),
    (100, 200, 300),
    (-5, -7, -12),
    (0, 42, 42),
    (999999, 1, 1000000),
])
def test_native_add(a, b, expected):
    assert native_add(a, b) == expected


# ── SUB ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("a,b,expected", [
    (0, 0, 0),
    (5, 3, 2),
    (3, 5, -2),
    (-5, -3, -2),
    (100, 100, 0),
    (0, 1, -1),
])
def test_native_sub(a, b, expected):
    assert native_sub(a, b) == expected


# ── MUL ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("a,b,expected", [
    (0, 100, 0),
    (1, 1, 1),
    (7, 8, 56),
    (-3, 4, -12),
    (-3, -4, 12),
    (1000, 0, 0),
])
def test_native_mul(a, b, expected):
    assert native_mul(a, b) == expected


# ── DIV ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("a,b,expected", [
    (0, 1, 0),
    (10, 3, 3),
    (7, 2, 3),
    (-10, 3, -3),
    (100, 25, 4),
])
def test_native_div(a, b, expected):
    assert native_div(a, b) == expected


def test_native_div_by_zero():
    result = native_div(10, 0)
    import ctypes
    assert result == ctypes.c_int(-2147483648).value  # INT_MIN sentinel


# ── FULL ADDER ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("a,b,cin,expected_sum,expected_cout", [
    (0, 0, 0, 0, 0),
    (0, 0, 1, 1, 0),
    (0, 1, 0, 1, 0),
    (0, 2, 0, 2, 0),
    (1, 1, 1, 0, 1),
    (2, 2, 2, 0, 2),
    (2, 2, 1, 2, 1),
    (1, 2, 2, 2, 1),
    (0, 0, 2, 2, 0),
    (2, 2, 0, 1, 1),
])
def test_native_full_adder(a, b, cin, expected_sum, expected_cout):
    s, co = native_full_adder(a, b, cin)
    assert s == expected_sum
    assert co == expected_cout


# ── CROSS-VALIDATION WITH PYTHON ────────────────────────────────────────

def test_native_matches_python_add():
    a_str, b_str = "102", "21"
    dec_a = ternary_to_decimal(a_str)
    dec_b = ternary_to_decimal(b_str)
    native_result = decimal_to_ternary(native_add(dec_a, dec_b))
    py_result = add_ternary(a_str, b_str)
    assert native_result == py_result


def test_native_matches_python_sub():
    a_str, b_str = "21", "102"
    dec_a = ternary_to_decimal(a_str)
    dec_b = ternary_to_decimal(b_str)
    native_result = decimal_to_ternary(native_sub(dec_a, dec_b))
    py_result = subtract_ternary(a_str, b_str)
    assert native_result == py_result


def test_native_matches_python_mul():
    a_str, b_str = "12", "21"
    dec_a = ternary_to_decimal(a_str)
    dec_b = ternary_to_decimal(b_str)
    native_result = decimal_to_ternary(native_mul(dec_a, dec_b))
    py_result = multiply_ternary(a_str, b_str)
    assert native_result == py_result


def test_native_matches_python_div():
    a_str, b_str = "102", "21"
    dec_a = ternary_to_decimal(a_str)
    dec_b = ternary_to_decimal(b_str)
    native_result = decimal_to_ternary(native_div(dec_a, dec_b))
    py_result = divide_ternary(a_str, b_str)
    assert native_result == py_result


def test_native_full_adder_matches_python():
    for a in range(3):
        for b in range(3):
            for cin in range(3):
                py_s, py_co = py_full_adder(a, b, cin)
                nat_s, nat_co = native_full_adder(a, b, cin)
                assert py_s == nat_s
                assert py_co == nat_co

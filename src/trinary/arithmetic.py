"""
Arithmetic operations for the ternary computing system.
"""

from trinary.conversion import decimal_to_ternary, ternary_to_decimal


validate_ternary = lambda s: all(c in '012' for c in s.lstrip('-')) and s != ""


def add_ternary(a, b):
    """Add two ternary numbers represented as strings."""
    decimal_a = ternary_to_decimal(a)
    decimal_b = ternary_to_decimal(b)
    decimal_sum = decimal_a + decimal_b
    return decimal_to_ternary(decimal_sum)

def subtract_ternary(a, b):
    """Subtract two ternary numbers represented as strings."""
    decimal_a = ternary_to_decimal(a)
    decimal_b = ternary_to_decimal(b)
    decimal_diff = decimal_a - decimal_b
    return decimal_to_ternary(decimal_diff)

def multiply_ternary(a, b):
    """Multiply two ternary numbers represented as strings."""
    decimal_a = ternary_to_decimal(a)
    decimal_b = ternary_to_decimal(b)
    decimal_product = decimal_a * decimal_b
    return decimal_to_ternary(decimal_product)

def divide_ternary(a, b):
    """Divide two ternary numbers represented as strings."""
    decimal_a = ternary_to_decimal(a)
    decimal_b = ternary_to_decimal(b)
    if decimal_b == 0:
        raise ValueError("Cannot divide by zero.")
    decimal_quotient = decimal_a // decimal_b
    return decimal_to_ternary(decimal_quotient)


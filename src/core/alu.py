"""
Ternary ALU (Arithmetic Logic Unit).

Provides: ADD, SUB, AND, OR, NOT, CMP operations on ternary strings.
"""

import sys
from pathlib import Path

_src = Path(__file__).resolve().parent.parent
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from core.adder import ripple_carry_adder
from core.arithmetic import add_ternary, subtract_ternary
from core.logic import tnot, tand, tor, validate_trit
from core.conversion import ternary_to_decimal, decimal_to_ternary


VALID_OPERATIONS = ("ADD", "SUB", "AND", "OR", "NOT", "CMP")


def validate_operation(op):
    """Validate operation name."""
    if op not in VALID_OPERATIONS:
        raise ValueError(f"Invalid operation: {op}. Must be one of {VALID_OPERATIONS}")


def validate_ternary_string(s):
    """Validate a ternary string."""
    if not isinstance(s, str):
        raise ValueError("Input must be a string")
    for c in s:
        if c not in "012":
            raise ValueError(f"Invalid trit: {c}. Must be 0, 1, or 2")
    return True


def pad_equal_length(a, b):
    """Pad strings to equal length with leading zeros."""
    max_len = max(len(a), len(b))
    return a.zfill(max_len), b.zfill(max_len)


def alu(operation, a, b=None):
    """Ternary ALU - Execute operation on ternary strings.

    Args:
        operation (str): ADD, SUB, AND, OR, NOT, or CMP
        a (str): first ternary number
        b (str): second ternary number (required for ADD, SUB, AND, OR; optional for NOT, CMP)

    Returns:
        For ADD: (sum_string, None)
        For SUB: (difference_string, None)
        For AND: (result_string, None)
        For OR: (result_string, None)
        For NOT: (result_string, None)
        For CMP: (comparison_result, None)
            - Returns "EQ" if a == b
            - Returns "LT" if a < b
            - Returns "GT" if a > b

    Examples:
        alu("ADD", "102", "21")   -> ("200", None)
        alu("SUB", "102", "21")   -> ("11", None)    # 11 - 7 = 4
        alu("AND", "102", "21")   -> ("000", None)
        alu("OR", "102", "21")     -> ("122", None)
        alu("NOT", "102")          -> ("210", None)
        alu("CMP", "102", "21")    -> ("GT", None)
    """
    validate_operation(operation)

    if operation in ("ADD", "SUB", "AND", "OR"):
        if b is None:
            raise ValueError(f"Operation {operation} requires two operands")
        validate_ternary_string(a)
        validate_ternary_string(b)

    if operation == "NOT":
        validate_ternary_string(a) if a else None

    if operation == "CMP":
        validate_ternary_string(a)
        if b is not None:
            validate_ternary_string(b)

    if operation == "ADD":
        result, _ = ripple_carry_adder(a, b)
        return (result, None)

    if operation == "SUB":
        result = subtract_ternary(a, b)
        return (result, None)

    if operation == "NOT":
        result = "".join(str(tnot(int(trit))) for trit in a)
        return (result, None)

    if operation == "AND":
        a_padded, b_padded = pad_equal_length(a, b)
        result = "".join(str(tand(int(ta), int(tb))) for ta, tb in zip(a_padded, b_padded))
        return (result, None)

    if operation == "OR":
        a_padded, b_padded = pad_equal_length(a, b)
        result = "".join(str(tor(int(ta), int(tb))) for ta, tb in zip(a_padded, b_padded))
        return (result, None)

    if operation == "CMP":
        dec_a = ternary_to_decimal(a)
        if b is not None:
            dec_b = ternary_to_decimal(b)
        else:
            dec_b = 0
        if dec_a == dec_b:
            return ("EQ", None)
        elif dec_a < dec_b:
            return ("LT", None)
        else:
            return ("GT", None)

    raise ValueError(f"Unknown operation: {operation}")


def print_alu_examples():
    """Print example ALU operations."""
    print("=" * 50)
    print("TERNARY ALU EXAMPLES")
    print("=" * 50)

    examples = [
        ("ADD", "102", "21"),
        ("SUB", "102", "21"),
        ("AND", "102", "21"),
        ("OR", "102", "21"),
        ("NOT", "102", None),
        ("CMP", "102", "21"),
        ("CMP", "10", "10"),
        ("CMP", "1", "2"),
    ]

    for op, a, b in examples:
        result, _ = alu(op, a, b)
        b_str = f", {b}" if b is not None else ""
        print(f"{op:>3} {a}{b_str} -> {result}")

    print("=" * 50)


if __name__ == "__main__":
    print_alu_examples()
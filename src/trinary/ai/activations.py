"""Ternary activation functions and signed-value conversion helpers.

Maps between the project's ternary digit encoding (0, 1, 2) and
signed values (-1, 0, +1) used for neural computation:

    0 -> -1
    1 ->  0
    2 -> +1

All activation functions return ternary digits (0/1/2).
"""


# Fast lookup tables for hot-path conversions
# trit 0/1/2 -> signed -1/0/+1
TRIT_TO_SIGNED_LUT = [-1, 0, 1]
# signed -1/0/+1 -> trit 0/1/2
SIGNED_TO_TRIT_LUT = [0, 1, 2]
# ternary_step via signed offset by +1: -1→0, 0→1, 1→2
TERNARY_STEP_LUT = [0, 1, 2]


def trit_to_signed(trit: int) -> int:
    if trit < 0 or trit > 2:
        raise ValueError(f"Expected ternary digit (0/1/2), got {trit}")
    return TRIT_TO_SIGNED_LUT[trit]


def signed_to_trit(value: int) -> int:
    if value < -1 or value > 1:
        raise ValueError(f"Expected signed value (-1/0/1), got {value}")
    return SIGNED_TO_TRIT_LUT[value + 1]


def ternary_step(value: int) -> int:
    if value < -1:
        return 0
    if value > 1:
        return 2
    return TERNARY_STEP_LUT[value + 1]


def ternary_sign(value: int) -> int:
    """Ternary sign activation function.

    Identical to ternary_step — maps input sign to a ternary digit.

    Args:
        value: Input integer.

    Returns:
        Ternary digit 0, 1, or 2.
    """
    return ternary_step(value)


def ternary_relu(value: int) -> int:
    """Ternary ReLU activation function.

    Negative and zero values map to 1 (neutral).
    Positive values map to their corresponding ternary state
    (2 for positive, 1 for zero).

    Args:
        value: Input integer.

    Returns:
        Ternary digit: 1 for non-positive, 2 for positive.
    """
    if value <= 0:
        return 1
    return 2

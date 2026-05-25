"""Ternary activation functions and signed-value conversion helpers.

Maps between the project's ternary digit encoding (0, 1, 2) and
signed values (-1, 0, +1) used for neural computation:

    0 -> -1
    1 ->  0
    2 -> +1

All activation functions return ternary digits (0/1/2).
"""


def trit_to_signed(trit: int) -> int:
    """Convert a ternary digit to its signed representation.

    Args:
        trit: Ternary digit (0, 1, or 2).

    Returns:
        Signed value: 0 -> -1, 1 -> 0, 2 -> +1.

    Raises:
        ValueError: If trit is not 0, 1, or 2.
    """
    if trit not in (0, 1, 2):
        raise ValueError(f"Expected ternary digit (0/1/2), got {trit}")
    return trit - 1


def signed_to_trit(value: int) -> int:
    """Convert a signed value to its ternary digit representation.

    Args:
        value: Signed integer (-1, 0, or +1).

    Returns:
        Ternary digit: -1 -> 0, 0 -> 1, +1 -> 2.

    Raises:
        ValueError: If value is not -1, 0, or 1.
    """
    if value not in (-1, 0, 1):
        raise ValueError(f"Expected signed value (-1/0/1), got {value}")
    return value + 1


def ternary_step(value: int) -> int:
    """Ternary step activation function.

    Maps any integer to a ternary digit:
        value < 0  -> 0  (negative)
        value == 0 -> 1  (zero)
        value > 0  -> 2  (positive)

    Args:
        value: Input integer.

    Returns:
        Ternary digit 0, 1, or 2.
    """
    if value < 0:
        return 0
    if value == 0:
        return 1
    return 2


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

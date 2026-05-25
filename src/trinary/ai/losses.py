"""Loss functions for ternary neural network training.

All functions accept two sequences of ternary digits (0/1/2) and
return a loss value computed in the signed representation (-1/0/+1).
"""

from trinary.ai.activations import trit_to_signed


def ternary_mse(predicted, target):
    """Mean squared error in signed space.

    Both inputs can be single ternary digits or lists of them.
    MSE = mean((signed(p) - signed(t))^2)

    Args:
        predicted: Ternary digit or list of ternary digits.
        target: Ternary digit or list of matching structure.

    Returns:
        Float MSE value (0.0 for perfect match).

    Raises:
        ValueError: If lengths differ or values are invalid.
    """
    if isinstance(predicted, int) and isinstance(target, int):
        p = trit_to_signed(predicted)
        t = trit_to_signed(target)
        return float((p - t) ** 2)
    if len(predicted) != len(target):
        raise ValueError(
            f"Length mismatch: {len(predicted)} vs {len(target)}"
        )
    total = 0
    n = len(predicted)
    for pv, tv in zip(predicted, target):
        p = trit_to_signed(pv)
        t = trit_to_signed(tv)
        total += (p - t) ** 2
    return total / n


def ternary_absolute_error(predicted, target):
    """Mean absolute error in signed space.

    MAE = mean(|signed(p) - signed(t)|)

    Args:
        predicted: Ternary digit or list of ternary digits.
        target: Ternary digit or list of matching structure.

    Returns:
        Float MAE value (0.0 for perfect match).

    Raises:
        ValueError: If lengths differ or values are invalid.
    """
    if isinstance(predicted, int) and isinstance(target, int):
        p = trit_to_signed(predicted)
        t = trit_to_signed(target)
        return float(abs(p - t))
    if len(predicted) != len(target):
        raise ValueError(
            f"Length mismatch: {len(predicted)} vs {len(target)}"
        )
    total = 0
    n = len(predicted)
    for pv, tv in zip(predicted, target):
        p = trit_to_signed(pv)
        t = trit_to_signed(tv)
        total += abs(p - t)
    return total / n


def classification_error(predicted, target):
    """Classification error: 0 for correct, 1 for incorrect.

    For single values or sequences. The mean is returned for
    sequences (accuracy in reverse).

    Args:
        predicted: Ternary digit or list of ternary digits.
        target: Ternary digit or list of matching structure.

    Returns:
        Float: 0.0 for perfect classification, 1.0 for all wrong.
    """
    if isinstance(predicted, int) and isinstance(target, int):
        return 0.0 if predicted == target else 1.0
    if len(predicted) != len(target):
        raise ValueError(
            f"Length mismatch: {len(predicted)} vs {len(target)}"
        )
    errors = sum(1 for p, t in zip(predicted, target) if p != t)
    return errors / len(predicted)

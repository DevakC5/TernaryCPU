"""TritSIMD — SIMD-like vector operations on ternary digits.

Provides element-wise vector arithmetic, dot products, and
ternary thresholding, all operating on lists of trits (0/1/2).
"""

from trinary.ai.activations import ternary_step, trit_to_signed, signed_to_trit


class TritSIMD:
    """Static methods for parallel trit vector operations.

    Each method takes two lists of ternary digits and returns
    a new list with the operation applied element-wise.
    """

    @staticmethod
    def _validate(a, b=None):
        if b is not None and len(a) != len(b):
            raise ValueError(f"Vector length mismatch: {len(a)} vs {len(b)}")

    @staticmethod
    def add_vectors(a, b):
        """Element-wise ternary addition.

        Internally converts to signed, adds, and applies ternary_step.

        Args:
            a: List of ternary digits.
            b: List of ternary digits.

        Returns:
            List of ternary digits.
        """
        TritSIMD._validate(a, b)
        result = []
        for x, y in zip(a, b):
            s = trit_to_signed(x) + trit_to_signed(y)
            result.append(ternary_step(s))
        return result

    @staticmethod
    def sub_vectors(a, b):
        """Element-wise ternary subtraction.

        Args:
            a: List of ternary digits.
            b: List of ternary digits.

        Returns:
            List of ternary digits.
        """
        TritSIMD._validate(a, b)
        result = []
        for x, y in zip(a, b):
            s = trit_to_signed(x) - trit_to_signed(y)
            result.append(ternary_step(s))
        return result

    @staticmethod
    def mul_vectors(a, b):
        """Element-wise ternary multiplication.

        Args:
            a: List of ternary digits.
            b: List of ternary digits.

        Returns:
            List of ternary digits.
        """
        TritSIMD._validate(a, b)
        result = []
        for x, y in zip(a, b):
            s = trit_to_signed(x) * trit_to_signed(y)
            result.append(ternary_step(s))
        return result

    @staticmethod
    def max_vectors(a, b):
        """Element-wise maximum.

        Args:
            a: List of ternary digits.
            b: List of ternary digits.

        Returns:
            List of ternary digits.
        """
        TritSIMD._validate(a, b)
        return [max(x, y) for x, y in zip(a, b)]

    @staticmethod
    def min_vectors(a, b):
        """Element-wise minimum.

        Args:
            a: List of ternary digits.
            b: List of ternary digits.

        Returns:
            List of ternary digits.
        """
        TritSIMD._validate(a, b)
        return [min(x, y) for x, y in zip(a, b)]

    @staticmethod
    def dot_product(a, b):
        """Inner product of two trit vectors.

        Converts to signed, multiplies element-wise, and sums.

        Args:
            a: List of ternary digits.
            b: List of ternary digits.

        Returns:
            Integer dot product (not ternary — the raw sum).
        """
        TritSIMD._validate(a, b)
        total = 0
        for x, y in zip(a, b):
            total += trit_to_signed(x) * trit_to_signed(y)
        return total

    @staticmethod
    def ternary_threshold(values):
        """Apply ternary_step to each element.

        Args:
            values: List of integers.

        Returns:
            List of ternary digits.
        """
        return [ternary_step(v) for v in values]

    @staticmethod
    def scaled_add(a, b, scale_a=1, scale_b=1):
        """Compute scale_a * a + scale_b * b element-wise in signed space.

        Args:
            a: List of ternary digits.
            b: List of ternary digits.
            scale_a: Integer scale for a.
            scale_b: Integer scale for b.

        Returns:
            List of ternary digits.
        """
        TritSIMD._validate(a, b)
        result = []
        for x, y in zip(a, b):
            s = scale_a * trit_to_signed(x) + scale_b * trit_to_signed(y)
            result.append(ternary_step(s))
        return result

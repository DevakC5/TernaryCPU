"""TritSIMD — SIMD-like vector operations on ternary digits.

Provides element-wise vector arithmetic, dot products, and
ternary thresholding, all operating on lists of trits (0/1/2).
"""

from trinary.ai.activations import TRIT_TO_SIGNED_LUT


_T2S = TRIT_TO_SIGNED_LUT
# ternary_step for range [-2, 2] at offset +2: -2→0, -1→0, 0→1, 1→2, 2→2
_TS5 = [0, 0, 1, 2, 2]


class TritSIMD:
    """Static methods for parallel trit vector operations."""

    @staticmethod
    def _validate(a, b=None):
        if b is not None and len(a) != len(b):
            raise ValueError(f"Vector length mismatch: {len(a)} vs {len(b)}")

    @staticmethod
    def add_vectors(a, b):
        TritSIMD._validate(a, b)
        t2s, ts = _T2S, _TS5
        return [ts[t2s[x] + t2s[y] + 2] for x, y in zip(a, b)]

    @staticmethod
    def sub_vectors(a, b):
        TritSIMD._validate(a, b)
        t2s, ts = _T2S, _TS5
        return [ts[t2s[x] - t2s[y] + 2] for x, y in zip(a, b)]

    @staticmethod
    def mul_vectors(a, b):
        TritSIMD._validate(a, b)
        t2s, ts = _T2S, _TS5
        return [ts[t2s[x] * t2s[y] + 2] for x, y in zip(a, b)]

    @staticmethod
    def max_vectors(a, b):
        TritSIMD._validate(a, b)
        return [x if x > y else y for x, y in zip(a, b)]

    @staticmethod
    def min_vectors(a, b):
        TritSIMD._validate(a, b)
        return [x if x < y else y for x, y in zip(a, b)]

    @staticmethod
    def dot_product(a, b):
        TritSIMD._validate(a, b)
        t2s = _T2S
        total = 0
        for x, y in zip(a, b):
            total += t2s[x] * t2s[y]
        return total

    @staticmethod
    def ternary_threshold(values):
        ts = _TS5
        return [ts[v + 2] if -2 <= v <= 2 else (0 if v < -2 else 2) for v in values]

    @staticmethod
    def scaled_add(a, b, scale_a=1, scale_b=1):
        TritSIMD._validate(a, b)
        t2s, ts = _T2S, _TS5
        return [ts[scale_a * t2s[x] + scale_b * t2s[y] + 2] for x, y in zip(a, b)]

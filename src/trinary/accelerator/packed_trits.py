"""PackedTritArray — compact storage of ternary digits.

Packs 4 trits per byte using 2 bits per trit:
  byte = (t0 << 6) | (t1 << 4) | (t2 << 2) | t3

This achieves 4× compression over Python lists of ints.
"""

import math

from trinary.ai.activations import signed_to_trit, trit_to_signed


_TRITS_PER_BYTE = 4
_BITS_PER_TRIT = 2
_TRIT_MASK = 0b11


def _encode_byte(t0, t1, t2, t3):
    return (t0 << 6) | (t1 << 4) | (t2 << 2) | t3


def _decode_byte(b):
    return [(b >> 6) & _TRIT_MASK, (b >> 4) & _TRIT_MASK,
            (b >> 2) & _TRIT_MASK, b & _TRIT_MASK]


class PackedTritArray:
    """A compact array of ternary digits packed 4 per byte.

    Supports dynamic resizing, get/set, append, extend, slicing,
    iteration, and signed conversion.

    Args:
        initial: Optional iterable of ternary digits to initialise with.
    """

    def __init__(self, initial=None):
        self._data = bytearray()
        self._len = 0
        if initial is not None:
            self.extend(initial)

    @classmethod
    def pack(cls, trits):
        """Create a PackedTritArray from an iterable of trits.

        Args:
            trits: Iterable of ternary digits (0/1/2).

        Returns:
            A new PackedTritArray.
        """
        return cls(trits)

    @classmethod
    def from_bytes(cls, data, length=None):
        """Create from raw packed bytes.

        Args:
            data: bytes or bytearray of packed trits.
            length: Number of trits (defaults to len(data) * 4).

        Returns:
            A new PackedTritArray.
        """
        arr = cls.__new__(cls)
        arr._data = bytearray(data)
        arr._len = length if length is not None else len(data) * _TRITS_PER_BYTE
        return arr

    def _grow(self, min_capacity):
        needed = (min_capacity + _TRITS_PER_BYTE - 1) // _TRITS_PER_BYTE
        while len(self._data) < needed:
            self._data.append(0)

    def __len__(self):
        return self._len

    def __iter__(self):
        for i in range(self._len):
            yield self[i]

    def __getitem__(self, index):
        if isinstance(index, slice):
            return PackedTritArray(list(self)[index])
        if index < 0:
            index += self._len
        if index < 0 or index >= self._len:
            raise IndexError(f"Index {index} out of range for length {self._len}")
        byte_idx = index // _TRITS_PER_BYTE
        trit_idx = index % _TRITS_PER_BYTE
        shift = (3 - trit_idx) * _BITS_PER_TRIT
        return (self._data[byte_idx] >> shift) & _TRIT_MASK

    def __setitem__(self, index, value):
        if value not in (0, 1, 2):
            raise ValueError(f"Invalid ternary digit: {value}")
        if isinstance(index, slice):
            indices = range(*index.indices(self._len))
            vals = list(value)
            if len(indices) != len(vals):
                raise ValueError(f"Slice length mismatch")
            for i, v in zip(indices, vals):
                self[i] = v
            return
        if index < 0:
            index += self._len
        if index < 0 or index >= self._len:
            raise IndexError(f"Index {index} out of range")
        byte_idx = index // _TRITS_PER_BYTE
        trit_idx = index % _TRITS_PER_BYTE
        shift = (3 - trit_idx) * _BITS_PER_TRIT
        mask = ~(_TRIT_MASK << shift)
        self._data[byte_idx] = (self._data[byte_idx] & mask) | (value << shift)

    def append(self, value):
        """Append a single ternary digit."""
        if value not in (0, 1, 2):
            raise ValueError(f"Invalid ternary digit: {value}")
        byte_idx = self._len // _TRITS_PER_BYTE
        self._grow(self._len + 1)
        if byte_idx < len(self._data):
            trit_idx = self._len % _TRITS_PER_BYTE
            shift = (3 - trit_idx) * _BITS_PER_TRIT
            self._data[byte_idx] |= value << shift
        else:
            self._data.append(value << 6)
        self._len += 1

    def extend(self, values):
        """Extend with an iterable of ternary digits."""
        for v in values:
            self.append(v)

    def pop(self, index=-1):
        """Remove and return a trit at the given index."""
        if index < 0:
            index += self._len
        if index < 0 or index >= self._len:
            raise IndexError("pop index out of range")
        val = self[index]
        n = self._len - 1
        for i in range(index, n):
            self[i] = self[i + 1]
        self._len -= 1
        return val

    def to_list(self):
        """Return a plain Python list of trits."""
        return list(self)

    def to_signed(self):
        """Return a list of signed values (-1/0/+1)."""
        return [trit_to_signed(t) for t in self]

    def from_signed(self, signed_values):
        """Replace contents with converted signed values."""
        self.clear()
        self.extend(signed_to_trit(s) for s in signed_values)

    def clear(self):
        """Remove all elements."""
        self._data.clear()
        self._len = 0

    def __repr__(self):
        return f"PackedTritArray({list(self)})"

    def __bytes__(self):
        return bytes(self._data[: (self._len + 3) // 4])

    def memory_bytes(self):
        """Return the number of bytes used for storage."""
        return len(self._data)

    def compression_ratio(self):
        """Compression ratio vs Python list of ints (28 bytes per int)."""
        raw = self._len * 28
        packed = self.memory_bytes()
        return raw / packed if packed > 0 else 1.0

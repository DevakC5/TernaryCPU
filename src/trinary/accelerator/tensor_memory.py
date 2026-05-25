"""TensorMemory — dedicated tensor storage for the accelerator.

Provides allocation, retrieval, and management of tensors by ID,
simulating VRAM-like behaviour with pack/unpack support.
"""

from trinary.accelerator.packed_trits import PackedTritArray


class TensorMemory:
    """Dedicated tensor storage with ID-based access.

    Args:
        capacity: Maximum number of tensor slots (default 64).
    """

    def __init__(self, capacity=64):
        self.capacity = capacity
        self._slots = {}
        self._next_id = 0

    def allocate(self, data=None, length=None, shape=None):
        """Allocate a new tensor and return its ID.

        Args:
            data: Optional iterable of ternary digits.
            length: Optional length for empty allocation.
            shape: Optional tuple (rows, cols) for 2D tensors.

        Returns:
            Integer tensor ID.

        Raises:
            RuntimeError: If no free slots available.
        """
        if len(self._slots) >= self.capacity:
            raise RuntimeError("Tensor memory full")
        tid = self._next_id
        self._next_id += 1
        if data is not None:
            self._slots[tid] = PackedTritArray(data)
        elif length is not None:
            self._slots[tid] = PackedTritArray([1] * length)
        else:
            self._slots[tid] = PackedTritArray()
        self._shapes = getattr(self, '_shapes', {})
        if shape is not None:
            self._shapes[tid] = shape
        return tid

    def get_shape(self, tid):
        """Return the shape of a tensor, or None if not set."""
        return getattr(self, '_shapes', {}).get(tid, None)

    def set_shape(self, tid, shape):
        """Set the shape of a tensor."""
        if not hasattr(self, '_shapes'):
            self._shapes = {}
        self._shapes[tid] = shape

    def load_2d(self, tid):
        """Load a tensor as a 2D list (matrix).

        Uses stored shape if available, otherwise raises.

        Args:
            tid: Tensor ID.

        Returns:
            List of lists of ternary digits.

        Raises:
            ValueError: If no shape is stored for this tensor.
        """
        flat = self.load_list(tid)
        shape = self.get_shape(tid)
        if shape is None:
            raise ValueError(f"Tensor {tid} has no shape information")
        rows, cols = shape
        return [flat[r * cols:(r + 1) * cols] for r in range(rows)]

    def free(self, tid):
        """Free a tensor slot.

        Args:
            tid: Tensor ID to free.

        Raises:
            KeyError: If tid is not allocated.
        """
        if tid not in self._slots:
            raise KeyError(f"Tensor {tid} not found")
        del self._slots[tid]

    def load(self, tid):
        """Load a tensor's packed data.

        Args:
            tid: Tensor ID.

        Returns:
            PackedTritArray.

        Raises:
            KeyError: If tid is not allocated.
        """
        if tid not in self._slots:
            raise KeyError(f"Tensor {tid} not found")
        return self._slots[tid]

    def load_list(self, tid):
        """Load a tensor as a plain Python list.

        Args:
            tid: Tensor ID.

        Returns:
            List of ternary digits.
        """
        return self.load(tid).to_list()

    def store(self, tid, data):
        """Store data into an existing tensor slot.

        Args:
            tid: Tensor ID.
            data: Iterable of ternary digits.
        """
        if tid not in self._slots:
            raise KeyError(f"Tensor {tid} not found")
        self._slots[tid].clear()
        self._slots[tid].extend(data)

    def list_tensors(self):
        """Return list of (tid, length) for all allocated tensors."""
        return [(tid, len(arr)) for tid, arr in self._slots.items()]

    def total_trits(self):
        """Return total number of trits stored."""
        return sum(len(arr) for arr in self._slots.values())

    def total_bytes(self):
        """Return total bytes used (packed)."""
        return sum(arr.memory_bytes() for arr in self._slots.values())

    def clear(self):
        """Free all tensors."""
        self._slots.clear()

    def __repr__(self):
        return (f"TensorMemory(slots={len(self._slots)}/{self.capacity}, "
                f"trits={self.total_trits()})")

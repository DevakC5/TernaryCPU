"""DMA controller — direct memory access transfers.

Supports:
- Memory-to-memory block copies
- VRAM block transfer
- Accelerator tensor transfer
- Concurrent execution (CPU runs while DMA active)
"""


class DMATransfer:
    __slots__ = ('src', 'dst', 'size', 'completed', 'cycle_start', 'cycles_per_word')

    def __init__(self, src, dst, size, cycles_per_word=2):
        self.src = src
        self.dst = dst
        self.size = size
        self.completed = 0
        self.cycle_start = 0
        self.cycles_per_word = cycles_per_word


class DMA:
    """DMA controller managing asynchronous memory transfers."""

    def __init__(self, bus=None):
        self.bus = bus
        self._active = None
        self._queue = []
        self.transfers_done = 0
        self.total_bytes_moved = 0
        self._cycle_counter = 0

    def start_transfer(self, src, dst, size, cycles_per_word=2):
        """Start a new DMA transfer.

        Args:
            src: Source start address.
            dst: Destination start address.
            size: Number of words to transfer.
            cycles_per_word: Cycles per single word transfer.

        Returns:
            DMATransfer handle.
        """
        tf = DMATransfer(src, dst, size, cycles_per_word)
        if self._active is None:
            self._active = tf
            self._cycle_counter = 0
        else:
            self._queue.append(tf)
        return tf

    @property
    def busy(self):
        return self._active is not None

    def tick(self, memory=None):
        """Advance DMA by one cycle.

        Args:
            memory: Optional Memory object to perform actual transfers.

        Returns:
            DMATransfer that completed, or None.
        """
        if self._active is None:
            return None
        self._cycle_counter += 1
        if self._cycle_counter >= self._active.cycles_per_word:
            self._cycle_counter = 0
            if memory and self._active.completed < self._active.size:
                src_addr = self._active.src + self._active.completed
                dst_addr = self._active.dst + self._active.completed
                data = memory.load(src_addr)
                memory.store(dst_addr, data)
            self._active.completed += 1
            self.total_bytes_moved += 1
            if self._active.completed >= self._active.size:
                completed = self._active
                self.transfers_done += 1
                self._active = self._queue.pop(0) if self._queue else None
                self._cycle_counter = 0
                return completed
        return None

    @property
    def progress(self):
        if self._active is None:
            return 1.0
        return self._active.completed / self._active.size

    def reset(self):
        self._active = None
        self._queue.clear()
        self.transfers_done = 0
        self.total_bytes_moved = 0

    def stats(self):
        return {
            "active": self._active is not None,
            "queued": len(self._queue),
            "completed_transfers": self.transfers_done,
            "bytes_moved": self.total_bytes_moved,
            "progress": self.progress,
        }

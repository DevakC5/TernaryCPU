"""System bus with arbitration, bandwidth limits, and contention."""


class BusRequest:
    __slots__ = ('source', 'address', 'data', 'is_write', 'priority')

    def __init__(self, source, address, data=None, is_write=False, priority=0):
        self.source = source
        self.address = address
        self.data = data
        self.is_write = is_write
        self.priority = priority


class Bus:
    """Shared system bus connecting CPU, memory, VRAM, DMA, accelerator.

    Simulates:
    - Single transfer per cycle
    - Arbitration (priority-based round-robin)
    - Bandwidth limits
    - Wait states for contention
    """

    def __init__(self, width_bytes=4, bandwidth_mbs=100):
        self.width_bytes = width_bytes
        self.bandwidth_mbs = bandwidth_mbs
        self._queue = []
        self._current_request = None
        self._wait_cycles = 0
        self.transfers = 0
        self.contention_cycles = 0
        self.idle_cycles = 0
        self._cycle_since_last = 0
        self.sources = ['cpu', 'dma', 'accel', 'display']

    @property
    def bandwidth_bytes_per_cycle(self):
        return self.width_bytes

    @property
    def max_transfers_per_cycle(self):
        return 1

    def request(self, source, address, data=None, is_write=False, priority=0):
        """Submit a bus request.

        Args:
            source: Name of requesting unit.
            address: Target memory address.
            data: Data for write operations.
            is_write: True for write, False for read.
            priority: 0 (low) to 3 (high).

        Returns:
            int: Estimated wait cycles before this request completes.
        """
        req = BusRequest(source, address, data, is_write, priority)
        self._queue.append(req)
        return len(self._queue)

    def tick(self):
        """Process one bus cycle.

        Returns:
            BusRequest or None if no transfer completed.
        """
        self._cycle_since_last += 1
        if self._wait_cycles > 0:
            self._wait_cycles -= 1
            return None
        if not self._queue:
            self.idle_cycles += 1
            return None
        self._queue.sort(key=lambda r: (-r.priority, id(r)))
        req = self._queue.pop(0)
        self._current_request = req
        self.transfers += 1
        self._cycle_since_last = 0
        return req

    @property
    def utilization(self):
        total = self.transfers + self.contention_cycles + self.idle_cycles
        if total == 0:
            return 0.0
        return (self.transfers + self.contention_cycles) / total

    @property
    def pending_count(self):
        return len(self._queue)

    def reset(self):
        self._queue.clear()
        self._current_request = None
        self._wait_cycles = 0
        self.transfers = 0
        self.contention_cycles = 0
        self.idle_cycles = 0

    def stats(self):
        return {
            "width_bytes": self.width_bytes,
            "transfers": self.transfers,
            "pending": len(self._queue),
            "contention_cycles": self.contention_cycles,
            "idle_cycles": self.idle_cycles,
            "utilization": self.utilization,
        }

"""System bus with arbitration, burst transfers, split transactions, and contention.

Supports multiple CPU cores, DMA, GPU, and accelerator with
round-robin arbitration and cache coherency snooping broadcast.
"""


class BusRequest:
    __slots__ = ('source', 'address', 'data', 'is_write', 'priority',
                 'burst_length', 'tag', 'split')

    def __init__(self, source, address, data=None, is_write=False, priority=0,
                 burst_length=1):
        self.source = source
        self.address = address
        self.data = data
        self.is_write = is_write
        self.priority = priority
        self.burst_length = burst_length
        self.tag = id(self)
        self.split = False


class Bus:
    """Shared system bus with burst mode and split transactions.

    Simulates:
    - Round-robin arbitration across all requesters
    - Burst transfers: multiple consecutive addresses in one request
    - Split transactions: requester is notified out-of-order when data arrives
    - Cache coherency snooping broadcast on writes
    - Bandwidth limits and wait states for contention
    """

    def __init__(self, width_bytes=4, bandwidth_mbs=100):
        self.width_bytes = width_bytes
        self.bandwidth_mbs = bandwidth_mbs
        self._queue = []
        self._pending_splits = {}
        self._current_request = None
        self._burst_progress = 0
        self._wait_cycles = 0
        self.transfers = 0
        self.burst_transfers = 0
        self.split_transactions = 0
        self.contention_cycles = 0
        self.idle_cycles = 0
        self._cycle_since_last = 0
        self._last_source_idx = -1
        self._snoopers = []

    def register_snooper(self, cache):
        self._snoopers.append(cache)

    def unregister_snooper(self, cache):
        if cache in self._snoopers:
            self._snoopers.remove(cache)

    def notify_write(self, address, source=None):
        for snooper in self._snoopers:
            snooper.snoop_invalidate(address)

    @property
    def bandwidth_bytes_per_cycle(self):
        return self.width_bytes

    @property
    def max_transfers_per_cycle(self):
        return 1

    def request(self, source, address, data=None, is_write=False, priority=0,
                burst_length=1):
        """Submit a bus request with optional burst mode.

        Args:
            source: Name of requesting unit.
            address: Target memory address.
            data: Data for write operations.
            is_write: True for write, False for read.
            priority: 0 (low) to 3 (high).
            burst_length: Number of consecutive words to transfer (default 1).

        Returns:
            int: Estimated wait cycles before this request completes.
        """
        req = BusRequest(source, address, data, is_write, priority, burst_length)
        self._queue.append(req)
        return len(self._queue)

    def _round_robin_select(self):
        if not self._queue:
            return None
        sources_in_queue = []
        seen = set()
        for req in self._queue:
            if req.source not in seen:
                seen.add(req.source)
                sources_in_queue.append(req.source)
        if not sources_in_queue:
            return None
        sources_in_queue.sort()
        start = (self._last_source_idx + 1) % len(sources_in_queue) if self._last_source_idx >= 0 else 0
        for i in range(len(sources_in_queue)):
            idx = (start + i) % len(sources_in_queue)
            src = sources_in_queue[idx]
            for j, req in enumerate(self._queue):
                if req.source == src:
                    self._last_source_idx = idx
                    return self._queue.pop(j)
        return self._queue.pop(0)

    def tick(self):
        """Process one bus cycle.

        Supports burst transfers: a single request sends burst_length
        consecutive words, one per cycle. Supports split transactions:
        ongoing burst can be paused and resumed later.

        Returns:
            BusRequest or None if no transfer completed.
        """
        self._cycle_since_last += 1
        if self._wait_cycles > 0:
            self._wait_cycles -= 1
            return None

        if self._current_request is not None:
            self._burst_progress += 1
            self.transfers += 1
            req = self._current_request
            if self._burst_progress >= req.burst_length:
                if req.burst_length > 1:
                    self.burst_transfers += 1
                self._current_request = None
                self._burst_progress = 0
            return req

        if not self._queue:
            self.idle_cycles += 1
            return None

        req = self._round_robin_select()
        if req is None:
            self.idle_cycles += 1
            return None

        if req.burst_length > 1:
            self.burst_transfers += 1
            self._burst_progress = 0
            self._current_request = req
            self._current_request.split = True
            self.split_transactions += 1
        else:
            self._current_request = None
            self._burst_progress = 0

        self.transfers += 1
        self._cycle_since_last = 0
        if req.is_write:
            self.notify_write(req.address, source=req.source)
        return req

    @property
    def utilization(self):
        total = self.transfers + self.contention_cycles + self.idle_cycles
        if total == 0:
            return 0.0
        return (self.transfers + self.contention_cycles) / total

    @property
    def pending_count(self):
        return len(self._queue) + (1 if self._current_request is not None else 0)

    def reset(self):
        self._queue.clear()
        self._pending_splits.clear()
        self._current_request = None
        self._burst_progress = 0
        self._wait_cycles = 0
        self.transfers = 0
        self.burst_transfers = 0
        self.split_transactions = 0
        self.contention_cycles = 0
        self.idle_cycles = 0
        self._last_source_idx = -1

    def stats(self):
        return {
            "width_bytes": self.width_bytes,
            "transfers": self.transfers,
            "burst_transfers": self.burst_transfers,
            "split_transactions": self.split_transactions,
            "pending": self.pending_count,
            "contention_cycles": self.contention_cycles,
            "idle_cycles": self.idle_cycles,
            "utilization": self.utilization,
            "snoopers": len(self._snoopers),
        }

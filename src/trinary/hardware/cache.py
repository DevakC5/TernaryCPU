"""Cache — direct-mapped L1 instruction and data caches."""


class CacheLine:
    __slots__ = ('tag', 'valid', 'data', 'dirty')

    def __init__(self):
        self.tag = -1
        self.valid = False
        self.data = {}
        self.dirty = False


class Cache:
    """Direct-mapped cache with configurable size and line width.

    Attributes:
        size_bytes: Total cache size in bytes.
        line_size: Bytes per cache line.
        hit_cycles: Cycles to serve a hit.
        miss_cycles: Cycles to serve a miss (load from next level).
    """

    def __init__(self, name='L1', size_bytes=1024, line_size=16,
                 hit_cycles=1, miss_cycles=10):
        self.name = name
        self.size_bytes = size_bytes
        self.line_size = line_size
        self.hit_cycles = hit_cycles
        self.miss_cycles = miss_cycles
        self.num_lines = size_bytes // line_size
        self.lines = [CacheLine() for _ in range(self.num_lines)]
        self.hits = 0
        self.misses = 0

    def _index(self, address):
        return (address // self.line_size) % self.num_lines

    def _tag(self, address):
        return address // (self.num_lines * self.line_size)

    def read(self, address):
        """Read from cache. Returns (value, cycles).

        Args:
            address: Integer memory address.

        Returns:
            tuple: (data_dict_or_None, cycles_taken)
        """
        idx = self._index(address)
        tag = self._tag(address)
        line = self.lines[idx]
        if line.valid and line.tag == tag:
            self.hits += 1
            return line.data.copy(), self.hit_cycles
        self.misses += 1
        return None, self.miss_cycles

    def write(self, address, data):
        """Write to cache. Returns cycles taken.

        On miss: allocate line (fetch from memory).
        On hit: update line, mark dirty.

        Args:
            address: Integer memory address.
            data: dict of offset->value to write.

        Returns:
            int: Cycles taken.
        """
        idx = self._index(address)
        tag = self._tag(address)
        line = self.lines[idx]
        if line.valid and line.tag == tag:
            line.data.update(data)
            line.dirty = True
            self.hits += 1
            return self.hit_cycles
        line.tag = tag
        line.valid = True
        line.data = data
        line.dirty = True
        self.misses += 1
        return self.miss_cycles

    def flush_line(self, address):
        """Flush a single cache line (write back if dirty).

        Args:
            address: Address within the line to flush.

        Returns:
            int: Cycles to write back (0 if not dirty).
        """
        idx = self._index(address)
        line = self.lines[idx]
        if line.valid and line.dirty:
            line.valid = False
            line.dirty = False
            return self.miss_cycles
        line.valid = False
        return self.hit_cycles

    def flush_all(self):
        cost = 0
        for line in self.lines:
            if line.valid and line.dirty:
                cost += self.miss_cycles
            line.valid = False
            line.dirty = False
        return cost

    @property
    def hit_rate(self):
        total = self.hits + self.misses
        if total == 0:
            return 1.0
        return self.hits / total

    def reset(self):
        for line in self.lines:
            line.tag = -1
            line.valid = False
            line.data.clear()
            line.dirty = False
        self.hits = 0
        self.misses = 0

    def stats(self):
        return {
            "name": self.name,
            "size_bytes": self.size_bytes,
            "line_size": self.line_size,
            "num_lines": self.num_lines,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "hit_cycles": self.hit_cycles,
            "miss_cycles": self.miss_cycles,
        }

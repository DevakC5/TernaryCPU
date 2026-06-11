"""Cache — N-way set-associative L1 cache with LRU replacement.

Supports bus-snooping cache coherency (write-invalidate protocol)
for SMP multi-core systems.
"""


class CacheLine:
    __slots__ = ('tag', 'valid', 'data', 'dirty')

    def __init__(self):
        self.tag = -1
        self.valid = False
        self.data = {}
        self.dirty = False


class CacheSet:
    """A single set in the N-way set-associative cache.

    Uses LRU (Least Recently Used) replacement — the way accessed
    most recently is moved to the front; eviction picks the last way.
    """

    def __init__(self, associativity):
        self.lines = [CacheLine() for _ in range(associativity)]
        self.associativity = associativity
        self._lru_order = list(range(associativity))

    def _touch(self, way):
        self._lru_order.remove(way)
        self._lru_order.insert(0, way)

    def _evict_way(self):
        return self._lru_order[-1]

    def find_line(self, tag):
        for way in self._lru_order:
            line = self.lines[way]
            if line.valid and line.tag == tag:
                return way
        return None

    def get_line(self, tag):
        way = self.find_line(tag)
        if way is not None:
            self._touch(way)
            return self.lines[way]
        return None

    def allocate_line(self, tag):
        evict_way = self._evict_way()
        line = self.lines[evict_way]
        old_data = None
        if line.valid and line.dirty:
            old_data = (line.tag, line.data.copy())
        line.tag = tag
        line.valid = True
        line.data = {}
        line.dirty = False
        self._touch(evict_way)
        return line, old_data


class Cache:
    """N-way set-associative cache with LRU replacement.

    Attributes:
        size_bytes: Total cache size in bytes.
        line_size: Bytes per cache line.
        associativity: Number of ways per set.
        hit_cycles: Cycles to serve a hit.
        miss_cycles: Cycles to serve a miss (load from next level).
    """

    def __init__(self, name='L1', size_bytes=1024, line_size=16,
                 associativity=2, hit_cycles=1, miss_cycles=10):
        self.name = name
        self.size_bytes = size_bytes
        self.line_size = line_size
        self.associativity = associativity
        self.hit_cycles = hit_cycles
        self.miss_cycles = miss_cycles
        self.num_sets = size_bytes // (line_size * associativity)
        if self.num_sets < 1:
            self.num_sets = 1
        self.sets = [CacheSet(associativity) for _ in range(self.num_sets)]
        self.hits = 0
        self.misses = 0
        self.snoop_invalidations = 0

    def _index(self, address):
        return (address // self.line_size) % self.num_sets

    def _tag(self, address):
        return address // (self.num_sets * self.line_size)

    def read(self, address):
        """Read from cache.

        Args:
            address: Integer memory address.

        Returns:
            tuple: (data_dict_or_None, cycles_taken)
        """
        idx = self._index(address)
        tag = self._tag(address)
        cache_set = self.sets[idx]
        line = cache_set.get_line(tag)
        if line is not None:
            self.hits += 1
            return line.data.copy(), self.hit_cycles
        self.misses += 1
        return None, self.miss_cycles

    def write(self, address, data):
        """Write to cache.

        On miss: allocate line (may evict a dirty line).
        On hit: update line, mark dirty.

        Args:
            address: Integer memory address.
            data: dict of offset->value to write.

        Returns:
            int: Cycles taken.
        """
        idx = self._index(address)
        tag = self._tag(address)
        cache_set = self.sets[idx]
        line = cache_set.get_line(tag)
        if line is not None:
            line.data.update(data)
            line.dirty = True
            self.hits += 1
            return self.hit_cycles
        new_line, evicted = cache_set.allocate_line(tag)
        new_line.data = data
        new_line.dirty = True
        self.misses += 1
        return self.miss_cycles

    def snoop_invalidate(self, address):
        """Bus-snoop: invalidate a cache line at the given address.

        Called by the bus when another core writes to this address.
        Implements a write-invalidate coherency protocol.

        Args:
            address: Integer memory address.

        Returns:
            bool: True if the line was valid and is now invalidated.
        """
        idx = self._index(address)
        tag = self._tag(address)
        cache_set = self.sets[idx]
        line = cache_set.get_line(tag)
        if line is not None:
            line.valid = False
            line.dirty = False
            self.snoop_invalidations += 1
            return True
        return False

    def flush_line(self, address):
        """Flush a single cache line (write back if dirty)."""
        idx = self._index(address)
        tag = self._tag(address)
        cache_set = self.sets[idx]
        line = cache_set.get_line(tag)
        if line is not None and line.dirty:
            line.valid = False
            line.dirty = False
            return self.miss_cycles
        if line is not None:
            line.valid = False
        return self.hit_cycles

    def flush_all(self):
        cost = 0
        for cache_set in self.sets:
            for line in cache_set.lines:
                if line.valid and line.dirty:
                    cost += self.miss_cycles
                line.valid = False
                line.dirty = False
        return cost

    @property
    def num_lines(self):
        return self.num_sets * self.associativity

    @property
    def hit_rate(self):
        total = self.hits + self.misses
        if total == 0:
            return 1.0
        return self.hits / total

    def reset(self):
        for cache_set in self.sets:
            for line in cache_set.lines:
                line.tag = -1
                line.valid = False
                line.data.clear()
                line.dirty = False
            cache_set._lru_order = list(range(cache_set.associativity))
        self.hits = 0
        self.misses = 0
        self.snoop_invalidations = 0

    def stats(self):
        return {
            "name": self.name,
            "size_bytes": self.size_bytes,
            "line_size": self.line_size,
            "associativity": self.associativity,
            "num_sets": self.num_sets,
            "num_lines": self.num_lines,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "hit_cycles": self.hit_cycles,
            "miss_cycles": self.miss_cycles,
            "snoop_invalidations": self.snoop_invalidations,
        }

"""Tests for cache subsystem."""

import pytest
from trinary.hardware.cache import Cache


class TestCache:
    def test_create(self):
        c = Cache(name="L1", size_bytes=64, line_size=8)
        assert c.name == "L1"
        assert c.num_lines == 8

    def test_read_miss(self):
        c = Cache(size_bytes=64, line_size=8)
        result, cycles = c.read(0)
        assert result is None
        assert cycles == c.miss_cycles

    def test_write_then_read_hit(self):
        c = Cache(size_bytes=64, line_size=8)
        c.write(0, {0: "0"})
        result, cycles = c.read(0)
        assert result is not None
        assert cycles == c.hit_cycles

    def test_hit_rate(self):
        c = Cache(size_bytes=64, line_size=8)
        c.write(0, {0: "0"})  # miss (allocate line)
        c.read(0)             # hit
        c.read(100)           # miss (different tag)
        assert c.hits == 1
        assert c.misses == 2
        assert c.hit_rate == 1.0 / 3.0

    def test_flush_line(self):
        c = Cache(size_bytes=64, line_size=8)
        c.write(0, {0: "0"})
        cycles = c.flush_line(0)
        assert cycles > 0

    def test_flush_all(self):
        c = Cache(size_bytes=64, line_size=8)
        c.write(0, {0: "0"})
        cost = c.flush_all()
        assert cost > 0

    def test_reset(self):
        c = Cache(size_bytes=64, line_size=8)
        c.write(0, {0: "0"})
        c.read(0)
        c.reset()
        assert c.hits == 0
        assert c.misses == 0

    def test_stats(self):
        c = Cache(size_bytes=64, line_size=8)
        stats = c.stats()
        assert stats["name"] == "L1"
        assert stats["size_bytes"] == 64

    def test_miss_penalty_cycles(self):
        c = Cache(size_bytes=64, line_size=8, miss_cycles=20)
        _, cycles = c.read(999)
        assert cycles == 20

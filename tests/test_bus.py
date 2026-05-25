"""Tests for system bus."""

import pytest
from trinary.hardware.bus import Bus


class TestBus:
    def test_create(self):
        bus = Bus()
        assert bus.width_bytes == 4

    def test_request(self):
        bus = Bus()
        n = bus.request('cpu', 100, data="0", is_write=True)
        assert n == 1

    def test_tick_processes_request(self):
        bus = Bus()
        bus.request('cpu', 100)
        req = bus.tick()
        assert req is not None
        assert req.source == 'cpu'

    def test_tick_idle_when_empty(self):
        bus = Bus()
        req = bus.tick()
        assert req is None

    def test_pending_count(self):
        bus = Bus()
        bus.request('cpu', 100)
        bus.request('dma', 200)
        assert bus.pending_count == 2

    def test_utilization(self):
        bus = Bus()
        bus.request('cpu', 100)
        bus.tick()
        bus.request('cpu', 200)
        bus.tick()
        assert bus.utilization > 0
        assert bus.utilization <= 1.0

    def test_reset(self):
        bus = Bus()
        bus.request('cpu', 100)
        bus.tick()
        bus.reset()
        assert bus.transfers == 0

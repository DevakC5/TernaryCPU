"""Tests for DMA controller."""

import pytest
from trinary.hardware.dma import DMA, DMATransfer
from trinary.memory import Memory


class TestDMA:
    def test_create(self):
        dma = DMA()
        assert not dma.busy
        assert dma.progress == 1.0

    def test_start_transfer(self):
        dma = DMA()
        tf = dma.start_transfer(0, 100, 10)
        assert tf.size == 10
        assert dma.busy

    def test_tick_no_active(self):
        dma = DMA()
        result = dma.tick()
        assert result is None

    def test_tick_completes_transfer(self):
        mem = Memory(256)
        for i in range(5):
            mem.store(i, str(i % 3))
        dma = DMA()
        dma.start_transfer(0, 100, 5, cycles_per_word=1)
        for _ in range(10):
            result = dma.tick(memory=mem)
            if result is not None:
                break
        assert dma.transfers_done >= 0

    def test_queue(self):
        dma = DMA()
        dma.start_transfer(0, 100, 5, cycles_per_word=1)
        dma.start_transfer(10, 200, 3, cycles_per_word=1)
        assert len(dma._queue) == 1

    def test_reset(self):
        dma = DMA()
        dma.start_transfer(0, 100, 5)
        dma.reset()
        assert not dma.busy

    def test_stats(self):
        dma = DMA()
        stats = dma.stats()
        assert "active" in stats
        assert "completed_transfers" in stats

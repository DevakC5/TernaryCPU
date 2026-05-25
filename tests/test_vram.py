"""Tests for VRAM controller."""

import pytest
from trinary.hardware.vram_controller import VRAMController


class TestVRAMController:
    def test_create(self):
        v = VRAMController()
        assert v.fps == 30
        assert v.width_px == 64

    def test_tick(self):
        v = VRAMController()
        info = v.tick()
        assert "frame" in info
        assert "scanline" in info

    def test_write_bandwidth_limit(self):
        v = VRAMController(bandwidth_bytes_per_frame=100)
        for _ in range(100):
            v.tick()
            ok = v.check_write(1)
            if not ok:
                break
        assert v.bandwidth_used_pct > 0

    def test_write_exceeds_bandwidth(self):
        v = VRAMController(bandwidth_bytes_per_frame=10)
        for i in range(15):
            v.check_write(1)
        assert v.total_writes <= 10

    def test_frame_boundary_resets_bandwidth(self):
        v = VRAMController(bandwidth_bytes_per_frame=100)
        cycles_per_frame = v.cycles_per_frame
        for _ in range(cycles_per_frame + 10):
            v.tick()
        assert v._write_bytes_this_frame == 0

    def test_stats(self):
        v = VRAMController()
        stats = v.stats()
        assert "fps" in stats
        assert "bandwidth_used_pct" in stats

    def test_reset(self):
        v = VRAMController()
        v.tick()
        v.check_write(10)
        v.reset()
        assert v.total_writes == 0
        assert v._stalled_cycles == 0

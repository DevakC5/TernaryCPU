"""Tests for hardware timing subsystems."""

import pytest
from trinary.hardware.clock import Clock
from trinary.hardware.pipeline import Pipeline, PipelineStage
from trinary.hardware.hazards import HazardUnit
from trinary.hardware.timing import get_latency, is_branch, is_load


class TestClock:
    def test_create(self):
        c = Clock()
        assert c.cycle == 0

    def test_tick(self):
        c = Clock()
        assert c.tick() == 1
        assert c.tick() == 2

    def test_advance(self):
        c = Clock()
        c.advance(5)
        assert c.cycle == 5

    def test_reset(self):
        c = Clock()
        c.advance(10)
        c.reset()
        assert c.cycle == 0

    def test_frequency(self):
        c = Clock(frequency_hz=1_000_000)
        assert c.period_ns == 1000.0


class TestPipeline:
    def test_create(self):
        p = Pipeline()
        assert len(p.stages) == 5
        assert p.total_instructions == 0

    def test_fetch_and_advance(self):
        p = Pipeline()
        p.fetch("LOAD R0 10", "LOAD", ["R0", "10"])
        for _ in range(6):
            p.advance()
        assert p.total_instructions == 1

    def test_stall(self):
        p = Pipeline()
        p.fetch("ADD R0 R1", "ADD", ["R0", "R1"])
        p.stall()
        p.advance()
        assert p.if_stage.bubble

    def test_flush(self):
        p = Pipeline()
        p.fetch("ADD R0 R1", "ADD", ["R0", "R1"])
        p.flush()
        assert p.if_stage.bubble
        assert p.id_stage.bubble
        assert p.ex_stage.bubble

    def test_visualize(self):
        p = Pipeline()
        out = p.visualize(cycle=1)
        assert "Cycle" in out or "IF" in out or "---" in out


class TestHazardUnit:
    def test_create(self):
        h = HazardUnit()
        assert h.stalls_inserted == 0

    def test_forward_ex(self):
        h = HazardUnit()
        result = h.detect_raw("R0", None, None, "R0", None)
        assert result == HazardUnit.FORWARD_EX_TO_EX

    def test_forward_mem(self):
        h = HazardUnit()
        result = h.detect_raw(None, "R0", None, "R0", None)
        assert result == HazardUnit.FORWARD_MEM_TO_EX

    def test_no_hazard(self):
        h = HazardUnit()
        result = h.detect_raw("R0", None, None, "R1", None)
        assert result is None

    def test_need_stall(self):
        h = HazardUnit()
        assert h.need_stall("R0", "R0", None)

    def test_no_stall_needed(self):
        h = HazardUnit()
        assert not h.need_stall("R0", "R1", None)


class TestTiming:
    def test_get_latency(self):
        assert get_latency("ADD") == 1
        assert get_latency("MUL") == 3
        assert get_latency("DIV") == 5
        assert get_latency("UNKNOWN") == 1

    def test_is_branch(self):
        assert is_branch("JMP")
        assert is_branch("JZ")
        assert not is_branch("ADD")

    def test_is_load(self):
        assert is_load("LOAD")
        assert is_load("LOADM")
        assert not is_load("ADD")

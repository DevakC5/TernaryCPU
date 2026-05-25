"""Tests for profiler."""

import pytest
from trinary.hardware.profiler import Profiler


class TestProfiler:
    def test_create(self):
        p = Profiler()
        assert p.cycles == 0

    def test_record_cycle(self):
        p = Profiler()
        p.record_cycle()
        assert p.cycles == 1

    def test_cpi(self):
        p = Profiler()
        p.record_cycle()
        p.record_cycle()
        p.record_instruction()
        assert p.cpi == 2.0

    def test_ipc(self):
        p = Profiler()
        p.record_cycle()
        p.record_instruction()
        p.record_instruction()
        assert p.ipc == 2.0

    def test_cache_hit_rate(self):
        p = Profiler()
        p.record_cache(hit=True)
        p.record_cache(hit=True)
        p.record_cache(hit=False)
        assert p.cache_hit_rate == 2.0 / 3.0

    def test_branch_accuracy(self):
        p = Profiler()
        p.record_branch(correct=True)
        p.record_branch(correct=False)
        assert p.branch_accuracy == 0.5

    def test_report_contains_fields(self):
        p = Profiler()
        p.record_cycle()
        p.record_instruction()
        report = p.report()
        assert "CPI" in report
        assert "Cycles" in report

    def test_csv(self):
        p = Profiler()
        p.record_cycle()
        p.record_instruction()
        assert len(p.csv_row().split(",")) == 16

    def test_reset(self):
        p = Profiler()
        p.record_cycle()
        p.record_instruction()
        p.reset()
        assert p.cycles == 0

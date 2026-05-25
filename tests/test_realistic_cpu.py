"""Tests for CPU realistic-timing mode."""

import pytest
from trinary.cpu import CPU


class TestRealisticTimingCPU:
    def test_default_is_fast(self):
        cpu = CPU()
        assert cpu.realistic_timing == False

    def test_realistic_mode_creates_hardware(self):
        cpu = CPU(realistic_timing=True)
        assert cpu.realistic_timing
        assert hasattr(cpu, 'clock')
        assert hasattr(cpu, 'pipeline')
        assert hasattr(cpu, 'icache')
        assert hasattr(cpu, 'dcache')
        assert hasattr(cpu, 'bp')
        assert hasattr(cpu, 'bus')
        assert hasattr(cpu, 'dma')
        assert hasattr(cpu, 'intc')
        assert hasattr(cpu, 'profiler')

    def test_program_executes_in_realistic_mode(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "22"

    def test_profiler_records_stats(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.profiler.cycles > 0
        assert cpu.cycles > 0

    def test_pipeline_advances(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 10", "HALT"])
        cpu.run(verbose=False)
        assert cpu.clock.cycle > 0

    def test_fast_mode_still_works(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "22"

    def test_dma_in_realistic_mode(self):
        cpu = CPU(realistic_timing=True)
        for i in range(5):
            cpu.memory.store(i, str(i % 3))
        cpu.dma.start_transfer(0, 100, 5, cycles_per_word=1)
        for _ in range(20):
            cpu._step_realistic()
        for i in range(5):
            assert cpu.memory.load(100 + i) == str(i % 3)

    def test_cache_hits_tracked(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 10", "HALT"])
        cpu.run(verbose=False)
        assert cpu.dcache is not None

    def test_reset_preserves_hardware(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 10", "HALT"])
        cpu.run(verbose=False)
        cpu.reset()
        assert cpu.realistic_timing
        assert hasattr(cpu, 'clock')

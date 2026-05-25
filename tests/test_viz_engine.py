"""Tests for the Visualization Engine snapshot capture."""

import pytest
from trinary.cpu import CPU
from trinary.memory import Memory
from trinary.ui.viz_engine import (
    VisualizationEngine, PipelineSnapshot, CacheSnapshot,
    BranchSnapshot, BusSnapshot, DMASnapshot, InterruptSnapshot,
    ProfilerSnapshot, CycleSnapshot,
)


class TestSnapshots:
    """Test dataclass creation and defaults."""

    def test_pipeline_snapshot_defaults(self):
        s = PipelineSnapshot()
        assert s.if_stage == "---"
        assert s.if_bubble is True
        assert s.if_stalled is False
        assert s.total_instructions == 0

    def test_cache_snapshot_defaults(self):
        s = CacheSnapshot()
        assert s.hits == 0
        assert s.hit_rate == 1.0
        assert s.lines == []

    def test_branch_snapshot_defaults(self):
        s = BranchSnapshot()
        assert s.mode == "two_bit"
        assert s.accuracy == 1.0

    def test_bus_snapshot_defaults(self):
        s = BusSnapshot()
        assert s.transfers == 0
        assert s.utilization == 0.0

    def test_dma_snapshot_defaults(self):
        s = DMASnapshot()
        assert s.active is False
        assert s.progress == 1.0

    def test_interrupt_snapshot_defaults(self):
        s = InterruptSnapshot()
        assert s.pending == 0
        assert s.in_isr is False

    def test_profiler_snapshot_defaults(self):
        s = ProfilerSnapshot()
        assert s.cycles == 0
        assert s.cpi == 0.0

    def test_cycle_snapshot_defaults(self):
        s = CycleSnapshot()
        assert s.cycle == 0
        assert s.pc == 0
        assert s.registers == {}
        assert s.pipeline is not None
        assert s.cache is not None
        assert s.cache_icache is not None


class TestVisualizationEngine:
    """Test the VisualizationEngine capture logic."""

    def test_create(self):
        engine = VisualizationEngine()
        assert engine.history == []
        assert engine.current.cycle == 0

    def test_capture_fast_cpu(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 1", "HALT"])
        engine = VisualizationEngine()
        snap = engine.capture(cpu)
        assert snap.cycle == 0
        assert snap.pc == 0
        assert snap.registers.get("R0") == "0"
        assert snap.clock_cycle == 0
        # Fast mode has no pipeline
        assert snap.pipeline is not None
        assert snap.cache is not None
        assert snap.branch is not None

    def test_capture_realistic_cpu(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 1", "HALT"])
        engine = VisualizationEngine()
        snap = engine.capture(cpu)
        assert snap.clock_cycle == 0
        assert snap.pipeline.if_stage is not None
        assert snap.cache.hits == 0
        assert snap.bus.transfers == 0

    def test_capture_multiple_steps(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 1", "LOAD R1 2", "HALT"])
        engine = VisualizationEngine()
        for _ in range(3):
            cpu.step()
            snap = engine.capture(cpu)
        assert len(engine.history) == 3
        assert engine.current.cycle == 2
        assert engine.current.clock_cycle >= 3

    def test_capture_registers(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 2", "LOAD R1 1", "ADD R0 R1", "HALT"])
        engine = VisualizationEngine()
        for _ in range(4):
            cpu.step()
            engine.capture(cpu)
        last = engine.history[-1]
        assert last.registers.get("R0") == "10"  # 2+1=3 in ternary = "10"

    def test_listener_registration(self):
        engine = VisualizationEngine()
        received = []
        def callback(snap):
            received.append(snap)
        engine.register(callback)
        cpu = CPU()
        cpu.load_program(["LOAD R0 1", "HALT"])
        engine.capture(cpu)
        assert len(received) == 1
        engine.unregister(callback)
        engine.capture(cpu)
        assert len(received) == 1  # no new callbacks

    def test_last_n(self):
        engine = VisualizationEngine()
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 1", "HALT"])
        for _ in range(10):
            cpu.step()
            engine.capture(cpu)
        last5 = engine.last_n(5)
        assert len(last5) == 5

    def test_clear(self):
        engine = VisualizationEngine()
        cpu = CPU()
        cpu.load_program(["HALT"])
        cpu.step()
        engine.capture(cpu)
        assert len(engine.history) == 1
        engine.clear()
        assert len(engine.history) == 0
        assert engine.current.cycle == 0

    def test_pipeline_stage_labels(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 1", "HALT"])
        engine = VisualizationEngine()
        for _ in range(3):
            cpu.step()
            engine.capture(cpu)
        snap = engine.history[-1]
        # Pipeline snapshot should have stage info
        assert hasattr(snap.pipeline, 'if_stage')
        assert hasattr(snap.pipeline, 'id_stage')
        assert hasattr(snap.pipeline, 'ex_stage')

    def test_cache_snapshot_on_realistic(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 1", "HALT"])
        engine = VisualizationEngine()
        cpu.step()
        snap = engine.capture(cpu)
        assert hasattr(snap.cache, 'hits')
        assert hasattr(snap.cache, 'lines')

    def test_branch_snapshot(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 0", "JZ 3", "HALT"])
        engine = VisualizationEngine()
        for _ in range(4):
            cpu.step()
            engine.capture(cpu)
        snap = engine.history[-1]
        assert hasattr(snap.branch, 'predictions')
        assert snap.branch.mode == 'two_bit'

    def test_dma_snapshot(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["HALT"])
        engine = VisualizationEngine()
        cpu.step()
        snap = engine.capture(cpu)
        assert hasattr(snap.dma, 'active')
        assert hasattr(snap.dma, 'completed_transfers')

    def test_interrupt_snapshot(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["HALT"])
        engine = VisualizationEngine()
        cpu.step()
        snap = engine.capture(cpu)
        assert hasattr(snap.interrupt, 'pending')
        assert hasattr(snap.interrupt, 'in_isr')

    def test_profiler_snapshot(self):
        cpu = CPU(realistic_timing=True)
        cpu.load_program(["LOAD R0 1", "HALT"])
        engine = VisualizationEngine()
        for _ in range(3):
            cpu.step()
            engine.capture(cpu)
        snap = engine.history[-1]
        assert hasattr(snap.profiler, 'cpi')
        assert hasattr(snap.profiler, 'ipc')

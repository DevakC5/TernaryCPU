"""Visualization engine — captures CPU+hardware state snapshots for GUI widgets.

Strict separation: UI never modifies CPU state, only reads snapshots.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PipelineSnapshot:
    if_stage: str = "---"
    id_stage: str = "---"
    ex_stage: str = "---"
    mem_stage: str = "---"
    wb_stage: str = "---"
    if_bubble: bool = True
    id_bubble: bool = True
    ex_bubble: bool = True
    mem_bubble: bool = True
    wb_bubble: bool = True
    if_stalled: bool = False
    id_stalled: bool = False
    ex_stalled: bool = False
    mem_stalled: bool = False
    wb_stalled: bool = False
    total_instructions: int = 0
    stall_cycles: int = 0
    flush_count: int = 0


@dataclass
class CacheSnapshot:
    hits: int = 0
    misses: int = 0
    hit_rate: float = 1.0
    lines: list = field(default_factory=list)


@dataclass
class BranchSnapshot:
    predictions: int = 0
    mispredictions: int = 0
    accuracy: float = 1.0
    mode: str = "two_bit"


@dataclass
class BusSnapshot:
    transfers: int = 0
    pending: int = 0
    utilization: float = 0.0
    idle_cycles: int = 0


@dataclass
class DMASnapshot:
    active: bool = False
    queued: int = 0
    completed_transfers: int = 0
    progress: float = 1.0


@dataclass
class InterruptSnapshot:
    pending: int = 0
    in_isr: bool = False
    masked: list = field(default_factory=list)


@dataclass
class ProfilerSnapshot:
    cycles: int = 0
    instructions_retired: int = 0
    cpi: float = 0.0
    ipc: float = 0.0
    total_stalls: int = 0
    cache_hit_rate: float = 1.0
    branch_accuracy: float = 1.0


@dataclass
class CycleSnapshot:
    cycle: int = 0
    pc: int = 0
    sp: int = 0
    registers: dict = field(default_factory=dict)
    flags: dict = field(default_factory=dict)
    halted: bool = False
    clock_cycle: int = 0
    pipeline: PipelineSnapshot = field(default_factory=PipelineSnapshot)
    cache: CacheSnapshot = field(default_factory=CacheSnapshot)
    cache_icache: CacheSnapshot = field(default_factory=CacheSnapshot)
    branch: BranchSnapshot = field(default_factory=BranchSnapshot)
    bus: BusSnapshot = field(default_factory=BusSnapshot)
    dma: DMASnapshot = field(default_factory=DMASnapshot)
    interrupt: InterruptSnapshot = field(default_factory=InterruptSnapshot)
    profiler: ProfilerSnapshot = field(default_factory=ProfilerSnapshot)
    instructions_executed: list = field(default_factory=list)
    execution_events: list = field(default_factory=list)


class VisualizationEngine:
    """Captures CPU+hardware state at each cycle for UI observation.

    The MainWindow calls `capture()` after each CPU step, then all
    registered widgets receive the new snapshot via their update methods.
    """

    def __init__(self):
        self.history: list[CycleSnapshot] = []
        self._listeners = []

    def register(self, callback):
        self._listeners.append(callback)

    def unregister(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def capture(self, cpu):
        """Capture current CPU+hardware state into a snapshot."""
        snap = CycleSnapshot()
        snap.cycle = len(self.history)
        snap.pc = cpu.pc
        snap.sp = cpu.sp
        snap.registers = dict(cpu.registers.dump())
        snap.flags = dict(cpu.flags)
        snap.halted = cpu.halted

        if hasattr(cpu, 'clock') and cpu.realistic_timing:
            snap.clock_cycle = cpu.clock.cycle
            snap.pipeline = self._capture_pipeline(cpu)
            snap.cache = self._capture_cache(cpu, 'dcache')
            snap.cache_icache = self._capture_cache(cpu, 'icache')
            snap.branch = self._capture_branch(cpu)
            snap.bus = self._capture_bus(cpu)
            snap.dma = self._capture_dma(cpu)
            snap.interrupt = self._capture_interrupts(cpu)
            snap.profiler = self._capture_profiler(cpu)

        self.history.append(snap)
        for cb in self._listeners:
            cb(snap)
        return snap

    def _capture_pipeline(self, cpu):
        p = PipelineSnapshot()
        if hasattr(cpu, 'pipeline'):
            pipe = cpu.pipeline
            p.if_stage = self._stage_label(pipe.if_stage)
            p.id_stage = self._stage_label(pipe.id_stage)
            p.ex_stage = self._stage_label(pipe.ex_stage)
            p.mem_stage = self._stage_label(pipe.mem_stage)
            p.wb_stage = self._stage_label(pipe.wb_stage)
            p.if_bubble = pipe.if_stage.bubble
            p.id_bubble = pipe.id_stage.bubble
            p.ex_bubble = pipe.ex_stage.bubble
            p.mem_bubble = pipe.mem_stage.bubble
            p.wb_bubble = pipe.wb_stage.bubble
            # stalled = cycles_remaining > 1 (multi-cycle operation) OR
            #           explicitly stalled by hazard unit
            p.if_stalled = pipe.if_stage.cycles_remaining > 1 and not pipe.if_stage.bubble
            p.id_stalled = pipe.id_stage.cycles_remaining > 1 and not pipe.id_stage.bubble
            p.ex_stalled = pipe.ex_stage.cycles_remaining > 1 and not pipe.ex_stage.bubble
            p.mem_stalled = pipe.mem_stage.cycles_remaining > 1 and not pipe.mem_stage.bubble
            p.wb_stalled = pipe.wb_stage.cycles_remaining > 1 and not pipe.wb_stage.bubble
            p.total_instructions = pipe.total_instructions
            p.stall_cycles = pipe.stall_cycles
            p.flush_count = pipe.flush_count
        return p

    def _capture_cache(self, cpu, cache_attr='dcache'):
        c = CacheSnapshot()
        if hasattr(cpu, cache_attr):
            cache = getattr(cpu, cache_attr)
            c.hits = cache.hits
            c.misses = cache.misses
            c.hit_rate = cache.hit_rate
            for line in cache.lines[:32]:
                c.lines.append({
                    'tag': line.tag,
                    'valid': line.valid,
                    'dirty': line.dirty,
                })
        return c

    def _capture_branch(self, cpu):
        b = BranchSnapshot()
        if hasattr(cpu, 'bp'):
            bp = cpu.bp
            b.predictions = bp.predictions
            b.mispredictions = bp.mispredictions
            b.accuracy = bp.accuracy
            b.mode = bp.mode
        return b

    def _capture_dma(self, cpu):
        d = DMASnapshot()
        if hasattr(cpu, 'dma'):
            dma = cpu.dma
            d.active = dma.busy
            d.queued = len(dma._queue) if hasattr(dma, '_queue') else 0
            d.completed_transfers = dma.transfers_done
            d.progress = dma.progress
        return d

    def _capture_bus(self, cpu):
        b = BusSnapshot()
        if hasattr(cpu, 'bus'):
            bus = cpu.bus
            b.transfers = bus.transfers
            b.pending = bus.pending_count
            b.utilization = bus.utilization
            b.idle_cycles = bus.idle_cycles
        return b

    def _capture_interrupts(self, cpu):
        ic = InterruptSnapshot()
        if hasattr(cpu, 'intc'):
            intc = cpu.intc
            ic.pending = intc.pending_count
            ic.in_isr = getattr(intc, '_in_isr', False)
            ic.masked = list(getattr(intc, '_masked', []))
        return ic

    def _capture_profiler(self, cpu):
        p = ProfilerSnapshot()
        if hasattr(cpu, 'profiler'):
            prof = cpu.profiler
            p.cycles = prof.cycles
            p.instructions_retired = prof.instructions_retired
            p.cpi = prof.cpi
            p.ipc = prof.ipc
            p.total_stalls = prof.total_stalls
            p.cache_hit_rate = prof.cache_hit_rate
            p.branch_accuracy = prof.branch_accuracy
        return p

    def _stage_label(self, stage):
        if stage.bubble:
            return "---"
        return f"{stage.opcode or '???'} {' '.join(stage.operands or [])}"

    @property
    def current(self):
        return self.history[-1] if self.history else CycleSnapshot()

    def last_n(self, n=10):
        return self.history[-n:] if self.history else []

    def clear(self):
        self.history.clear()

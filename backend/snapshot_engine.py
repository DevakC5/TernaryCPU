"""Snapshot engine — wraps the TernaryCPU and emits structured snapshots over WS.

Strict separation: this module only reads CPU state via public APIs.
"""

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

from trinary.cpu import CPU
from trinary.machine import Machine
from trinary.memory import Memory


@dataclass
class PipelineStageState:
    instruction: str = "---"
    opcode: str = ""
    bubble: bool = True
    stalled: bool = False


@dataclass
class PipelineSnapshot:
    if_stage: PipelineStageState = field(default_factory=PipelineStageState)
    id_stage: PipelineStageState = field(default_factory=PipelineStageState)
    ex_stage: PipelineStageState = field(default_factory=PipelineStageState)
    mem_stage: PipelineStageState = field(default_factory=PipelineStageState)
    wb_stage: PipelineStageState = field(default_factory=PipelineStageState)
    total_instructions: int = 0
    stall_cycles: int = 0
    flush_count: int = 0


@dataclass
class CacheLineState:
    tag: int = -1
    valid: bool = False
    dirty: bool = False


@dataclass
class CacheSnapshot:
    name: str = "L1"
    hits: int = 0
    misses: int = 0
    hit_rate: float = 1.0
    lines: list = field(default_factory=list)


@dataclass
class BranchSnapshot:
    mode: str = "two_bit"
    predictions: int = 0
    mispredictions: int = 0
    accuracy: float = 1.0
    counters: dict = field(default_factory=dict)


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


@dataclass
class ProfilerSnapshot:
    cycles: int = 0
    instructions: int = 0
    cpi: float = 0.0
    ipc: float = 0.0
    total_stalls: int = 0
    cache_hit_rate: float = 1.0
    branch_accuracy: float = 1.0


@dataclass
class SystemSnapshot:
    cycle: int = 0
    clock_cycle: int = 0
    pc: int = 0
    sp: int = 0
    halted: bool = False
    registers: dict = field(default_factory=dict)
    flags: dict = field(default_factory=dict)
    pipeline: Optional[PipelineSnapshot] = None
    icache: Optional[CacheSnapshot] = None
    dcache: Optional[CacheSnapshot] = None
    branch: Optional[BranchSnapshot] = None
    bus: Optional[BusSnapshot] = None
    dma: Optional[DMASnapshot] = None
    interrupt: Optional[InterruptSnapshot] = None
    profiler: Optional[ProfilerSnapshot] = None
    current_instruction: str = ""
    instructions_loaded: int = 0
    timestamp: float = 0.0

    def to_json(self):
        d = asdict(self)
        d["timestamp"] = self.timestamp or time.time()
        return d


class SnapshotEngine:
    """Wraps the TernaryCPU and produces JSON-serializable snapshots."""

    def __init__(self, memory_size=10000, realistic_timing=True):
        self.memory = Memory(memory_size)
        self.cpu = CPU(memory=self.memory, realistic_timing=realistic_timing)
        self.machine = Machine()
        self.program = []
        self.machine_code = []
        self.labels = {}
        self.step_count = 0
        self.cycle_count = 0
        self.last_instruction = ""

    def load_program(self, source: str) -> dict:
        """Load assembly source. Returns {success, message, labels, instr_count}."""
        try:
            self.machine_code, self.program, self.labels = self.machine.assemble(source)
            self.cpu.load_program(self.program)
            self.step_count = 0
            self.cycle_count = 0
            return {
                "success": True,
                "message": f"Assembled OK — {len(self.program)} instructions",
                "labels": self.labels,
                "instruction_count": len(self.program),
                "instructions": self.program,
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def step(self, count: int = 1) -> list[SystemSnapshot]:
        """Step the CPU by N cycles, returning snapshots for each."""
        snapshots = []
        for _ in range(count):
            if self.cpu.halted:
                snapshots.append(self.capture())
                break
            self.step_count += 1
            self.cpu.step()
            self.cycle_count = self.cpu.cycles
            if self.cpu.pc < len(self.program):
                self.last_instruction = self.program[self.cpu.pc]
            snapshots.append(self.capture())
        return snapshots

    def run_to_halt(self) -> list[SystemSnapshot]:
        """Run CPU until halted, returning all intermediate snapshots."""
        snapshots = []
        while not self.cpu.halted and self.cpu.pc < len(self.program):
            self.step_count += 1
            self.cpu.step()
            self.cycle_count = self.cpu.cycles
            if self.cpu.pc < len(self.program):
                self.last_instruction = self.program[self.cpu.pc]
            snapshots.append(self.capture())
        snapshots.append(self.capture())
        return snapshots

    def reset(self):
        """Reset CPU and reload program."""
        self.cpu.reset()
        if self.program:
            self.cpu.load_program(self.program)
        self.step_count = 0
        self.cycle_count = 0

    def capture(self) -> SystemSnapshot:
        """Capture current CPU state as a SystemSnapshot."""
        current_instr = ""
        if self.cpu.pc < len(self.program):
            current_instr = self.program[self.cpu.pc]
        elif self.last_instruction:
            current_instr = self.last_instruction

        snap = SystemSnapshot(
            cycle=self.step_count,
            clock_cycle=self.cpu.cycles,
            pc=self.cpu.pc,
            sp=self.cpu.sp,
            halted=self.cpu.halted,
            registers=dict(self.cpu.registers.dump()),
            flags=dict(self.cpu.flags),
            current_instruction=current_instr,
            instructions_loaded=len(self.program),
            timestamp=time.time(),
        )

        if hasattr(self.cpu, 'pipeline') and self.cpu.realistic_timing:
            snap.pipeline = self._capture_pipeline()
            snap.icache = self._capture_cache("icache")
            snap.dcache = self._capture_cache("dcache")
            snap.branch = self._capture_branch()
            snap.bus = self._capture_bus()
            snap.dma = self._capture_dma()
            snap.interrupt = self._capture_interrupts()
            snap.profiler = self._capture_profiler()

        return snap

    def _stage_state(self, stage) -> PipelineStageState:
        if stage.bubble:
            return PipelineStageState()
        instr = f"{stage.opcode or '???'} {' '.join(stage.operands or [])}"
        stalled = stage.cycles_remaining > 1 and not stage.bubble
        return PipelineStageState(
            instruction=instr,
            opcode=stage.opcode or "",
            bubble=stage.bubble,
            stalled=stalled,
        )

    def _capture_pipeline(self) -> PipelineSnapshot:
        p = self.cpu.pipeline
        return PipelineSnapshot(
            if_stage=self._stage_state(p.if_stage),
            id_stage=self._stage_state(p.id_stage),
            ex_stage=self._stage_state(p.ex_stage),
            mem_stage=self._stage_state(p.mem_stage),
            wb_stage=self._stage_state(p.wb_stage),
            total_instructions=p.total_instructions,
            stall_cycles=p.stall_cycles,
            flush_count=p.flush_count,
        )

    def _capture_cache(self, name="dcache") -> CacheSnapshot:
        if not hasattr(self.cpu, name):
            return CacheSnapshot(name=name)
        c = getattr(self.cpu, name)
        lines = []
        for line in c.lines[:32]:
            lines.append(CacheLineState(tag=line.tag, valid=line.valid, dirty=line.dirty))
        return CacheSnapshot(
            name=c.name,
            hits=c.hits,
            misses=c.misses,
            hit_rate=c.hit_rate,
            lines=[asdict(l) for l in lines],
        )

    def _capture_branch(self) -> BranchSnapshot:
        bp = self.cpu.bp
        return BranchSnapshot(
            mode=bp.mode,
            predictions=bp.predictions,
            mispredictions=bp.mispredictions,
            accuracy=bp.accuracy,
            counters={str(k): v for k, v in bp._counters.items()},
        )

    def _capture_bus(self) -> BusSnapshot:
        bus = self.cpu.bus
        return BusSnapshot(
            transfers=bus.transfers,
            pending=bus.pending_count,
            utilization=bus.utilization,
            idle_cycles=bus.idle_cycles,
        )

    def _capture_dma(self) -> DMASnapshot:
        dma = self.cpu.dma
        return DMASnapshot(
            active=dma.busy,
            queued=len(dma._queue) if hasattr(dma, '_queue') else 0,
            completed_transfers=dma.transfers_done,
            progress=dma.progress,
        )

    def _capture_interrupts(self) -> InterruptSnapshot:
        intc = self.cpu.intc
        return InterruptSnapshot(
            pending=intc.pending_count,
            in_isr=getattr(intc, '_in_isr', False),
        )

    def _capture_profiler(self) -> ProfilerSnapshot:
        p = self.cpu.profiler
        return ProfilerSnapshot(
            cycles=p.cycles,
            instructions=p.instructions_retired,
            cpi=p.cpi,
            ipc=p.ipc,
            total_stalls=p.total_stalls,
            cache_hit_rate=p.cache_hit_rate,
            branch_accuracy=p.branch_accuracy,
        )

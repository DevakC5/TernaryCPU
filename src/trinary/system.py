"""
Multi-Core SMP System Wrapper.

Instantiates multiple CPU cores sharing a unified main memory,
a single system clock, a shared bus (with round-robin arbitration),
and a shared DMA controller. Each core has private L1 caches that
snoop the bus for cache-coherency invalidation.

Lock states (ternary) for atomic TCAS instruction:
    0 = Unlocked
    1 = Read-Lock  (shared read, no writes)
    2 = Write-Lock (exclusive access)
"""

from trinary.cpu import CPU
from trinary.memory import Memory
from trinary.hardware import Clock, Bus, DMA


class MultiCoreSystem:
    """Symmetric Multiprocessing system with N CPU cores.

    All cores share the same Memory, Clock, Bus, and DMA controller.
    Each core has its own private L1 cache (I + D) that participates
    in bus snooping for write-invalidate coherency.
    """

    def __init__(self, num_cores=2, memory_size=10000, realistic_timing=False):
        self.realistic_timing = realistic_timing
        self.memory = Memory(size=memory_size)
        self.clock = Clock()
        self.bus = Bus()
        self.dma = DMA(bus=self.bus)

        self.cores = []
        for i in range(num_cores):
            core = CPU(
                memory=self.memory,
                realistic_timing=realistic_timing,
                core_id=i,
                shared_bus=self.bus,
                shared_clock=self.clock,
                shared_dma=self.dma,
            )
            self.cores.append(core)

        self.cycle = 0

    def step(self):
        """Execute one synchronous cycle across all cores.

        In fast mode: each core executes one instruction per step.
        In realistic mode: each core advances one clock cycle through
        its pipeline, and the shared clock ticks once.

        Returns:
            int: Number of cores that are still running.
        """
        if self.realistic_timing:
            self.clock.tick()
            self.bus.tick()
            self.dma.tick(memory=self.memory)

        active = 0
        for core in self.cores:
            if not core.halted:
                core.step()
                active += 1

        self.cycle += 1
        return active

    def run(self, max_cycles=None, verbose=False):
        """Run the system until all cores halt or max_cycles reached.

        Args:
            max_cycles: Optional cycle limit.
            verbose: Print per-step info if True.

        Returns:
            dict: Map of core_id -> final register state.
        """
        step_num = 0
        while True:
            active = self.step()
            if active == 0:
                break
            step_num += 1
            if max_cycles and step_num >= max_cycles:
                break
            if verbose and step_num % 1000 == 0:
                print(f"[cycle {self.cycle}] active cores: {active}")

        return {c.core_id: c.registers.dump() for c in self.cores}

    def load_program(self, core_id, instructions):
        """Load a program onto a specific core.

        Args:
            core_id: Target core index.
            instructions: List of instruction strings.
        """
        if 0 <= core_id < len(self.cores):
            self.cores[core_id].load_program(instructions)

    def load_program_all(self, instructions):
        """Load the same program onto every core.

        Args:
            instructions: List of instruction strings.
        """
        for core in self.cores:
            core.load_program(list(instructions))

    def send_ipi(self, source_core, target_core, irq_num):
        """Send an Inter-Processor Interrupt from one core to another.

        Args:
            source_core: Source core index.
            target_core: Target core index.
            irq_num: Interrupt request line to trigger on the target.
        """
        if 0 <= target_core < len(self.cores):
            if hasattr(self.cores[source_core], 'intc'):
                self.cores[source_core].intc.send_ipi(
                    self.cores[target_core].intc, irq_num
                )

    @property
    def stats(self):
        return {
            "cores": len(self.cores),
            "cycle": self.cycle,
            "memory_size": self.memory.size,
            "bus": self.bus.stats(),
            "clock": self.clock.stats(),
            "dma": self.dma.stats() if hasattr(self.dma, 'stats') else {},
        }

    def reset(self):
        """Reset the entire system."""
        self.memory.clear_all()
        self.clock.reset()
        self.bus.reset()
        self.dma.reset()
        for core in self.cores:
            core.reset()
        self.cycle = 0

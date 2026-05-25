"""Performance profiler and statistics tracking."""


class Profiler:
    """Tracks performance metrics across all hardware subsystems.

    Collects:
    - CPI / IPC
    - Pipeline stall breakdown
    - Cache hit/miss rates
    - Branch prediction accuracy
    - Bus utilization
    - DMA throughput
    - VRAM bandwidth usage
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.cycles = 0
        self.instructions_retired = 0
        self.stalls_data = 0
        self.stalls_control = 0
        self.stalls_structural = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.branch_predictions = 0
        self.branch_mispredicts = 0
        self.bus_transfers = 0
        self.bus_contention = 0
        self.dma_bytes = 0
        self.dma_transfers = 0
        self.vram_writes = 0
        self.vram_stalls = 0

    def record_cycle(self):
        self.cycles += 1

    def record_instruction(self):
        self.instructions_retired += 1

    def record_stall(self, kind='data'):
        if kind == 'data':
            self.stalls_data += 1
        elif kind == 'control':
            self.stalls_control += 1
        elif kind == 'structural':
            self.stalls_structural += 1

    def record_cache(self, hit=True):
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    def record_branch(self, correct=True):
        self.branch_predictions += 1
        if not correct:
            self.branch_mispredicts += 1

    def record_bus(self, transfer=True):
        if transfer:
            self.bus_transfers += 1
        else:
            self.bus_contention += 1

    def record_dma(self, bytes_moved=1, transfer_complete=False):
        self.dma_bytes += bytes_moved
        if transfer_complete:
            self.dma_transfers += 1

    def record_vram(self, write=True, stalled=False):
        if write:
            self.vram_writes += 1
        if stalled:
            self.vram_stalls += 1

    @property
    def cpi(self):
        if self.instructions_retired == 0:
            return 0.0
        return self.cycles / self.instructions_retired

    @property
    def ipc(self):
        if self.cycles == 0:
            return 0.0
        return self.instructions_retired / self.cycles

    @property
    def cache_hit_rate(self):
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 1.0
        return self.cache_hits / total

    @property
    def branch_accuracy(self):
        if self.branch_predictions == 0:
            return 1.0
        return 1.0 - (self.branch_mispredicts / self.branch_predictions)

    @property
    def total_stalls(self):
        return self.stalls_data + self.stalls_control + self.stalls_structural

    def report(self):
        lines = ["=" * 55]
        lines.append("  Performance Profile")
        lines.append("=" * 55)
        lines.append(f"  Cycles:              {self.cycles}")
        lines.append(f"  Instructions:        {self.instructions_retired}")
        lines.append(f"  CPI:                 {self.cpi:.3f}")
        lines.append(f"  IPC:                 {self.ipc:.3f}")
        lines.append(f"  Total Stalls:        {self.total_stalls}")
        lines.append(f"    Data:              {self.stalls_data}")
        lines.append(f"    Control:           {self.stalls_control}")
        lines.append(f"    Structural:        {self.stalls_structural}")
        lines.append(f"  Cache Hit Rate:      {self.cache_hit_rate:.1%}")
        lines.append(f"  Branch Accuracy:     {self.branch_accuracy:.1%}")
        lines.append(f"  Bus Transfers:       {self.bus_transfers}")
        lines.append(f"  Bus Contention:      {self.bus_contention}")
        lines.append(f"  DMA Bytes:           {self.dma_bytes}")
        lines.append(f"  VRAM Writes:         {self.vram_writes}")
        lines.append(f"  VRAM Stalls:         {self.vram_stalls}")
        lines.append("-" * 55)
        return "\n".join(lines)

    def csv_header(self):
        return ("cycles,instructions,cpi,ipc,stalls_data,stalls_control,"
                "stalls_structural,cache_hits,cache_misses,"
                "branch_pred,branch_miss,bus_tx,bus_cont,"
                "dma_bytes,vram_writes,vram_stalls")

    def csv_row(self):
        return (f"{self.cycles},{self.instructions_retired},{self.cpi:.3f},"
                f"{self.ipc:.3f},{self.stalls_data},{self.stalls_control},"
                f"{self.stalls_structural},{self.cache_hits},{self.cache_misses},"
                f"{self.branch_predictions},{self.branch_mispredicts},"
                f"{self.bus_transfers},{self.bus_contention},"
                f"{self.dma_bytes},{self.vram_writes},{self.vram_stalls}")

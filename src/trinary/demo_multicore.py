"""
Multi-Core SMP Demo — runs 4 synthetic workloads across 4 CPU cores
and renders ASCII usage graphs (bar charts, time series, stats tables).

Usage:
    python -m trinary.demo_multicore
"""

import math
import time

from trinary.system import MultiCoreSystem
from trinary.assembler import Assembler


# ═══════════════════════════════════════════════════════════════
#  Synthetic workloads (assembly source → assembled programs)
# ═══════════════════════════════════════════════════════════════

def _assemble(source):
    asm = Assembler()
    prog, labels = asm.assemble(source)
    return prog


def workload_compute():
    """Core 0: Compute — dense ALU, MUL chains (3-cycle op), few branches.

    Register map:
      R0 = free work register
      R1 = 1 (const, decrement)
      R2 = 0 (const, CMP sentinel)
      R3 = loop counter = 101 (10 decimal iterations)
    """
    return _assemble("""
        LOAD R0 2
        LOAD R1 1
        LOAD R2 0
        LOAD R3 202
    loop:
        MUL R0 R0
        ADD R0 R1
        MUL R0 R0
        ADD R0 R1
        MUL R0 R0
        ADD R0 R1
        MUL R0 R0
        ADD R0 R1
        MUL R0 R0
        ADD R0 R1
        MUL R0 R0
        ADD R0 R1
        MUL R0 R0
        ADD R0 R1
        SUB R3 R1
        CMP R3 R2
        JNZ loop
        HALT
    """)


def workload_memory():
    """Core 1: Memory — STOREM/LOADM streaming, no branches except loop exit.

    Register map:
      R0 = data value
      R1 = 1 (const, decrement)
      R2 = 0 (const, CMP sentinel)
      R3 = loop counter = 202 (20 decimal iterations)
    """
    return _assemble("""
        LOAD R0 1
        LOAD R1 1
        LOAD R2 0
        LOAD R3 202
    loop:
        STOREM 200 R0
        LOADM 200 R2
        STOREM 202 R0
        LOADM 202 R2
        STOREM 204 R0
        LOADM 204 R2
        STOREM 206 R0
        LOADM 206 R2
        STOREM 208 R0
        LOADM 208 R2
        STOREM 210 R0
        LOADM 210 R2
        STOREM 212 R0
        LOADM 212 R2
        SUB R3 R1
        CMP R3 R2
        JNZ loop
        HALT
    """)


def workload_mixed():
    """Core 2: Mixed — alternates ALU / memory with a 50/50 branch.

    R0 toggles between 0 and 1 each iteration.
    CMP R0, R1 (where R1=1) alternates equal/not-equal every iter.
    JZ is taken 50%, not-taken 50% → the 2-bit predictor saturates
    at 50% (always mispredicts on alternating pattern).
    """
    return _assemble("""
        LOAD R0 1
        LOAD R1 1
        LOAD R2 0
        LOAD R3 202
    loop:
        CMP R0 R1
        JZ skip
        ADD R0 R1
        MUL R0 R1
        JMP next
    skip:
        SUB R0 R1
        STOREM 150 R0
    next:
        SUB R3 R1
        CMP R3 R2
        JNZ loop
        HALT
    """)


def workload_branch():
    """Core 3: Branch — alternating JZ taken/not-taken, heavy predictor stress.

    R0 toggles between 0 and 1 every iteration → JZ target alternates.
    JZ is taken 50%, not-taken 50% → ~0% accuracy for 2-bit predictor.
    Loop JNZ is taken 19/20 times → high accuracy after warmup.
    """
    return _assemble("""
        LOAD R0 0
        LOAD R1 1
        LOAD R2 0
        LOAD R3 202
    loop:
        CMP R0 R1
        JZ body_b
    body_a:
        ADD R0 R1
        MUL R0 R1
        JMP next
    body_b:
        SUB R0 R1
        STOREM 200 R0
    next:
        SUB R3 R1
        CMP R3 R2
        JNZ loop
        HALT
    """)


WORKLOADS = [
    ("Compute",   workload_compute(),   "#ff8844"),
    ("Memory",    workload_memory(),    "#4488ff"),
    ("Mixed",     workload_mixed(),     "#88ff88"),
    ("Branch",    workload_branch(),    "#ff4488"),
]


# ═══════════════════════════════════════════════════════════════
#  ASCII chart rendering utilities
# ═══════════════════════════════════════════════════════════════

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def hbar(value, max_val, width=40, fill="█", empty="░"):
    """Single horizontal bar."""
    frac = value / max(max_val, 1e-9)
    filled = int(round(frac * width))
    filled = _clamp(filled, 0, width)
    return fill * filled + empty * (width - filled)


def hbar_chart(items, width=40, title="", fmt=".3f"):
    """Horizontal bar chart.  items: list of (label, value, color_ignored)."""
    lines = []
    if title:
        pad = (width + 16 - len(title)) // 2
        lines.append(" " * pad + title)
        lines.append("")
    max_val = max((v for _, v, _ in items), default=1)
    for label, value, _ in items:
        bar = hbar(value, max_val, width)
        lines.append(f"  {label:<10} {bar}  {value:{fmt}}")
    return "\n".join(lines) + "\n"


TS_W = 64
TS_H = 14


def time_series_chart(samples, width=TS_W, height=TS_H, title=""):
    """ASCII time-series line chart.

    Args:
        samples: list of float values in chronological order.
        width, height: character dimensions.
        title: optional title centered above chart.

    Returns:
        str: rendered chart.
    """
    if len(samples) < 2:
        return f"  {title}: insufficient data ({len(samples)} points)\n"

    lines = []
    if title:
        pad = (width - len(title)) // 2
        lines.append(" " * pad + title)
        lines.append("")

    mn = min(samples)
    mx = max(samples)
    if mx - mn < 1e-9:
        lo = mn - 0.05 if mn > 0 else 0
        hi = mn + 0.05
        if hi - lo < 0.001:
            hi = lo + 0.1
        mn, mx = lo, hi

    chart_h = height - 2
    n = len(samples)
    fmt = ".3f"

    grid = [[" "] * width for _ in range(chart_h)]

    for i in range(n):
        x = int(round((i / max(n - 1, 1)) * (width - 1)))
        x = _clamp(x, 0, width - 1)
        frac = (samples[i] - mn) / (mx - mn) if (mx - mn) > 0 else 0.5
        frac = _clamp(frac, 0.0, 1.0)
        y = chart_h - 1 - int(round(frac * (chart_h - 1)))
        y = _clamp(y, 0, chart_h - 1)
        if 0 <= y < chart_h and 0 <= x < width:
            grid[y][x] = "●"

    for row in range(chart_h):
        frac = 1.0 - row / (chart_h - 1)
        val = mn + frac * (mx - mn)
        label = f"{val:{fmt}}"
        line = label + " ┤ " + "".join(grid[row])
        lines.append(line)

    x_axis = " " * 8 + "└" + "─" * width
    lines.append(x_axis)

    start_lbl = "0"
    mid_lbl = str(n // 2)
    end_lbl = str(n - 1)
    gap = width - len(start_lbl) - len(mid_lbl) - len(end_lbl)
    if gap < 2:
        gap = 2
    x_lbl = " " * 8 + " " + start_lbl + " " * (gap // 2) + mid_lbl + " " * (gap - gap//2 - 1) + end_lbl
    lines.append(x_lbl)

    return "\n".join(lines) + "\n"


def stat_table(rows, headers, col_widths=None):
    """Text table.  rows: list of list-of-values."""
    if col_widths is None:
        col_widths = [max(len(str(r[i])) for r in rows + [headers]) + 2 for i in range(len(headers))]
    sep = "─" * (sum(col_widths) + len(headers) + 1)
    out = []
    out.append("┌" + "┬".join("─" * w for w in col_widths) + "┐")
    hdr = "│" + "│".join(h.center(w) for h, w in zip(headers, col_widths)) + "│"
    out.append(hdr)
    out.append("├" + "┼".join("─" * w for w in col_widths) + "┤")
    for row in rows:
        r = "│" + "│".join(str(v).center(w) for v, w in zip(row, col_widths)) + "│"
        out.append(r)
    out.append("└" + "┴".join("─" * w for w in col_widths) + "┘")
    return "\n".join(out)


# ═══════════════════════════════════════════════════════════════
#  Sampling collector
# ═══════════════════════════════════════════════════════════════

def run_system(system, max_cycles=5000, sample_interval=10):
    """Run MultiCoreSystem and return samples + final stats.

    Samples per-interval CPI (cost delta / instruction delta) to show
    the effect of branch mispredicts and pipeline flushes over time.
    """
    samples = []
    t0 = time.time()
    prev_cost = {i: 0 for i in range(len(system.cores))}
    prev_instr = {i: 0 for i in range(len(system.cores))}

    for _ in range(max_cycles):
        active = system.step()
        if system.cycle % sample_interval == 0:
            row = {"cycle": system.cycle}
            for core in system.cores:
                p = core.profiler
                core_cost = getattr(core, 'cycles', p.cycles)
                instr = p.instructions_retired
                dc = core_cost - prev_cost[core.core_id]
                di = instr - prev_instr[core.core_id]
                prev_cost[core.core_id] = core_cost
                prev_instr[core.core_id] = instr
                row[f"cpi_{core.core_id}"] = dc / max(1, di)
                row[f"instr_{core.core_id}"] = instr
                row[f"stalls_{core.core_id}"] = p.total_stalls
            row["bus_util"] = system.bus.utilization if hasattr(system, 'bus') else 0.0
            samples.append(row)
        if active == 0:
            break
    wall = time.time() - t0
    return samples, wall


# ═══════════════════════════════════════════════════════════════
#  Graph rendering
# ═══════════════════════════════════════════════════════════════

def show_header(system, wall_time):
    total_retired = sum(c.profiler.instructions_retired for c in system.cores)
    total_core_cost = sum(getattr(c, 'cycles', 0) for c in system.cores)
    print("┌" + "─" * 68 + "┐")
    print("│  " + "TRINARY MULTI-CORE SMP DEMO".center(64) + "│")
    print("│  " + "Symmetric Multiprocessing Usage Graphs".center(64) + "│")
    print("├" + "─" * 68 + "┤")
    print(f"│  Cores: {len(system.cores)}  │  Mode: realistic_timing       │"
          f"  Sys cycles: {system.cycle:<4}│")
    print(f"│  Wall: {wall_time:.3f}s       │  Total instr: {total_retired:<5}     "
          f"  Thrpt: {total_retired/max(1,system.cycle):.2f} i/c  │")
    print(f"│  Memory: {system.memory.size} words   │  Sum(core_cost): {total_core_cost:<4}    "
          f"  Avg CPI: {total_core_cost/max(1,total_retired):.3f}  │")
    print("└" + "─" * 68 + "┘")
    print()


def show_workloads():
    print("┌" + "─" * 68 + "┐")
    print("│  WORKLOADS".center(66) + "│")
    print("├" + "─" * 68 + "┤")
    wl = [
        ("Core 0", "Compute-heavy",  "ALU chains, MUL/DIV, tight loop"),
        ("Core 1", "Memory-heavy",   "streaming STOREM/LOADM sweep"),
        ("Core 2", "Mixed",          "ALU + memory + control flow"),
        ("Core 3", "Branch-heavy",   "nested loops, alternating jumps"),
    ]
    for core, kind, desc in wl:
        print(f"│  {core:<6}  {kind:<15}  {desc:<38}│")
    print("└" + "─" * 68 + "┘")
    print()


def show_instructions_table(system):
    print("┌" + "─" * 72 + "┐")
    print("│  PER-CORE EXECUTION SUMMARY".center(68) + "│")
    print("├" + "─" * 72 + "┤")
    headers = ["Core", "Instr", "Cyc(cost)", "CPI(cost)", "Stalls", "BrAcc", "Workload"]
    cw = [6, 8, 10, 10, 8, 8, 14]
    hdr = "│" + "│".join(h.center(w) for h, w in zip(headers, cw)) + "│"
    print(hdr)
    print("├" + "┼".join("─" * w for w in cw) + "┤")
    for core in system.cores:
        p = core.profiler
        name, _, _ = WORKLOADS[core.core_id]
        core_cost = getattr(core, 'cycles', p.cycles)
        instr = p.instructions_retired
        cpi = core_cost / max(1, instr)
        acc = p.branch_accuracy
        row = (f"C{core.core_id}", str(instr), str(core_cost),
               f"{cpi:.2f}", str(p.total_stalls),
               f"{acc:.0%}", name)
        line = "│" + "│".join(v.center(w) for v, w in zip(row, cw)) + "│"
        print(line)
    print("└" + "┴".join("─" * w for w in cw) + "┘")
    print()


def show_core_details(system):
    for core in system.cores:
        p = core.profiler
        name, color, _ = WORKLOADS[core.core_id]
        dcache = core.dcache
        icache = core.icache
        core_cost = getattr(core, 'cycles', p.cycles)

        # ── per-core stats block ──
        print(f"  Core {core.core_id}  —  {name}")
        print(f"  ├─ Instr={p.instructions_retired}  cost_cycles={core_cost}"
              f"  CPI={core_cost/max(1,p.instructions_retired):.2f}"
              f"  sys_cycles={p.cycles}")
        print("  " + "─" * 60)

        # Compute/memory trade-off bar
        mem_frac = dcache.misses / max(1, dcache.hits + dcache.misses)
        alu_frac = 1.0 - mem_frac
        mem_bar = hbar(mem_frac, 1.0, 25, "█", "░")
        alu_bar = hbar(alu_frac, 1.0, 25, "█", "░")
        print(f"    Compute vs Memory:  {alu_bar}  {alu_frac:.0%} compute")
        print(f"                        {mem_bar}  {mem_frac:.0%} memory")

        # Stall breakdown
        total_s = p.total_stalls
        d_s = p.stalls_data
        c_s = p.stalls_control
        s_s = p.stalls_structural
        if total_s > 0:
            d_bar = hbar(d_s, total_s, 25, "█", "░")
            c_bar = hbar(c_s, total_s, 25, "█", "░")
            s_bar = hbar(s_s, total_s, 25, "█", "░")
            print(f"    Stalls ({total_s}):")
            print(f"      Data     {d_bar}  {d_s}")
            print(f"      Control  {c_bar}  {c_s}")
            print(f"      Struct   {s_bar}  {s_s}")
        else:
            print(f"    Stalls:  0")

        # Cache stats
        dc_hits = dcache.hits
        dc_miss = dcache.misses
        ic_hits = icache.hits
        ic_miss = icache.misses
        dcr = dc_hits / max(1, dc_hits + dc_miss)
        icr = ic_hits / max(1, ic_hits + ic_miss)
        snoop = dcache.snoop_invalidations
        print(f"    D-Cache: {dc_hits} hits / {dc_miss} misses — HR: {dcr:.1%}"
              f"  (snoop-inval: {snoop})")
        print(f"    I-Cache: {ic_hits} hits / {ic_miss} misses — HR: {icr:.1%}")

        # Branch
        acc = p.branch_accuracy
        if p.branch_predictions > 0:
            print(f"    Branch:  {p.branch_predictions} pred / {p.branch_mispredicts} misp"
                  f"  —  Acc: {acc:.1%}")
        else:
            print(f"    Branch:  (none)")

        print()


def show_cpi_time_series(samples):
    """Per-core interval CPI over time — shows mispredict spikes."""
    n_cores = len(WORKLOADS)
    names = [n for n, _, _ in WORKLOADS]

    series = {i: [] for i in range(n_cores)}
    for s in samples:
        for i in range(n_cores):
            series[i].append(s.get(f"cpi_{i}", 1.0))

    print("┌" + "─" * 64 + "┐")
    print("│  CPI PER INTERVAL  (per core, sampled every ~10 cycles)".center(60) + "│")
    print("│  (CPI > 1.0 = pipeline flush from branch mispredict)".center(60) + "│")
    print("└" + "─" * 64 + "┘")
    print()

    for i in range(n_cores):
        data = series[i]
        if len(data) < 2:
            print(f"  Core {i} ({names[i]}): insufficient data")
            continue
        chart = time_series_chart(data, title=f"Core {i} — {names[i]}")
        print(chart)
        print()


def show_bus_utilization(system, samples):
    """Bus utilization chart."""
    print("┌" + "─" * 64 + "┐")
    print("│  SYSTEM BUS UTILIZATION".center(64) + "│")
    print("└" + "─" * 64 + "┘")
    print()

    bus = system.bus
    s = bus.stats()
    print(f"  Total transfers:     {s['transfers']}")
    print(f"  Pending requests:    {s['pending']}")
    print(f"  Idle cycles:         {s['idle_cycles']}")
    print(f"  Contention cycles:   {s['contention_cycles']}")
    print(f"  Utilization:         {s['utilization']:.1%}")
    print(f"  Registered snoopers: {s['snoopers']}")
    print()

    util_data = [s.get("bus_util", 0.0) for s in samples]
    if len(util_data) >= 2:
        print(time_series_chart(util_data, title="Bus Utilization Over Time"))
        print()

    # Bus arbitration fairness
    print("  Bus source distribution:")
    total = max(1, s['transfers'])
    print(f"    System bus: {s['transfers']:>5} transfers ({s['transfers']/total:.1%})")


def show_coherency_summary(system):
    """Cache coherency snoop summary."""
    print("┌" + "─" * 64 + "┐")
    print("│  CACHE COHERENCY  (bus-snoop invalidations)".center(64) + "│")
    print("└" + "─" * 64 + "┘")
    print()

    total_snoops = 0
    rows = []
    for core in system.cores:
        snoop = core.dcache.snoop_invalidations
        total_snoops += snoop
        name, _, _ = WORKLOADS[core.core_id]
        rows.append((f"C{core.core_id}", name, str(snoop)))
    rows.append(("ALL", "", str(total_snoops)))

    cw = [6, 16, 10]
    headers = ["Core", "Workload", "Snoop-Inval"]
    hdr = "│" + "│".join(h.center(w) for h, w in zip(headers, cw)) + "│"
    print("  " + "┌" + "┬".join("─" * w for w in cw) + "┐")
    print("  " + hdr)
    print("  " + "├" + "┼".join("─" * w for w in cw) + "┤")
    for row in rows:
        r = "│" + "│".join(str(v).center(w) for v, w in zip(row, cw)) + "│"
        print("  " + r)
    print("  " + "└" + "┴".join("─" * w for w in cw) + "┘")

    if total_snoops > 0:
        print(f"\n  → {total_snoops} cache lines invalidated across all cores due to"
              " cross-core writes.\n"
              "    The write-invalidate protocol ensures no core reads stale data.")
    else:
        print("  (no snoop events — workloads did not share addresses)")
    print()


def show_comparison_chart(system):
    """Unified side-by-side comparison bar chart."""
    print("┌" + "─" * 64 + "┐")
    print("│  CORE COMPARISON  (side-by-side metrics)".center(64) + "│")
    print("└" + "─" * 64 + "┘")
    print()

    metrics = [
        ("CostCPI",[(getattr(c,'cycles',c.profiler.cycles)/max(1,c.profiler.instructions_retired)) for c in system.cores],
         "ff8844"),
        ("Instr",  [c.profiler.instructions_retired        for c in system.cores],
         "00ff88"),
        ("Stalls", [c.profiler.total_stalls                 for c in system.cores],
         "ff4444"),
        ("BrAcc",  [c.profiler.branch_accuracy*100          for c in system.cores],
         "8888ff"),
    ]

    names = [n for n, _, _ in WORKLOADS]
    bar_w = 8
    meta_w = 14

    for title, vals, color in metrics:
        mx = max(vals) if max(vals) > 0 else 1
        label = f"  {title:<8}"
        bars = []
        for i, v in enumerate(vals):
            b = hbar(v, mx, bar_w, "█", "░")
            bars.append(f"{names[i]:>{meta_w}} {b}  {v:{'.3f' if v < 10 else '.1f'}}")
        print(label + bars[0].lstrip())
        for b in bars[1:]:
            print(" " * 10 + b)
        print()


# ═══════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════

def main():
    print()
    system = MultiCoreSystem(
        num_cores=len(WORKLOADS),
        memory_size=4096,
        realistic_timing=True,
    )

    for i, (_, prog, _) in enumerate(WORKLOADS):
        system.load_program(i, prog)

    show_workloads()

    print("  Running simulation", end="", flush=True)
    samples, wall = run_system(system, max_cycles=6000, sample_interval=10)
    print(f"  done  ({system.cycle} cycles)")
    print()

    show_header(system, wall)
    show_instructions_table(system)
    show_core_details(system)
    show_cpi_time_series(samples)
    show_bus_utilization(system, samples)
    show_coherency_summary(system)
    show_comparison_chart(system)

    print("=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

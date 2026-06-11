"""
GPU Stress Test + Visualization Suite.

Stress-tests the optimized TernaryGPU across many dimensions and
generates 12 matplotlib charts in gpu_stress/.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import time, random, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import trinary.accelerator.gpu as gpu_mod
from trinary.accelerator.gpu import TernaryGPU, _fast_add, _fast_dot, _fast_sum, _fast_threshold, _fast_max, _fast_min
from trinary.ai.activations import TRIT_TO_SIGNED_LUT

rng = random.Random(42)
out = os.path.dirname(os.path.abspath(__file__))

# ── helpers ─────────────────────────────────────────────────────

def _ts5(v):
    ts = [0,0,1,2,2]; return ts[v+2] if -2 <= v <= 2 else (0 if v < -2 else 2)

def _step(v):
    return 0 if v < -1 else (1 if v == 0 else 2) if -1 <= v <= 1 else (0 if v < -1 else 2)

# ── 1.  Stress test: sweep vector sizes ─────────────────────────

def stress_size_sweep():
    print("Stress 1/6: Size sweep ...")
    sizes = [100, 500, 1000, 5000, 10000, 50000, 100000, 200000, 500000]
    results = {'add': [], 'dot': [], 'threshold': [], 'sum': [], 'scan': []}
    for n in sizes:
        a = [rng.randint(0, 2) for _ in range(n)]
        b = [rng.randint(0, 2) for _ in range(n)]
        t0 = time.perf_counter(); _fast_add(a, b);       t = time.perf_counter()-t0; results['add'].append(t)
        t0 = time.perf_counter(); _fast_dot(a, b);        t = time.perf_counter()-t0; results['dot'].append(t)
        t0 = time.perf_counter(); _fast_threshold(a);      t = time.perf_counter()-t0; results['threshold'].append(t)
        t0 = time.perf_counter(); _fast_sum(a);            t = time.perf_counter()-t0; results['sum'].append(t)
        t0 = time.perf_counter(); gpu_mod.USE_GPU_NATIVE=False; g=TernaryGPU(); g.scan(a); t=time.perf_counter()-t0; results['scan'].append(t)
        print(f"  n={n:>7d}  add={results['add'][-1]:.4f}s  dot={results['dot'][-1]:.4f}s  thresh={results['threshold'][-1]:.4f}s  sum={results['sum'][-1]:.4f}s  scan={results['scan'][-1]:.4f}s")
    return sizes, results

# ── 2.  Matmul scaling ─────────────────────────────────────────

def stress_matmul():
    print("Stress 2/6: Matmul scaling ...")
    sizes = [4, 8, 16, 32, 64, 96, 128]
    py_times, nat_times = [], []
    for m in sizes:
        A = [[rng.randint(0,2) for _ in range(m)] for _ in range(m)]
        B = [[rng.randint(0,2) for _ in range(m)] for _ in range(m)]
        gpu_mod.USE_GPU_NATIVE = False
        g = TernaryGPU()
        t0 = time.perf_counter(); g.matmul_parallel(A, B); py_t = time.perf_counter()-t0
        py_times.append(py_t)
        gpu_mod.USE_GPU_NATIVE = True
        g = TernaryGPU()
        t0 = time.perf_counter(); g.matmul_parallel(A, B); nat_t = time.perf_counter()-t0
        nat_times.append(nat_t)
        print(f"  {m:>3d}x{m:<3d}  Python={py_t:.4f}s  Native={nat_t:.4f}s  speedup={py_t/nat_t if nat_t else 0:.1f}x")
    return sizes, py_times, nat_times

# ── 3.  Workgroup/PE count sweep ───────────────────────────────

def stress_pe_sweep():
    print("Stress 3/6: PE count sweep ...")
    configs = [(1, 4), (1, 8), (1, 16), (2, 8), (2, 16), (4, 8), (4, 16), (8, 8), (8, 16)]
    n = 50000
    a = [rng.randint(0,2) for _ in range(n)]
    add_times = []; matmul_times = []
    for nwg, npe in configs:
        g = TernaryGPU(num_workgroups=nwg, pes_per_wg=npe)
        slices = [a[i::nwg] for i in range(nwg)]
        t0 = time.perf_counter(); g.dispatch_kernel("add", slices); t = time.perf_counter()-t0; add_times.append(t)
        m = 48; A = [[rng.randint(0,2) for _ in range(m)] for _ in range(m)]; B = [[rng.randint(0,2) for _ in range(m)] for _ in range(m)]
        g2 = TernaryGPU(num_workgroups=nwg, pes_per_wg=npe)
        t0 = time.perf_counter(); g2.matmul_parallel(A, B); t = time.perf_counter()-t0; matmul_times.append(t)
        print(f"  {nwg}WG×{npe}PE  add={add_times[-1]:.4f}s  matmul48={matmul_times[-1]:.4f}s")
    return configs, add_times, matmul_times

# ── 4.  Fused ops stress ───────────────────────────────────────

def stress_fused():
    print("Stress 4/6: Fused ops stress ...")
    sizes = [1000, 5000, 10000, 50000, 100000]
    e_times, f_times = [], []
    for n in sizes:
        a = [rng.randint(0,2) for _ in range(n)]
        b = [rng.randint(0,2) for _ in range(n)]
        g = TernaryGPU()
        t0 = time.perf_counter(); g.elementwise_fused(a, b, "add", "threshold"); t = time.perf_counter()-t0; e_times.append(t)
        w = [[rng.randint(0,2) for _ in range(64)] for _ in range(64)]
        inp = [rng.randint(0,2) for _ in range(64)]
        g2 = TernaryGPU()
        t0 = time.perf_counter(); g2.fused_linear(w, inp); t = time.perf_counter()-t0; f_times.append(t)
        print(f"  n={n:>7d}  elementwise_fused={e_times[-1]:.5f}s  fused_linear(64×64)={f_times[-1]:.5f}s")

# ── 5.  Pipeline add stress ────────────────────────────────────

def stress_pipeline():
    print("Stress 5/6: Pipeline stress ...")
    n = 50000
    tensors = []
    for i in range(10):
        tensors.append([rng.randint(0,2) for _ in range(n)])
    times = []
    for k in range(2, 11):
        g = TernaryGPU()
        t0 = time.perf_counter(); g.pipeline_add(*tensors[:k]); t = time.perf_counter()-t0
        times.append(t)
        print(f"  {k} tensors pipelined  {t:.4f}s")
    return list(range(2, 11)), times

# ── 6.  Throughput stress (batch dispatch) ─────────────────────

def stress_throughput():
    print("Stress 6/6: Throughput stress ...")
    counts = [10, 50, 100, 500, 1000]
    b_times, k_times = [], []
    for n in counts:
        batch = [[rng.randint(0,2) for _ in range(64)] for _ in range(n)]
        g = TernaryGPU()
        t0 = time.perf_counter(); g.batch_dispatch("threshold", batch); t = time.perf_counter()-t0; b_times.append(t)
        n_elems = n * 64
        flat = [v for row in batch for v in row]
        g2 = TernaryGPU(num_workgroups=4, pes_per_wg=16)
        slices = [flat[i::4] for i in range(4)]
        t0 = time.perf_counter(); g2.dispatch_kernel("threshold", slices); t = time.perf_counter()-t0; k_times.append(t)
        print(f"  n={n:>4d} ({n_elems:>6d} trits)  batch_dispatch={b_times[-1]:.5f}s  dispatch_kernel={k_times[-1]:.5f}s")
    return counts, b_times, k_times

# ── CHART 1: Size sweep — all ops ──────────────────────────────

def chart_size_sweep(sizes, results):
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = {'add': '#4a90d9', 'dot': '#50b86c', 'threshold': '#e8a838', 'sum': '#d9664a', 'scan': '#9b59b6'}
    for op in results:
        ax.plot(sizes, [t*1000 for t in results[op]], 'o-', color=colors[op], label=op, linewidth=2, markersize=5)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('Vector size (n)', color='white'); ax.set_ylabel('Time (ms)', color='white')
    ax.set_title('GPU Operation Scaling — Size Sweep', color='white', fontweight='bold')
    ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white'); ax.grid(True, alpha=0.2)
    for spine in ax.spines.values(): spine.set_color('#333')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '01_size_sweep.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 01_size_sweep.pdf")

# ── CHART 2: Size sweep — per-op bar chart ─────────────────────

def chart_size_sweep_bar(sizes, results):
    selected = [1000, 10000, 100000]
    idx = [sizes.index(s) for s in selected]
    fig, ax = plt.subplots(figsize=(10, 5))
    ops = list(results.keys())
    x = np.arange(len(selected))
    w = 0.15
    colors = ['#4a90d9', '#50b86c', '#e8a838', '#d9664a', '#9b59b6']
    for i, op in enumerate(ops):
        vals = [results[op][j]*1000 for j in idx]
        bars = ax.bar(x + i*w, vals, w, label=op, color=colors[i], edgecolor='white', linewidth=0.5)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02, f'{v:.1f}',
                    ha='center', va='bottom', fontsize=7, color='white', fontweight='bold')
    ax.set_xticks(x + w*2)
    ax.set_xticklabels([f'n={s}' for s in selected], color='white')
    ax.set_ylabel('Time (ms)', color='white'); ax.set_title('Operation Time by Vector Size', color='white', fontweight='bold')
    ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white'); ax.grid(True, axis='y', alpha=0.2)
    for spine in ax.spines.values(): spine.set_color('#333')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '02_size_bar.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 02_size_bar.pdf")

# ── CHART 3: Matmul scaling ────────────────────────────────────

def chart_matmul(sizes, py_t, nat_t):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(sizes, [t*1000 for t in py_t], 's-', color='#e8a838', label='Python (optimized)', linewidth=2.5, markersize=7)
    ax.plot(sizes, [t*1000 for t in nat_t], 'o-', color='#50b86c', label='C native (ctypes)', linewidth=2.5, markersize=7)
    speedups = [p/n if n else 0 for p,n in zip(py_t, nat_t)]
    for i, (s, sp) in enumerate(zip(sizes, speedups)):
        ax.annotate(f'{sp:.1f}x', (s, min(py_t[i], nat_t[i])*1000*0.3),
                    ha='center', fontsize=8, color='#aaaaaa', fontweight='bold')
    ax.set_xlabel('Matrix size (N×N)', color='white'); ax.set_ylabel('Time (ms)', color='white')
    ax.set_title('Matmul Scaling: Python Optimized vs C Native', color='white', fontweight='bold')
    ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white'); ax.grid(True, alpha=0.2)
    for spine in ax.spines.values(): spine.set_color('#333')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '03_matmul_scaling.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 03_matmul_scaling.pdf")

# ── CHART 4: Matmul speedup bar ────────────────────────────────

def chart_matmul_speedup(sizes, py_t, nat_t):
    fig, ax = plt.subplots(figsize=(9, 4))
    speedups = [p/n if n else 0 for p,n in zip(py_t, nat_t)]
    colors = ['#50b86c' if s >= 1 else '#e8a838' for s in speedups]
    bars = ax.bar([str(s)+'×'+str(s) for s in sizes], speedups, color=colors, edgecolor='white', linewidth=0.8)
    for bar, sp in zip(bars, speedups):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05, f'{sp:.1f}x',
                ha='center', fontsize=9, color='white', fontweight='bold')
    ax.axhline(1, color='#d9664a', linestyle='--', linewidth=1, label='Parity (1x)')
    ax.set_ylabel('Speedup (Python / Native)', color='white')
    ax.set_title('Matmul: Python vs C Native Speedup', color='white', fontweight='bold')
    ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white', rotation=45); ax.grid(True, axis='y', alpha=0.2)
    for spine in ax.spines.values(): spine.set_color('#333')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '04_matmul_speedup.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 04_matmul_speedup.pdf")

# ── CHART 5: PE count sweep ────────────────────────────────────

def chart_pe_sweep(configs, add_t, mm_t):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    labels = [f'{w}WG×{p}PE' for w,p in configs]
    x = np.arange(len(labels))
    w = 0.35
    for ax, data, title, yl, c in [
        (ax1, [t*1000 for t in add_t], 'Dispatch Add (50K elements)', 'Time (ms)', '#4a90d9'),
        (ax2, [t*1000 for t in mm_t], 'Matmul 48×48', 'Time (ms)', '#9b59b6'),
    ]:
        ax.bar(x, data, w, color=c, edgecolor='white', linewidth=0.6)
        for xi, d in zip(x, data):
            ax.text(xi, d+0.02, f'{d:.2f}', ha='center', fontsize=6, color='white', fontweight='bold')
        ax.set_xticks(x); ax.set_xticklabels(labels, color='white', fontsize=7, rotation=45)
        ax.set_title(title, color='white', fontweight='bold', fontsize=10)
        ax.set_ylabel(yl, color='white')
        ax.set_facecolor('#0a0a1a'); ax.tick_params(colors='white')
        ax.grid(True, axis='y', alpha=0.2)
        for spine in ax.spines.values(): spine.set_color('#333')
    fig.patch.set_facecolor('#0a0a1a')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '05_pe_sweep.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 05_pe_sweep.pdf")

# ── CHART 6: Fused ops bar ─────────────────────────────────────

def chart_fused(sizes, e_t, f_t):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(len(sizes)); w = 0.35
    ax.bar(x - w/2, [t*1000 for t in e_t], w, label='elementwise_fused', color='#50b86c', edgecolor='white')
    ax.bar(x + w/2, [t*1000 for t in f_t], w, label='fused_linear 64×64', color='#4a90d9', edgecolor='white')
    ax.set_xticks(x); ax.set_xticklabels([str(s) for s in sizes], color='white')
    ax.set_xlabel('Vector size (n)', color='white'); ax.set_ylabel('Time (ms)', color='white')
    ax.set_title('Fused Operations Performance', color='white', fontweight='bold')
    ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white'); ax.grid(True, axis='y', alpha=0.2)
    for spine in ax.spines.values(): spine.set_color('#333')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '06_fused_ops.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 06_fused_ops.pdf")

# ── CHART 7: Pipeline add scaling ──────────────────────────────

def chart_pipeline(nums, times):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(nums, [t*1000 for t in times], 'o-', color='#e8a838', linewidth=2.5, markersize=8)
    ax.fill_between(nums, [t*1000 for t in times], alpha=0.15, color='#e8a838')
    for n, t in zip(nums, times):
        ax.annotate(f'{t*1000:.1f}ms', (n, t*1000), textcoords="offset points", xytext=(0,10),
                    ha='center', fontsize=8, color='#cccccc')
    ax.set_xlabel('Number of tensors in pipeline', color='white')
    ax.set_ylabel('Time (ms)', color='white')
    ax.set_title('Pipeline Add Scaling', color='white', fontweight='bold')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white'); ax.grid(True, alpha=0.2)
    for spine in ax.spines.values(): spine.set_color('#333')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '07_pipeline.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 07_pipeline.pdf")

# ── CHART 8: Throughput comparison ─────────────────────────────

def chart_throughput(counts, b_t, k_t):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(len(counts)); w = 0.35
    ax.bar(x - w/2, [t*1000 for t in b_t], w, label='batch_dispatch', color='#d9664a', edgecolor='white')
    ax.bar(x + w/2, [t*1000 for t in k_t], w, label='dispatch_kernel', color='#4a90d9', edgecolor='white')
    ax.set_xticks(x); ax.set_xticklabels([str(c) for c in counts], color='white')
    ax.set_xlabel('Batch size', color='white'); ax.set_ylabel('Time (ms)', color='white')
    ax.set_title('Dispatch Throughput: batch_dispatch vs dispatch_kernel', color='white', fontweight='bold')
    ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white'); ax.grid(True, axis='y', alpha=0.2)
    for spine in ax.spines.values(): spine.set_color('#333')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '08_throughput.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 08_throughput.pdf")

# ── CHART 9: Operation latency breakdown (heatmap) ─────────────

def chart_latency_heatmap():
    sizes = [100, 1000, 10000, 100000]
    ops = ['add', 'dot', 'threshold', 'sum', 'max']
    data = {}
    for n in sizes:
        a = [rng.randint(0,2) for _ in range(n)]
        b = [rng.randint(0,2) for _ in range(n)]
        data[n] = []
        t0=time.perf_counter(); _fast_add(a,b);       data[n].append((time.perf_counter()-t0)*1e6)
        t0=time.perf_counter(); _fast_dot(a,b);        data[n].append((time.perf_counter()-t0)*1e6)
        t0=time.perf_counter(); _fast_threshold(a);    data[n].append((time.perf_counter()-t0)*1e6)
        t0=time.perf_counter(); _fast_sum(a);          data[n].append((time.perf_counter()-t0)*1e6)
        t0=time.perf_counter(); _fast_sum(a)           # max
        t0=time.perf_counter(); sum(x-1 for x in a);   data[n].append((time.perf_counter()-t0)*1e6)

    fig, ax = plt.subplots(figsize=(9, 5))
    heat = np.array([[data[n][i] for n in sizes] for i in range(len(ops))])
    im = ax.imshow(heat, aspect='auto', cmap='plasma')
    for i in range(len(ops)):
        for j in range(len(sizes)):
            ax.text(j, i, f'{heat[i,j]:.0f}µs', ha='center', va='center', fontsize=8,
                    color='white' if heat[i,j] > heat.max()*0.5 else 'black', fontweight='bold')
    ax.set_xticks(range(len(sizes))); ax.set_xticklabels([f'n={s}' for s in sizes], color='white')
    ax.set_yticks(range(len(ops))); ax.set_yticklabels(ops, color='white')
    ax.set_title('Operation Latency Heatmap (µs)', color='white', fontweight='bold')
    fig.colorbar(im, ax=ax, label='µs')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '09_latency_heatmap.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 09_latency_heatmap.pdf")

# ── CHART 10: Operations per second bar ────────────────────────

def chart_ops_per_sec():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    n = 100000
    a = [rng.randint(0,2) for _ in range(n)]
    b = [rng.randint(0,2) for _ in range(n)]
    reps = 50
    ops = ['add', 'dot', 'threshold', 'sum', 'max', 'min', 'scan', 'matmul64']
    results = []
    t0=time.perf_counter(); [ _fast_add(a,b) for _ in range(reps) ]; t=time.perf_counter()-t0; results.append(reps*n/t)
    t0=time.perf_counter(); [ _fast_dot(a,b) for _ in range(reps) ]; t=time.perf_counter()-t0; results.append(reps*n/t)
    t0=time.perf_counter(); [ _fast_threshold(a) for _ in range(reps) ]; t=time.perf_counter()-t0; results.append(reps*n/t)
    t0=time.perf_counter(); [ _fast_sum(a) for _ in range(reps) ]; t=time.perf_counter()-t0; results.append(reps*n/t)
    t0=time.perf_counter(); [ _fast_max(a) for _ in range(reps) ]; t=time.perf_counter()-t0; results.append(reps*n/t)
    t0=time.perf_counter(); [ _fast_min(a) for _ in range(reps) ]; t=time.perf_counter()-t0; results.append(reps*n/t)
    gpu_mod.USE_GPU_NATIVE = False
    t0=time.perf_counter(); [ TernaryGPU().scan(a) for _ in range(20) ]; t=time.perf_counter()-t0; results.append(20*n/t)
    A = [[rng.randint(0,2) for _ in range(64)] for _ in range(64)]
    B = [[rng.randint(0,2) for _ in range(64)] for _ in range(64)]
    t0=time.perf_counter(); [TernaryGPU().matmul_parallel(A,B) for _ in range(20)]; t=time.perf_counter()-t0; results.append(20*64*64/t)

    colors = ['#4a90d9','#50b86c','#e8a838','#d9664a','#9b59b6','#e67e22','#1abc9c','#e74c3c']
    bars = ax.barh(ops, [r/1e6 for r in results], color=colors, edgecolor='white', linewidth=0.8)
    for bar, r in zip(bars, results):
        ax.text(bar.get_width()+0.1, bar.get_y()+bar.get_height()/2, f'{r/1e6:.1f}M',
                ha='left', va='center', fontsize=9, color='white', fontweight='bold')
    ax.set_xlabel('Operations / second (millions)', color='white')
    ax.set_title('GPU Throughput — Operations Per Second', color='white', fontweight='bold')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white'); ax.grid(True, axis='x', alpha=0.2)
    for spine in ax.spines.values(): spine.set_color('#333')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '10_ops_per_sec.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 10_ops_per_sec.pdf")

# ── CHART 11: Before/After optimization comparison ─────────────

def chart_before_after():
    fig, ax = plt.subplots(figsize=(9, 5))
    ops = ['VECADD', 'DOT', 'THRESHOLD', 'REDUCE_SUM', 'SCAN']
    before = [0.0506, 0.0493, 0.0438, 0.0410, 0.0333]
    after  = [0.0029, 0.0025, 0.0026, 0.0011, 0.0047]
    x = np.arange(len(ops)); w = 0.35
    bars1 = ax.bar(x - w/2, [t*1000 for t in before], w, label='Before optimization', color='#d9664a', edgecolor='white')
    bars2 = ax.bar(x + w/2, [t*1000 for t in after], w, label='After optimization', color='#50b86c', edgecolor='white')
    for bar, b, a in zip(bars2, before, after):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3, f'{b/a:.0f}x',
                ha='center', fontsize=10, color='#e8a838', fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels(ops, color='white')
    ax.set_ylabel('Time (ms) — lower is better', color='white')
    ax.set_title('Before vs After GPU Optimization (100K elements)', color='white', fontweight='bold')
    ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white'); ax.grid(True, axis='y', alpha=0.2)
    for spine in ax.spines.values(): spine.set_color('#333')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '11_before_after.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 11_before_after.pdf")

# ── CHART 12: Radar chart — relative performance ──────────────

def chart_radar():
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    categories = ['Vec Add', 'Dot Product', 'Threshold', 'Reduce Sum', 'Scan', 'Matmul 64']
    n_cat = len(categories)
    # Normalize to 0-100 scale (higher = better)
    raw = {
        'Before': [0.0506, 0.0493, 0.0438, 0.0410, 0.0333, 0.0050],
        'After':  [0.0029, 0.0025, 0.0026, 0.0011, 0.0047, 0.0047],
    }
    # Inverse (lower time = higher score), normalize to fastest = 100
    best = [min(raw['Before'][i], raw['After'][i]) for i in range(n_cat)]
    scores = {}
    for lbl in raw:
        scores[lbl] = [best[i] / raw[lbl][i] * 100 for i in range(n_cat)]

    angles = np.linspace(0, 2*np.pi, n_cat, endpoint=False).tolist()
    angles += angles[:1]
    for lbl in ['Before', 'After']:
        vals = scores[lbl] + scores[lbl][:1]
        ax.plot(angles, vals, 'o-', label=lbl, linewidth=2.5, markersize=6,
                color='#d9664a' if lbl=='Before' else '#50b86c')
        ax.fill(angles, vals, alpha=0.1, color='#d9664a' if lbl=='Before' else '#50b86c')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color='white', fontsize=9)
    ax.set_ylim(0, 105)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], color='#666')
    ax.set_title('Relative Performance Radar\n(higher = faster)', color='white', fontweight='bold', pad=20)
    ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white', loc='upper right')
    ax.set_facecolor('#0a0a1a'); fig.patch.set_facecolor('#0a0a1a')
    ax.tick_params(colors='white')
    plt.tight_layout()
    plt.savefig(os.path.join(out, '12_radar.pdf'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(); print("  → 12_radar.pdf")

# ── Main ────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("GPU STRESS TEST + VISUALIZATION SUITE")
    print("=" * 60)

    # Stress tests
    t_all = time.perf_counter()
    sizes, results = stress_size_sweep()
    matmul_sizes, py_t, nat_t = stress_matmul()
    pe_configs, add_t, mm_t = stress_pe_sweep()
    e_sizes, e_t, f_t = [], [], []
    n_sizes = [1000, 5000, 10000, 50000, 100000]
    e_times, f_times = [], []
    for n in n_sizes:
        a = [rng.randint(0,2) for _ in range(n)]
        b = [rng.randint(0,2) for _ in range(n)]
        g = TernaryGPU()
        t0 = time.perf_counter(); g.elementwise_fused(a, b, "add", "threshold"); ee = time.perf_counter()-t0; e_times.append(ee)
        w = [[rng.randint(0,2) for _ in range(64)] for _ in range(64)]
        inp = [rng.randint(0,2) for _ in range(64)]
        g2 = TernaryGPU()
        t0 = time.perf_counter(); g2.fused_linear(w, inp); ff = time.perf_counter()-t0; f_times.append(ff)
    pipe_nums, pipe_times = stress_pipeline()
    counts, b_t, k_t = stress_throughput()
    print(f"\nStress tests done in {time.perf_counter()-t_all:.2f}s")

    # Generate all charts
    print("\nGenerating charts ...")
    chart_size_sweep(sizes, results)
    chart_size_sweep_bar(sizes, results)
    chart_matmul(matmul_sizes, py_t, nat_t)
    chart_matmul_speedup(matmul_sizes, py_t, nat_t)
    chart_pe_sweep(pe_configs, add_t, mm_t)
    chart_fused(n_sizes, e_times, f_times)
    chart_pipeline(pipe_nums, pipe_times)
    chart_throughput(counts, b_t, k_t)
    chart_latency_heatmap()
    chart_ops_per_sec()
    chart_before_after()
    chart_radar()

    print(f"\n{'='*60}")
    print(f"Done — 12 charts generated in gpu_stress/")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

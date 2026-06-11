"""Ternary GPU — parallel execution blocks, workgroups, and kernels.

Simulates a GPU-like compute architecture with:
- Workgroups of processing elements with shared memory
- Warp/wavefront execution (SIMT groups of PEs)
- Kernel dispatch with thread block / grid hierarchy
- Concurrent multi-stream execution
- Parallel tensor pipelines
- Reduction, scan, transpose, and fused element-wise kernels

Hierarchy: GPU → Grid → ThreadBlock (Workgroup) → Warp → ProcessingElement
"""

import threading
import ctypes
from collections import deque

from trinary.accelerator.tensor_core import TensorCore
from trinary.accelerator.packed_trits import PackedTritArray
from trinary.ai.activations import TRIT_TO_SIGNED_LUT, TERNARY_STEP_LUT

try:
    from trinary.gpu_native import (
        GPU_NATIVE_AVAILABLE,
        native_vec_add,
        native_vec_mul,
        native_vec_dot,
        native_vec_threshold,
        native_vec_sum,
        native_vec_max,
        native_vec_min,
        native_reduce,
        native_scan,
        native_transpose,
        native_matmul,
        native_fused_linear,
        native_elementwise_fused,
    )
except ImportError:
    GPU_NATIVE_AVAILABLE = False

USE_GPU_NATIVE = True

# Lookup tables
_T2S = TRIT_TO_SIGNED_LUT  # [ -1, 0, 1 ]  indexed by trit 0/1/2
# ternary_step for range [-2, 2] at offset +2
_TS5 = [0, 0, 1, 2, 2]

DEFAULT_WARPSIZE = 4
DEFAULT_PES_PER_WG = 16
DEFAULT_NUM_WGS = 4


def _fast_add(a, b):
    """Inlined ternary vector add — no function call overhead."""
    t2s, ts = _T2S, _TS5
    return [ts[t2s[x] + t2s[y] + 2] for x, y in zip(a, b)]


def _fast_dot(a, b):
    """Inlined ternary dot product."""
    t2s = _T2S
    total = 0
    for x, y in zip(a, b):
        total += t2s[x] * t2s[y]
    return total


def _fast_threshold(vals):
    ts = _TS5
    return [ts[v + 2] if -2 <= v <= 2 else (0 if v < -2 else 2) for v in vals]


def _fast_sum(vals):
    t2s = _T2S
    total = 0
    for v in vals:
        total += t2s[v]
    return total


def _fast_max(vals):
    t2s = _T2S
    if not vals:
        return 0
    mx = t2s[vals[0]]
    for v in vals[1:]:
        s = t2s[v]
        if s > mx:
            mx = s
    return mx


def _fast_min(vals):
    t2s = _T2S
    if not vals:
        return 0
    mn = t2s[vals[0]]
    for v in vals[1:]:
        s = t2s[v]
        if s < mn:
            mn = s
    return mn


class ProcessingElement:
    """A single GPU processing element (like a CUDA core).

    Each PE has local memory as a plain list of trits (no PackedTritArray
    overhead on hot paths).
    """

    def __init__(self, pe_id, warp_id=None):
        self.pe_id = pe_id
        self.warp_id = warp_id
        self.data = []
        self.result = None
        self.cycles = 0
        self.active = True

    def load(self, data):
        self.data = list(data)

    def execute(self, op, other=None):
        self.cycles += 1
        d = self.data
        if not d:
            self.result = []
            return

        if op == "add" and other is not None:
            self.result = _fast_add(d, other)
        elif op == "mul" and other is not None:
            self.result = [ts5[t2s[x]*t2s[y]+2] for x, y in zip(d, other)]
        elif op == "dot" and other is not None:
            self.result = _fast_dot(d, other)
        elif op == "threshold":
            self.result = _fast_threshold(d)
        elif op == "sum":
            self.result = _fast_sum(d)
        elif op == "max":
            self.result = _fast_max(d)
        elif op == "min":
            self.result = _fast_min(d)
        else:
            self.result = d[:]

    def reset(self):
        self.result = None
        self.data.clear()


class Warp:
    """A warp/wavefront: a group of PEs executing in lockstep (SIMT)."""

    def __init__(self, warp_id, size=DEFAULT_WARPSIZE):
        self.warp_id = warp_id
        self.size = size
        self.pes = []
        self.active = True
        self.scheduler_offset = 0

    def add_pe(self, pe):
        if len(self.pes) < self.size:
            pe.warp_id = self.warp_id
            self.pes.append(pe)

    def execute_kernel(self, kernel_func, data_slices=None, **kwargs):
        results = []
        for i, pe in enumerate(self.pes):
            if data_slices and i < len(data_slices):
                pe.load(data_slices[i])
            pe.execute(kernel_func, **kwargs)
            results.append(pe.result)
        return results

    def broadcast(self, data):
        for pe in self.pes:
            pe.load(data)

    def active_count(self):
        return sum(1 for pe in self.pes if pe.active)


class Workgroup:
    """A workgroup (thread block) containing warps and shared memory."""

    def __init__(self, wg_id, num_pes=DEFAULT_PES_PER_WG, warp_size=DEFAULT_WARPSIZE):
        self.wg_id = wg_id
        self.warp_size = warp_size
        self.pes = [ProcessingElement(i, warp_id=i // warp_size) for i in range(num_pes)]
        self.warps = []
        self.shared_mem = PackedTritArray()
        self._build_warps()
        self.barrier_count = 0

    def _build_warps(self):
        for i in range(0, len(self.pes), self.warp_size):
            warp = Warp(i // self.warp_size, self.warp_size)
            for pe in self.pes[i:i + self.warp_size]:
                warp.add_pe(pe)
            self.warps.append(warp)

    def broadcast(self, data):
        for pe in self.pes:
            pe.load(data)

    def shared_store(self, data):
        self.shared_mem = PackedTritArray(data)

    def shared_load(self):
        return self.shared_mem.to_list()

    def barrier(self):
        self.barrier_count += 1

    def execute_kernel(self, kernel_func, **kwargs):
        results = []
        for warp in self.warps:
            if warp.active:
                warp_results = warp.execute_kernel(kernel_func, **kwargs)
                results.extend(warp_results)
        return results

    def execute_warp(self, warp_id, kernel_func, **kwargs):
        if 0 <= warp_id < len(self.warps):
            return self.warps[warp_id].execute_kernel(kernel_func, **kwargs)
        return []

    def num_warps(self):
        return len(self.warps)

    def pe_count(self):
        return len(self.pes)


class Stream:
    """A GPU stream for concurrent kernel execution."""

    def __init__(self, stream_id):
        self.stream_id = stream_id
        self._queue = deque()
        self._completed = []
        self.lock = threading.Lock()

    def enqueue(self, kernel_func, workgroups, **kwargs):
        with self.lock:
            self._queue.append((kernel_func, workgroups, kwargs))

    def has_work(self):
        return len(self._queue) > 0

    def dequeue(self):
        with self.lock:
            if self._queue:
                return self._queue.popleft()
        return None

    def mark_complete(self, result):
        with self.lock:
            self._completed.append(result)

    def get_completed(self):
        return list(self._completed)


class TernaryGPU:
    """Simulated ternary GPU with workgroups, warps, and kernel dispatch.

    Architecture hierarchy:
        GPU → Grid of ThreadBlocks (Workgroups) → Warps → ProcessingElements

    Supports:
    - Configurable core count (workgroups × PEs per workgroup)
    - Warp-level SIMT execution
    - Shared memory within workgroups
    - Parallel matmul using all PEs
    - Reduction, scan, transpose, fused kernels
    - Multi-stream concurrent execution
    - Thread block / grid dispatch model
    """

    def __init__(self, num_workgroups=DEFAULT_NUM_WGS, pes_per_wg=DEFAULT_PES_PER_WG,
                 warp_size=DEFAULT_WARPSIZE):
        self.warp_size = warp_size
        self.workgroups = [
            Workgroup(i, pes_per_wg, warp_size) for i in range(num_workgroups)
        ]
        self.tensor_core = TensorCore()
        self.cycles = 0
        self._pipeline = []
        self.streams = {}
        self._stream_counter = 0
        self._kernel_log = []

    def total_pes(self):
        return sum(wg.pe_count() for wg in self.workgroups)

    def total_warps(self):
        return sum(wg.num_warps() for wg in self.workgroups)

    def create_stream(self):
        stream_id = self._stream_counter
        self._stream_counter += 1
        self.streams[stream_id] = Stream(stream_id)
        return stream_id

    def dispatch_kernel(self, kernel, data_slices, stream_id=None):
        results = []
        for wg, data in zip(self.workgroups, data_slices):
            per_pe_slices = self._distribute_to_pes(wg, data)
            wg_results = wg.execute_kernel(kernel, data_slices=per_pe_slices)
            results.append(wg_results)
            self.cycles += 1
        self._kernel_log.append({
            "kernel": kernel,
            "workgroups": len(data_slices),
            "cycles": self.cycles,
        })
        return results

    def dispatch_grid(self, kernel, grid_data, grid_shape):
        gx, gy = grid_shape
        n = len(grid_data)
        block_size = max(1, n // (gx * gy))
        grid_results = []
        idx = 0
        for _ in range(gy):
            row_results = []
            for _ in range(gx):
                block = grid_data[idx:idx + block_size]
                idx += block_size
                wg = self.workgroups[(idx // block_size - 1) % len(self.workgroups)]
                slices = self._distribute_to_pes(wg, block)
                row_results.append(wg.execute_kernel(kernel, data_slices=slices))
                self.cycles += 1
            grid_results.append(row_results)
        return grid_results

    def dispatch_stream(self, stream_id):
        if stream_id not in self.streams:
            return None
        item = self.streams[stream_id].dequeue()
        if item is None:
            return None
        kernel, wg_indices, kwargs = item
        results = []
        for wg_idx in wg_indices:
            if wg_idx < len(self.workgroups):
                results.append(self.workgroups[wg_idx].execute_kernel(kernel, **kwargs))
                self.cycles += 1
        self.streams[stream_id].mark_complete(results)
        return results

    def run_streams_concurrent(self):
        active = {sid: s for sid, s in self.streams.items() if s.has_work()}
        results = {}
        while active:
            for sid in list(active.keys()):
                r = self.dispatch_stream(sid)
                if r is not None:
                    results.setdefault(sid, []).append(r)
                if not active[sid].has_work():
                    del active[sid]
        return results

    def _distribute_to_pes(self, wg, data):
        """Chunk data across PEs — each PE gets roughly equal contiguous slice."""
        n = len(data)
        num_pes = wg.pe_count()
        if n == 0:
            return [[] for _ in range(num_pes)]
        base = n // num_pes
        rem = n % num_pes
        slices = []
        start = 0
        for i in range(num_pes):
            sz = base + (1 if i < rem else 0)
            slices.append(list(data[start:start + sz]) if sz else [])
            start += sz
        return slices

    def pipeline_add(self, *tensors):
        if len(tensors) < 2:
            return tensors[0] if tensors else []
        current = list(tensors[0])
        for t in tensors[1:]:
            t_list = list(t)
            current = _fast_add(current, t_list)
            self.cycles += 1
        return current

    def _transpose_b(self, mat_b):
        """Pre-transpose B so columns become rows (faster matmul access)."""
        rows = len(mat_b)
        cols = len(mat_b[0])
        return [[mat_b[r][c] for r in range(rows)] for c in range(cols)]

    def matmul_parallel(self, mat_a, mat_b):
        if not mat_a or not mat_b:
            return []
        rows_a = len(mat_a)
        cols_b = len(mat_b[0])
        inner = len(mat_b)

        # Direct C native path
        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            try:
                flat_a = [v for row in mat_a for v in row]
                flat_b = [v for row in mat_b for v in row]
                from trinary.gpu_native import _lib as _gn
                out = (ctypes.c_int * (rows_a * cols_b))()
                _gn.gpu_matmul(
                    (ctypes.c_int * len(flat_a))(*flat_a), rows_a, inner,
                    (ctypes.c_int * len(flat_b))(*flat_b), inner, cols_b,
                    out,
                )
                self.cycles += rows_a * cols_b
                return [[out[r * cols_b + c] for c in range(cols_b)] for r in range(rows_a)]
            except Exception:
                pass

        # Pre-transpose B for row-major access
        bt = self._transpose_b(mat_b) if cols_b > 1 else mat_b
        t2s = _T2S

        result = [[0] * cols_b for _ in range(rows_a)]
        for r in range(rows_a):
            row_a = mat_a[r]
            row_a_s = [t2s[v] for v in row_a]
            for c in range(cols_b):
                col_b = bt[c]
                total = 0
                for k in range(inner):
                    total += row_a_s[k] * t2s[col_b[k]]
                result[r][c] = 0 if total < -1 else (1 if total == 0 else 2) if -1 <= total <= 1 else (0 if total < -1 else 2)
                # equivalent to ternary_step but faster inline
        self.cycles += rows_a * cols_b
        return result

    def reduce(self, data, op="sum"):
        if not data:
            return 0
        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            try:
                return native_reduce(data, op)
            except Exception:
                pass
        if op == "sum":
            return _fast_sum(data)
        elif op == "max":
            return _fast_max(data)
        elif op == "min":
            return _fast_min(data)
        return 0

    def scan(self, data):
        if not data:
            return []
        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            try:
                return native_scan(data)
            except Exception:
                pass
        t2s = _T2S
        n = len(data)
        result = [0] * n
        prefix = 0
        for i in range(n):
            prefix += t2s[data[i]]
            result[i] = 0 if prefix < -1 else (1 if prefix == 0 else 2) if -1 <= prefix <= 1 else (0 if prefix < -1 else 2)
        return result

    def transpose(self, matrix):
        if not matrix or not matrix[0]:
            return []
        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            try:
                return native_transpose(matrix)
            except Exception:
                pass
        rows = len(matrix)
        cols = len(matrix[0])
        result = [[0] * rows for _ in range(cols)]
        for r in range(rows):
            row = matrix[r]
            for c in range(cols):
                result[c][r] = row[c]
        return result

    def fused_linear(self, weights, inputs, bias=None, activation="threshold"):
        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            try:
                if isinstance(inputs[0], list):
                    return [native_fused_linear(weights, inp, bias, activation)
                            for inp in inputs]
                return native_fused_linear(weights, inputs, bias, activation)
            except Exception:
                pass

        if isinstance(inputs[0], list):
            results = []
            for inp in inputs:
                flat = self.tensor_core.matmul(weights, inp)
                if isinstance(flat, list) and flat and isinstance(flat[0], list):
                    flat = [flat[0][j] for j in range(len(inp))]
                elif not isinstance(flat, list):
                    flat = list(inp)
                if bias:
                    flat = _fast_add(flat, bias)
                flat = _fast_threshold(flat)
                results.append(flat[:len(inp)])
            return results
        else:
            flat = self.tensor_core.matmul(weights, inputs)
            if isinstance(flat, list) and flat and isinstance(flat[0], list):
                flat = [flat[0][j] for j in range(len(inputs))]
            elif not isinstance(flat, list):
                flat = list(inputs)
            if bias:
                flat = _fast_add(flat, bias)
            return _fast_threshold(flat)[:len(inputs)]

    def elementwise_fused(self, a, b, op1="add", op2="threshold"):
        if len(a) != len(b):
            raise ValueError("Input lengths must match")
        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            try:
                return native_elementwise_fused(a, b, op1, op2)
            except Exception:
                pass
        if op1 == "add":
            mid = _fast_add(a, b)
        else:
            t2s, ts5 = _T2S, _TS5
            mid = [ts5[t2s[x] * t2s[y] + 2] for x, y in zip(a, b)]
        if op2 == "threshold":
            return _fast_threshold(mid)
        return mid

    def batch_dispatch(self, kernel, batch_data):
        results = [[] for _ in range(len(self.workgroups))]
        for i, data in enumerate(batch_data):
            wg = self.workgroups[i % len(self.workgroups)]
            pe = wg.pes[i % wg.pe_count()]
            d = list(data) if isinstance(data, list) else [data]
            pe.load(d)
            pe.execute(kernel)
            results[i % len(self.workgroups)].append(pe.result)
        self.cycles += 1
        return results

    def stats(self):
        total_pes = self.total_pes()
        total_warps = self.total_warps()
        npes = len(self.workgroups[0].pes) if self.workgroups else 0
        return (
            f"TernaryGPU\n"
            f"  Workgroups:  {len(self.workgroups)}\n"
            f"  PEs per WG:  {npes}\n"
            f"  Warp size:   {self.warp_size}\n"
            f"  Total warps: {total_warps}\n"
            f"  Total PEs:   {total_pes}\n"
            f"  Cycles:      {self.cycles}\n"
            f"  Streams:     {len(self.streams)}\n"
            f"  Pipeline:    {len(self._pipeline)} ops queued\n"
        )

    def arch_summary(self):
        lines = [
            "╔══════════════════════════════════════════════╗",
            "║         Ternary GPU Architecture             ║",
            "╚══════════════════════════════════════════════╝",
            "",
            f"  Grid: {len(self.workgroups)} workgroup(s)",
            f"  Block: {self.workgroups[0].pe_count() if self.workgroups else 0} PEs"
            f" ({self.warp_size} PE(s)/warp,"
            f" {self.workgroups[0].num_warps() if self.workgroups else 0} warps/block)"
            if self.workgroups else "",
            f"  Total cores: {self.total_pes()}",
            f"  Total warps: {self.total_warps()}",
            "",
        ]
        for wg in self.workgroups:
            lines.append(
                f"  WG[{wg.wg_id}]: {wg.pe_count()} PEs,"
                f" {wg.num_warps()} warps, shared_mem={len(wg.shared_mem)} trits"
            )
        return "\n".join(lines)

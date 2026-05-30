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
from trinary.accelerator.vector_ops import TritSIMD
from trinary.accelerator.packed_trits import PackedTritArray
from trinary.ai.activations import trit_to_signed, signed_to_trit, ternary_step

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


def _to_c_arr(data):
    return (ctypes.c_int * len(data))(*data)

DEFAULT_WARPSIZE = 4
DEFAULT_PES_PER_WG = 16
DEFAULT_NUM_WGS = 4


class ProcessingElement:
    """A single GPU processing element (like a CUDA core).

    Each PE has local memory, a result register, and can execute
    element-wise ternary operations on its loaded data.
    """

    def __init__(self, pe_id, warp_id=None):
        self.pe_id = pe_id
        self.warp_id = warp_id
        self.local_mem = PackedTritArray()
        self.result = None
        self.cycles = 0
        self.active = True

    def load(self, data):
        self.local_mem = PackedTritArray(data)

    def execute(self, op, other=None):
        self.cycles += 1
        data = self.local_mem.to_list()
        use_native = USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE and len(data) > 0

        if op == "add" and other is not None:
            if use_native and len(other) == len(data):
                self.result = native_vec_add(data, other)
            else:
                self.result = TritSIMD.add_vectors(data, other)
        elif op == "mul" and other is not None:
            if use_native and len(other) == len(data):
                self.result = native_vec_mul(data, other)
            else:
                self.result = TritSIMD.mul_vectors(data, other)
        elif op == "dot" and other is not None:
            if use_native and len(other) == len(data):
                self.result = native_vec_dot(data, other)
            else:
                self.result = TritSIMD.dot_product(data, other)
        elif op == "threshold":
            if use_native:
                self.result = native_vec_threshold(data)
            else:
                self.result = TritSIMD.ternary_threshold(data)
        elif op == "sum":
            if use_native:
                self.result = native_vec_sum(data)
            else:
                self.result = sum(trit_to_signed(v) for v in data)
        elif op == "max":
            if use_native:
                self.result = native_vec_max(data)
            else:
                signed = [trit_to_signed(v) for v in data]
                self.result = max(signed) if signed else 0
        elif op == "min":
            if use_native:
                self.result = native_vec_min(data)
            else:
                signed = [trit_to_signed(v) for v in data]
                self.result = min(signed) if signed else 0
        else:
            self.result = data[:]

    def reset(self):
        self.result = None
        self.local_mem = PackedTritArray()


class Warp:
    """A warp/wavefront: a group of PEs executing in lockstep (SIMT).

    All PEs in a warp execute the same instruction on different data.
    """

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
        """Execute kernel across all active PEs in lockstep.

        Args:
            kernel_func: Operation name ('add', 'mul', 'dot', 'threshold', etc.)
            data_slices: Optional list of per-PE data. If None, uses PE local_mem.
            **kwargs: Additional arguments passed to PE.execute().

        Returns:
            List of results from each PE.
        """
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
    """A workgroup (thread block) containing warps and shared memory.

    Provides shared memory for inter-PE communication within the block,
    and manages warp-level execution.
    """

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
    """A GPU stream for concurrent kernel execution.

    Kernels in the same stream execute sequentially.
    Kernels in different streams can execute concurrently.
    """

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
        """Dispatch a kernel across workgroups.

        Each workgroup receives one data slice. PEs within a workgroup
        are assigned data elements round-robin.

        Args:
            kernel: Operation name ('add', 'mul', 'dot', 'threshold', 'sum', etc.)
            data_slices: List of data lists, one per workgroup.

        Returns:
            List of results per workgroup.
        """
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
        """Dispatch kernel over a 2D grid of thread blocks.

        Args:
            kernel: Operation name.
            grid_data: Flat list of data elements.
            grid_shape: (grid_x, grid_y) tuple.

        Returns:
            2D list of results indexed by [grid_y][grid_x].
        """
        gx, gy = grid_shape
        total_elements = len(grid_data)
        elements_per_block = max(1, total_elements // (gx * gy))

        grid_results = []
        idx = 0
        for row in range(gy):
            row_results = []
            for col in range(gx):
                block_data = grid_data[idx:idx + elements_per_block]
                idx += elements_per_block
                wg_idx = (row * gx + col) % len(self.workgroups)
                wg = self.workgroups[wg_idx]
                per_pe_slices = self._distribute_to_pes(wg, block_data)
                wg_results = wg.execute_kernel(kernel, data_slices=per_pe_slices)
                row_results.append(wg_results)
                self.cycles += 1
            grid_results.append(row_results)
        return grid_results

    def dispatch_stream(self, stream_id):
        """Execute next kernel from a stream on available workgroups."""
        if stream_id not in self.streams:
            return None
        stream = self.streams[stream_id]
        item = stream.dequeue()
        if item is None:
            return None
        kernel, workgroup_indices, kwargs = item
        results = []
        for wg_idx in workgroup_indices:
            if wg_idx < len(self.workgroups):
                wg = self.workgroups[wg_idx]
                wg_results = wg.execute_kernel(kernel, **kwargs)
                results.append(wg_results)
                self.cycles += 1
        stream.mark_complete(results)
        return results

    def run_streams_concurrent(self):
        """Run all streams concurrently, round-robin scheduling."""
        active = {sid: s for sid, s in self.streams.items() if s.has_work()}
        results = {}
        while active:
            for sid in list(active.keys()):
                result = self.dispatch_stream(sid)
                if result is not None:
                    results.setdefault(sid, []).append(result)
                if not active[sid].has_work():
                    del active[sid]
        return results

    def _distribute_to_pes(self, wg, data):
        """Round-robin distribute data elements across PEs in a workgroup."""
        num_pes = wg.pe_count()
        slices = []
        for i in range(num_pes):
            start = i
            step = num_pes
            pe_data = data[start::step] if step > 0 else data[:]
            slices.append(pe_data)
        return slices

    def pipeline_add(self, *tensors):
        """Build a tensor pipeline: add tensors sequentially.

        Each step is parallelized across all PEs in all workgroups.
        """
        if len(tensors) < 2:
            return tensors[0] if tensors else []
        current = tensors[0]
        num_wgs = len(self.workgroups)
        for t in tensors[1:]:
            slices = [current[j::num_wgs] for j in range(num_wgs)]
            other_slices = [t[j::num_wgs] for j in range(num_wgs)]
            wg_results = []
            for wg_idx, wg in enumerate(self.workgroups):
                per_pe = self._distribute_to_pes(wg, slices[wg_idx])
                other_pe = self._distribute_to_pes(wg, other_slices[wg_idx])
                results = []
                for pe, oth in zip(wg.pes, other_pe):
                    if oth:
                        pe.load(per_pe[wg.pes.index(pe) % len(per_pe)] if per_pe else [])
                        pe.execute("add", other=oth)
                        results.append(pe.result)
                    else:
                        results.append(per_pe[wg.pes.index(pe) % len(per_pe)] if per_pe else [])
                wg_results.append(results)
            current = [v for wg_r in wg_results for v in wg_r if v is not None]
            self.cycles += 1
        return current

    def matmul_parallel(self, mat_a, mat_b):
        """Matrix multiply using all PEs across all workgroups.

        Each workgroup computes a block of result rows.
        Within each workgroup, PEs compute different columns in parallel.

        Args:
            mat_a: List of lists (rows of trits).
            mat_b: List of lists (columns of trits).

        Returns:
            Result matrix as list of lists.
        """
        if not mat_a or not mat_b:
            return []
        rows_a = len(mat_a)
        cols_b = len(mat_b[0])
        inner = len(mat_b)

        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            result_flat = (ctypes.c_int * (rows_a * cols_b))()
            flat_a = [v for row in mat_a for v in row]
            flat_b = [v for row in mat_b for v in row]
            _lib = None
            try:
                from trinary.gpu_native import _lib as _gn
                _gn.gpu_matmul(
                    _to_c_arr(flat_a), rows_a, inner,
                    _to_c_arr(flat_b), inner, cols_b,
                    result_flat,
                )
                self.cycles += cols_b * rows_a
                return [[result_flat[r * cols_b + c] for c in range(cols_b)]
                        for r in range(rows_a)]
            except Exception:
                pass

        result = [[0] * cols_b for _ in range(rows_a)]
        rows_per_wg = max(1, rows_a // len(self.workgroups))
        for wg_idx, wg in enumerate(self.workgroups):
            start_r = wg_idx * rows_per_wg
            end_r = min(start_r + rows_per_wg, rows_a)
            num_pes = wg.pe_count()

            for r in range(start_r, end_r):
                row_vec = mat_a[r]
                pes_active = min(num_pes, cols_b)
                cols_per_pe = max(1, (cols_b + pes_active - 1) // pes_active)

                for pe_idx in range(pes_active):
                    col_start = pe_idx * cols_per_pe
                    col_end = min(col_start + cols_per_pe, cols_b)
                    if col_start >= cols_b:
                        break
                    pe = wg.pes[pe_idx]
                    pe.load(row_vec)

                for c in range(cols_b):
                    pe_idx = c % pes_active
                    col_vec = [mat_b[k][c] for k in range(inner)]
                    wg.pes[pe_idx].execute("dot", other=col_vec)
                    dot_result = wg.pes[pe_idx].result
                    result[r][c] = dot_result if isinstance(dot_result, int) else 0

            self.cycles += cols_b * max(1, end_r - start_r)
        return result

    def reduce(self, data, op="sum"):
        """Parallel reduction across all PEs.

        Splits data across PEs, each reduces its chunk, then
        combines results.

        Args:
            data: List of trit values.
            op: Reduction operation ('sum', 'max', 'min').

        Returns:
            Scalar result.
        """
        if not data:
            return 0

        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            try:
                return native_reduce(data, op)
            except Exception:
                pass

        num_wgs = min(len(self.workgroups), len(data))
        chunks = [data[i::num_wgs] for i in range(num_wgs)]
        partials = []

        for wg_idx in range(num_wgs):
            wg = self.workgroups[wg_idx]
            per_pe = self._distribute_to_pes(wg, chunks[wg_idx])
            for pe_idx, pe in enumerate(wg.pes):
                if pe_idx < len(per_pe) and per_pe[pe_idx]:
                    pe.load(per_pe[pe_idx])
                    pe.execute(op)
                    if pe.result is not None:
                        partials.append(pe.result)
            self.cycles += 1

        if not partials:
            return 0

        if op == "sum":
            return sum(partials)
        elif op == "max":
            return max(partials)
        elif op == "min":
            return min(partials)
        return 0

    def scan(self, data):
        """Prefix scan (inclusive) across data using parallel workgroups.

        Each workgroup scans its chunk, then propagates prefixes.
        """
        if not data:
            return []

        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            try:
                return native_scan(data)
            except Exception:
                pass

        n = len(data)
        num_wgs = min(len(self.workgroups), n)
        chunk_size = max(1, n // num_wgs)

        result = list(data)
        for wg_idx in range(num_wgs):
            start = wg_idx * chunk_size
            end = min(start + chunk_size, n)
            signed = [trit_to_signed(v) for v in result[start:end]]
            prefix = 0
            for i in range(len(signed)):
                prefix += signed[i]
                result[start + i] = signed_to_trit(max(-1, min(1, prefix)))

        prefix_sum = 0
        for wg_idx in range(num_wgs):
            start = wg_idx * chunk_size
            end = min(start + chunk_size, n)
            for i in range(start, end):
                signed_val = trit_to_signed(result[i])
                result[i] = signed_to_trit(max(-1, min(1, signed_val + prefix_sum)))
            if end > start:
                chunk_signed = [trit_to_signed(v) for v in result[start:end]]
                prefix_sum += sum(chunk_signed)
            self.cycles += 1

        return result

    def transpose(self, matrix):
        """Parallel matrix transpose using workgroups."""
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

        num_wgs = min(len(self.workgroups), rows)
        for wg_idx in range(num_wgs):
            wg = self.workgroups[wg_idx]
            rows_per_wg = max(1, rows // num_wgs)
            start = wg_idx * rows_per_wg
            end = min(start + rows_per_wg, rows)
            for r in range(start, end):
                for c in range(cols):
                    result[c][r] = matrix[r][c]
            self.cycles += (end - start) * cols
        return result

    def fused_linear(self, weights, inputs, bias=None, activation="threshold"):
        """Fused linear layer: activation(W @ x + b) using tensor core + GPU.

        Args:
            weights: 2D matrix of trits.
            inputs: 1D vector of trits (or 2D for batch).
            bias: Optional 1D bias vector.
            activation: Activation function name.

        Returns:
            Result vector.
        """
        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            try:
                if isinstance(inputs[0], list):
                    return [native_fused_linear(weights, inp, bias, activation)
                            for inp in inputs]
                else:
                    return native_fused_linear(weights, inputs, bias, activation)
            except Exception:
                pass

        if isinstance(inputs[0], list):
            results = []
            for inp in inputs:
                matmul_result = self.tensor_core.matmul(weights, inp)
                if isinstance(matmul_result, list) and matmul_result and isinstance(matmul_result[0], list):
                    flat = [matmul_result[0][j] for j in range(len(inp))]
                elif isinstance(matmul_result, list):
                    flat = matmul_result
                else:
                    flat = inp[:]
                if bias:
                    flat = TritSIMD.add_vectors(flat, bias)
                num_wgs = len(self.workgroups)
                slices = [flat[j::num_wgs] for j in range(num_wgs)]
                results_wg = []
                for wg_idx, wg in enumerate(self.workgroups):
                    per_pe = self._distribute_to_pes(wg, slices[wg_idx])
                    wg_results = wg.execute_kernel(activation, data_slices=per_pe)
                    for r in wg_results:
                        if r is not None:
                            results_wg.append(r)
                results.append(results_wg[:len(inp)])
            return results
        else:
            matmul_result = self.tensor_core.matmul(weights, inputs)
            if isinstance(matmul_result, list) and matmul_result and isinstance(matmul_result[0], list):
                flat = [matmul_result[0][j] for j in range(len(inputs))]
            elif isinstance(matmul_result, list):
                flat = matmul_result
            else:
                flat = inputs[:]
            if bias:
                flat = TritSIMD.add_vectors(flat, bias)
            num_wgs = len(self.workgroups)
            slices = [flat[j::num_wgs] for j in range(num_wgs)]
            results_wg = []
            for wg_idx, wg in enumerate(self.workgroups):
                per_pe = self._distribute_to_pes(wg, slices[wg_idx])
                wg_results = wg.execute_kernel(activation, data_slices=per_pe)
                for r in wg_results:
                    if r is not None:
                        results_wg.append(r)
            return results_wg[:len(inputs)]

    def elementwise_fused(self, a, b, op1="add", op2="threshold"):
        """Fused element-wise: apply op1 then op2 in a single pass.

        Example: add + threshold = ternary addition with normalization.
        """
        if len(a) != len(b):
            raise ValueError("Input lengths must match")

        if USE_GPU_NATIVE and GPU_NATIVE_AVAILABLE:
            try:
                return native_elementwise_fused(a, b, op1, op2)
            except Exception:
                pass

        num_wgs = min(len(self.workgroups), len(a))
        slices_a = [a[i::num_wgs] for i in range(num_wgs)]
        slices_b = [b[i::num_wgs] for i in range(num_wgs)]
        results = []
        for wg_idx in range(num_wgs):
            wg = self.workgroups[wg_idx]
            per_pe_a = self._distribute_to_pes(wg, slices_a[wg_idx])
            per_pe_b = self._distribute_to_pes(wg, slices_b[wg_idx])
            for pe_idx, pe in enumerate(wg.pes):
                if pe_idx < len(per_pe_a) and per_pe_a[pe_idx]:
                    pe.load(per_pe_a[pe_idx])
                    pe.execute(op1, other=per_pe_b[pe_idx] if pe_idx < len(per_pe_b) else None)
                    if pe.result is not None:
                        pe.load(pe.result)
                        pe.execute(op2)
                        results.append(pe.result)
            self.cycles += 1
        return results

    def batch_dispatch(self, kernel, batch_data):
        """Dispatch kernel on a batch of data, parallelized across all PEs.

        Each PE processes one element from the batch simultaneously.
        """
        total_pes = self.total_pes()
        results = [[] for _ in range(len(self.workgroups))]

        wg_idx = 0
        for i, data in enumerate(batch_data):
            wg = self.workgroups[wg_idx % len(self.workgroups)]
            pe_idx = i % wg.pe_count()
            pe = wg.pes[pe_idx]
            if isinstance(data, list):
                pe.load(data)
            else:
                pe.load([data])
            pe.execute(kernel)
            results[wg_idx % len(self.workgroups)].append(pe.result)
            wg_idx += 1

        self.cycles += 1
        return results

    def stats(self):
        total_pes = self.total_pes()
        total_warps = self.total_warps()
        return (
            f"TernaryGPU\n"
            f"  Workgroups:  {len(self.workgroups)}\n"
            f"  PEs per WG:  {len(self.workgroups[0].pes) if self.workgroups else 0}\n"
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

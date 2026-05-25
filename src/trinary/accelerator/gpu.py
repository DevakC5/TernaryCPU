"""Ternary GPU — parallel execution blocks, workgroups, and kernels.

Simulates a GPU-like compute architecture with:
- Workgroups of processing elements
- Kernel dispatch
- Parallel tensor pipelines
- SIMT (single instruction, multiple thread) execution
"""

from trinary.accelerator.tensor_core import TensorCore
from trinary.accelerator.vector_ops import TritSIMD
from trinary.accelerator.packed_trits import PackedTritArray


class ProcessingElement:
    """A single GPU processing element (like a CUDA core)."""

    def __init__(self, pe_id):
        self.pe_id = pe_id
        self.local_mem = PackedTritArray()
        self.result = None

    def load(self, data):
        self.local_mem = PackedTritArray(data)

    def execute(self, op, other=None):
        if op == "add" and other is not None:
            self.result = TritSIMD.add_vectors(self.local_mem.to_list(), other)
        elif op == "mul" and other is not None:
            self.result = TritSIMD.mul_vectors(self.local_mem.to_list(), other)
        elif op == "dot" and other is not None:
            self.result = TritSIMD.dot_product(self.local_mem.to_list(), other)
        elif op == "threshold":
            self.result = TritSIMD.ternary_threshold(self.local_mem.to_list())
        else:
            self.result = self.local_mem.to_list()[:]


class Workgroup:
    """A workgroup containing multiple processing elements."""

    def __init__(self, wg_id, num_pes=4):
        self.wg_id = wg_id
        self.pes = [ProcessingElement(i) for i in range(num_pes)]
        self.shared_mem = PackedTritArray()

    def broadcast(self, data):
        for pe in self.pes:
            pe.load(data)

    def execute_kernel(self, kernel_func, **kwargs):
        results = []
        for pe in self.pes:
            pe.execute(kernel_func, **kwargs)
            results.append(pe.result)
        return results


class TernaryGPU:
    """Simulated ternary GPU with workgroups and kernel dispatch.

    Supports:
    - Multiple workgroups with processing elements
    - Kernel dispatch (element-wise add, mul, dot, threshold)
    - Tensor pipeline operations
    - Parallel execution simulation
    """

    def __init__(self, num_workgroups=2, pes_per_wg=4):
        self.workgroups = [
            Workgroup(i, pes_per_wg) for i in range(num_workgroups)
        ]
        self.tensor_core = TensorCore()
        self.cycles = 0
        self._pipeline = []

    def dispatch_kernel(self, kernel, data_slices):
        """Dispatch a kernel across workgroups.

        Args:
            kernel: Operation name ('add', 'mul', 'dot', 'threshold').
            data_slices: List of data lists, one per workgroup.

        Returns:
            List of results per workgroup.
        """
        results = []
        for wg, data in zip(self.workgroups, data_slices):
            wg.broadcast(data)
            wg_results = wg.execute_kernel(kernel)
            results.append(wg_results)
            self.cycles += 1
        return results

    def pipeline_add(self, *tensors):
        """Build a tensor pipeline: add tensors sequentially.

        Each step in the pipeline is executed in parallel across all PEs.

        Args:
            *tensors: Variable number of trit lists.

        Returns:
            Pipeline output.
        """
        if len(tensors) < 2:
            return tensors[0] if tensors else []
        current = tensors[0]
        for i, t in enumerate(tensors[1:], 1):
            slices = [
                current[j::len(self.workgroups)]
                for j in range(len(self.workgroups))
            ]
            other_slices = [
                t[j::len(self.workgroups)]
                for j in range(len(self.workgroups))
            ]
            wg_results = []
            for wg_idx, wg in enumerate(self.workgroups):
                wg.broadcast(slices[wg_idx])
                wg_results.append(
                    wg.execute_kernel("add", other=other_slices[wg_idx])
                )
            current = [v for wg_r in wg_results for pe_r in wg_r for v in pe_r]
            self.cycles += 1
        return current

    def matmul_parallel(self, mat_a, mat_b):
        """Matrix multiply using parallel workgroup dispatch.

        Each workgroup computes a row block of the result.

        Args:
            mat_a: List of lists (rows of trits).
            mat_b: List of lists (columns of trits) — transposed for access.

        Returns:
            Result matrix as list of lists.
        """
        if not mat_a or not mat_b:
            return []
        rows = len(mat_a)
        cols = len(mat_b[0])
        cols_b = len(mat_b)
        result = [[0] * cols for _ in range(rows)]
        rows_per_wg = max(1, rows // len(self.workgroups))
        for wg_idx, wg in enumerate(self.workgroups):
            start_r = wg_idx * rows_per_wg
            end_r = min(start_r + rows_per_wg, rows)
            for r in range(start_r, end_r):
                for c in range(cols):
                    col_vec = [mat_b[k][c] for k in range(cols_b)]
                    wg.pes[0].load(mat_a[r])
                    wg.pes[0].execute("dot", other=col_vec)
                    dot_result = wg.pes[0].result
                    result[r][c] = dot_result if isinstance(dot_result, int) else 0
            self.cycles += cols
        return result

    def stats(self):
        """Return a summary string of GPU stats."""
        total_pes = sum(len(wg.pes) for wg in self.workgroups)
        return (
            f"TernaryGPU\n"
            f"  Workgroups: {len(self.workgroups)}\n"
            f"  PEs per WG: {len(self.workgroups[0].pes) if self.workgroups else 0}\n"
            f"  Total PEs:  {total_pes}\n"
            f"  Cycles:     {self.cycles}\n"
            f"  Pipeline:   {len(self._pipeline)} ops queued\n"
        )

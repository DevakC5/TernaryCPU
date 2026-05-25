"""TernaryTensorAccelerator — the main tensor execution unit.

Integrates tensor memory, SIMD lanes, and the tensor core into
a single coprocessor that executes tensor instructions.
"""

from trinary.ai.activations import ternary_step, ternary_relu, trit_to_signed
from trinary.accelerator.tensor_memory import TensorMemory
from trinary.accelerator.vector_ops import TritSIMD
from trinary.accelerator.tensor_core import TensorCore
from trinary.accelerator.simd import SIMDProcessor
from trinary.accelerator.instruction_set import (
    Instruction,
    Opcode,
)


class TernaryTensorAccelerator:
    """Tensor accelerator coprocessor.

    Contains a TensorMemory, SIMDProcessor, and TensorCore.
    Executes tensor instructions in a sequential program model.

    Args:
        mem_capacity: Number of tensor slots (default 64).
        simd_lanes: Number of SIMD lanes (default 4).
    """

    def __init__(self, mem_capacity=64, simd_lanes=4):
        self.memory = TensorMemory(capacity=mem_capacity)
        self.simd = SIMDProcessor(lanes=simd_lanes)
        self.core = TensorCore()
        self.cycles = 0
        self._program_counter = 0
        self._debug = False

    @property
    def stats(self):
        return {
            "cycles": self.cycles,
            "tensors": len(self.memory._slots),
            "simd_lanes": self.simd.lanes,
            "trit_count": self.memory.total_trits(),
        }

    def execute(self, instr):
        """Execute a single instruction.

        Args:
            instr: An Instruction instance.

        Returns:
            Result dependent on opcode (list of trits, int, or None).
        """
        op = instr.opcode
        self.cycles += 1

        if op == Opcode.TLOAD:
            tid = self.memory.allocate()
            return tid

        elif op == Opcode.TSTORE:
            return None

        elif op == Opcode.TVECADD:
            a = self.memory.load_list(instr.src_a)
            b = self.memory.load_list(instr.src_b)
            result = TritSIMD.add_vectors(a, b)
            if instr.dest is not None:
                self.memory.store(instr.dest, result)
            return result

        elif op == Opcode.TVECSUB:
            a = self.memory.load_list(instr.src_a)
            b = self.memory.load_list(instr.src_b)
            result = TritSIMD.sub_vectors(a, b)
            if instr.dest is not None:
                self.memory.store(instr.dest, result)
            return result

        elif op == Opcode.TVECMUL:
            a = self.memory.load_list(instr.src_a)
            b = self.memory.load_list(instr.src_b)
            result = TritSIMD.mul_vectors(a, b)
            if instr.dest is not None:
                self.memory.store(instr.dest, result)
            return result

        elif op == Opcode.TDOT:
            a = self.memory.load_list(instr.src_a)
            b = self.memory.load_list(instr.src_b)
            result = TritSIMD.dot_product(a, b)
            if instr.dest is not None:
                t = self.memory.allocate(
                    [ternary_step(result)]
                )
                return t, result
            return result

        elif op == Opcode.TMATMUL:
            try:
                mat_a = self.memory.load_2d(instr.src_a)
            except ValueError:
                flat_a = self.memory.load_list(instr.src_a)
                if instr.extra is not None:
                    cols = instr.extra
                    rows = len(flat_a) // cols
                    mat_a = [flat_a[r * cols:(r + 1) * cols] for r in range(rows)]
                else:
                    mat_a = [flat_a]
            try:
                mat_b = self.memory.load_2d(instr.src_b)
            except ValueError:
                flat_b = self.memory.load_list(instr.src_b)
                if instr.extra is not None:
                    cols = instr.extra
                    rows = len(flat_b) // cols
                    mat_b = [flat_b[r * cols:(r + 1) * cols] for r in range(rows)]
                else:
                    mat_b = [flat_b]
            result = self.core.matmul(mat_a, mat_b)
            if instr.dest is not None:
                flat = [v for row in result for v in row] if isinstance(result[0], list) else result
                self.memory.store(instr.dest, flat)
            return result

        elif op == Opcode.TACT:
            src = self.memory.load_list(instr.src_a)
            act_type = instr.extra if instr.extra is not None else 0
            if act_type == 0:
                result = [ternary_step(trit_to_signed(v)) for v in src]
            elif act_type == 1:
                result = [ternary_relu(trit_to_signed(v)) for v in src]
            else:
                raise ValueError(f"Unknown activation type: {act_type}")
            if instr.dest is not None:
                self.memory.store(instr.dest, result)
            return result

        elif op == Opcode.TFUSED:
            w = self.memory.load_list(instr.src_a)
            x = self.memory.load_list(instr.src_b)
            bias = self.memory.load_list(instr.dest) if instr.dest else None
            act_type = instr.extra if instr.extra is not None else 0
            act = ternary_step if act_type == 0 else ternary_relu
            weights_2d = [w[i:i + len(x)] for i in range(0, len(w), len(x))]
            result = self.core.fused_linear(weights_2d, x, bias=bias, activation=act)
            return result

        elif op == Opcode.TCONV:
            return None

        else:
            raise ValueError(f"Unknown opcode: {op}")

    def run_program(self, instructions):
        """Execute a list of instructions sequentially.

        Args:
            instructions: List of Instruction objects.

        Returns:
            List of results, one per instruction.
        """
        results = []
        self._program_counter = 0
        for instr in instructions:
            if self._debug:
                print(f"  [{self._program_counter}] {instr}")
            result = self.execute(instr)
            results.append(result)
            self._program_counter += 1
        return results

    def benchmark(self):
        """Return a summary string of accelerator stats."""
        return (
            f"TernaryTensorAccelerator\n"
            f"  Cycles: {self.cycles}\n"
            f"  Tensors allocated: {len(self.memory._slots)}\n"
            f"  Total trits stored: {self.memory.total_trits()}\n"
            f"  SIMD lanes: {self.simd.lanes}\n"
            f"  Tensor memory: {self.memory.total_bytes()} bytes packed\n"
        )

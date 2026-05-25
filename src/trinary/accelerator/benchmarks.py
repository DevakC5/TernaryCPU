"""Benchmarks for the Ternary Tensor Accelerator subsystem.

Measures throughput for packed operations, SIMD vector ops,
tensor core matmul, and full accelerator workflows.
"""

import time
import random

from trinary.accelerator.packed_trits import PackedTritArray
from trinary.accelerator.vector_ops import TritSIMD
from trinary.accelerator.simd import SIMDProcessor
from trinary.accelerator.tensor_core import TensorCore
from trinary.accelerator.accelerator import TernaryTensorAccelerator


def _fmt(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.2f}K"
    return f"{n:.2f}"


def bench_packed_throughput(n=100_000):
    a = [random.choice([0, 1, 2]) for _ in range(n)]
    packed = PackedTritArray(a)
    start = time.perf_counter()
    for _ in range(100):
        _ = packed.to_list()
    elapsed = time.perf_counter() - start
    ops = (n * 100) / elapsed
    return ops, elapsed, packed.compression_ratio()


def bench_simd_add(n_runs=50_000):
    a = [2, 0, 1, 2]
    b = [0, 2, 1, 0]
    start = time.perf_counter()
    for _ in range(n_runs):
        TritSIMD.add_vectors(a, b)
    elapsed = time.perf_counter() - start
    ops = n_runs / elapsed
    return ops, elapsed


def bench_tensor_matmul(n_runs=10_000):
    core = TensorCore()
    a = [[2, 0], [0, 2]]
    b = [[2, 0], [0, 2]]
    start = time.perf_counter()
    for _ in range(n_runs):
        core.matmul(a, b)
    elapsed = time.perf_counter() - start
    ops = n_runs / elapsed
    return ops, elapsed


def bench_packed_vs_list(n=1000):
    data = [random.choice([0, 1, 2]) for _ in range(n)]
    packed = PackedTritArray(data)

    start = time.perf_counter()
    for _ in range(10000):
        _ = [x for x in data]
    list_time = time.perf_counter() - start

    start = time.perf_counter()
    for _ in range(10000):
        _ = [x for x in packed]
    packed_time = time.perf_counter() - start

    return list_time, packed_time, packed.compression_ratio()


def bench_accelerator_program(n_runs=5000):
    accel = TernaryTensorAccelerator()
    from trinary.accelerator.instruction_set import Instruction, Opcode
    start = time.perf_counter()
    for _ in range(n_runs):
        tid_a = accel.memory.allocate([2, 0, 1, 2])
        tid_b = accel.memory.allocate([0, 2, 1, 0])
        tid_c = accel.memory.allocate(length=4)
        accel.run_program([
            Instruction(Opcode.TVECADD, dest=tid_c, src_a=tid_a, src_b=tid_b),
            Instruction(Opcode.TVECMUL, dest=tid_c, src_a=tid_a, src_b=tid_b),
            Instruction(Opcode.TDOT, dest=tid_c, src_a=tid_a, src_b=tid_b),
        ])
        accel.memory._slots.clear()
        accel.memory._next_id = 0
    elapsed = time.perf_counter() - start
    ops = (n_runs * 3) / elapsed
    return ops, elapsed, 3


def run_all():
    """Run all benchmarks."""
    random.seed(42)
    print("=" * 55)
    print("  Ternary Tensor Accelerator — Benchmarks")
    print("=" * 55)
    print()

    ops, sec, ratio = bench_packed_throughput()
    print(f"PackedTritArray unpack (100K trits × 100):")
    print(f"  {_fmt(ops)} trits/s  ({sec:.4f}s)")
    print(f"  Compression ratio: {ratio:.1f}x")
    print()

    ops, sec = bench_simd_add()
    print(f"SIMD vector add (4-trit × {_fmt(50000)}):")
    print(f"  {_fmt(ops)} ops/s  ({sec:.4f}s)")
    print()

    ops, sec = bench_tensor_matmul()
    print(f"Tensor core matmul (2×2 × {_fmt(10000)}):")
    print(f"  {_fmt(ops)} ops/s  ({sec:.4f}s)")
    print()

    list_t, packed_t, ratio = bench_packed_vs_list()
    print(f"Packed vs list iteration (1000 trits × 10000):")
    print(f"  Python list:  {list_t:.4f}s")
    print(f"  PackedTrit:   {packed_t:.4f}s")
    print(f"  Compression:  {ratio:.1f}x")
    print()

    ops, sec, ninstr = bench_accelerator_program()
    print(f"Accelerator program ({ninstr} instr × {_fmt(5000)}):")
    print(f"  {_fmt(ops)} instructions/s  ({sec:.4f}s)")
    print()


if __name__ == "__main__":
    run_all()

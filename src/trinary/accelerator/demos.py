"""Demonstrations of the Ternary Tensor Accelerator subsystem.

Shows packed storage, SIMD operations, tensor core matmul,
and neural inference acceleration.
"""

import time
import random

from trinary.accelerator.packed_trits import PackedTritArray
from trinary.accelerator.vector_ops import TritSIMD
from trinary.accelerator.simd import SIMDProcessor
from trinary.accelerator.tensor_core import TensorCore
from trinary.accelerator.accelerator import TernaryTensorAccelerator
from trinary.accelerator.instruction_set import Instruction, Opcode


def _header(title):
    print()
    print("=" * 55)
    print(f"  {title}")
    print("=" * 55)


def demo_packed_storage():
    _header("Packed Trit Storage Demo")
    trits = [2, 0, 1, 2, 1, 0, 2, 0, 1, 1]
    packed = PackedTritArray(trits)
    print(f"  Original: {trits}")
    print(f"  Packed:   {list(packed)}")
    print(f"  Length:   {len(packed)}")
    print(f"  Bytes:    {packed.memory_bytes()} (vs ~{len(trits) * 28}B raw)")
    print(f"  Ratio:    {packed.compression_ratio():.1f}x")
    print(f"  Signed:   {packed.to_signed()}")
    print()


def demo_simd():
    _header("SIMD Vector Operations Demo")
    a = [2, 0, 2, 0]
    b = [0, 2, 0, 2]
    print(f"  a = {a}  [{' '.join('+' if x==2 else '-' if x==0 else '0' for x in a)}]")
    print(f"  b = {b}  [{' '.join('+' if x==2 else '-' if x==0 else '0' for x in b)}]")
    print(f"  add:  {TritSIMD.add_vectors(a, b)}")
    print(f"  sub:  {TritSIMD.sub_vectors(a, b)}")
    print(f"  mul:  {TritSIMD.mul_vectors(a, b)}")
    print(f"  max:  {TritSIMD.max_vectors(a, b)}")
    print(f"  min:  {TritSIMD.min_vectors(a, b)}")
    print(f"  dot:  {TritSIMD.dot_product(a, b)}")
    print()


def demo_simd_processor():
    _header("SIMD Processor — Lane Execution")
    simd = SIMDProcessor(lanes=4)
    simd.load([2, 0, 1, 2])
    print(f"  After load:  {simd.registers}")
    simd.add([0, 2, 1, 0])
    print(f"  After add:   {simd.registers}")
    simd.mul([2, 0, 2, 0])
    print(f"  After mul:   {simd.registers}")
    d = simd.dot([2, 0, 2, 0])
    print(f"  Dot product: {d}")
    print()
    print(f"  {simd.show_state()}")
    print()


def demo_tensor_core():
    _header("Tensor Core — Matrix Multiply Demo")
    core = TensorCore()
    a = [[2, 0], [0, 2]]
    b = [[2, 0], [0, 2]]
    print(f"  A = {a}")
    print(f"  B = {b}")
    c = core.matmul(a, b)
    print(f"  A @ B = {c}")
    print()

    x = [2, 0, 2]
    w = [[2, 0, 2], [0, 2, 0]]
    bias = [1, 1]
    print(f"  W = {w}")
    print(f"  x = {x}")
    print(f"  b = {bias}")
    out = core.fused_linear(w, x, bias)
    print(f"  fused_linear(W, x, b, step) = {out}")
    out_relu = core.fused_linear(w, x, bias, activation=lambda v: 2 if v > 0 else 1)
    print(f"  fused_linear(W, x, b, relu) = {out_relu}")
    print()


def demo_batched_matmul():
    _header("Batched Matrix Multiply Demo")
    core = TensorCore()
    batch_a = [
        [[2, 0], [0, 2]],
        [[0, 2], [2, 0]],
    ]
    batch_b = [
        [[2, 0], [0, 2]],
        [[2, 0], [0, 2]],
    ]
    results = core.batch_matmul(batch_a, batch_b)
    for i, (a, b, c) in enumerate(zip(batch_a, batch_b, results)):
        print(f"  Batch {i}: {a} @ {b} = {c}")
    print()


def demo_accelerator_program():
    _header("Accelerator — Instruction Program Demo")
    accel = TernaryTensorAccelerator(mem_capacity=32, simd_lanes=4)

    tid_a = accel.memory.allocate([2, 0, 1, 2])
    tid_b = accel.memory.allocate([0, 2, 1, 0])
    print(f"  Tensor A (id={tid_a}): {accel.memory.load_list(tid_a)}")
    print(f"  Tensor B (id={tid_b}): {accel.memory.load_list(tid_b)}")

    tid_c = accel.memory.allocate(length=4)
    program = [
        Instruction(Opcode.TVECADD, dest=tid_c, src_a=tid_a, src_b=tid_b),
        Instruction(Opcode.TVECMUL, dest=tid_c, src_a=tid_a, src_b=tid_b),
        Instruction(Opcode.TDOT, dest=tid_c, src_a=tid_a, src_b=tid_b),
    ]
    print(f"\n  Running {len(program)} instructions...")
    results = accel.run_program(program)
    print(f"  TVECADD result: {accel.memory.load_list(tid_c)}")
    print(f"  TDOT result:    {results[2] if not isinstance(results[2], tuple) else results[2][0]}")
    print(f"\n  Accelerator stats: {accel.stats}")
    print()


def demo_neural_inference():
    _header("Accelerator — Neural Inference Demo")
    accel = TernaryTensorAccelerator()

    w = [[2, 0, 2], [0, 2, 0]]
    x = [2, 0, 2]
    bias = [1, 1]

    tid_w = accel.memory.allocate([v for row in w for v in row])
    tid_x = accel.memory.allocate(x)
    tid_b = accel.memory.allocate(bias)
    tid_out = accel.memory.allocate(length=2)

    program = [
        Instruction(Opcode.TFUSED, dest=tid_b, src_a=tid_w, src_b=tid_x, extra=0),
    ]
    accel.run_program(program)
    print(f"  Input:       {x}")
    print(f"  Weights:     {w}")
    print(f"  Bias:        {bias}")
    print(f"  Output:      {accel.memory.load_list(tid_b)}")
    print()


def demo_performance():
    _header("Accelerator — Performance Comparison")
    random.seed(42)

    n = 64
    a = [random.choice([0, 1, 2]) for _ in range(n)]
    b = [random.choice([0, 1, 2]) for _ in range(n)]

    start = time.perf_counter()
    for _ in range(1000):
        _ = [min(x, y) for x, y in zip(a, b)]
    py_time = time.perf_counter() - start

    packed_a = PackedTritArray(a)
    packed_b = PackedTritArray(b)
    start = time.perf_counter()
    for _ in range(1000):
        packed_result = PackedTritArray(
            min(x, y) for x, y in zip(packed_a, packed_b)
        )
    packed_time = time.perf_counter() - start

    print(f"  Python list min (64×1000): {py_time:.4f}s")
    print(f"  Packed min     (64×1000): {packed_time:.4f}s")
    print(f"  Compression:              {PackedTritArray(a).compression_ratio():.1f}x")
    print(f"  Python bytes:             {len(a) * 28}B")
    print(f"  Packed bytes:             {PackedTritArray(a).memory_bytes()}B")
    print()


def run_all():
    """Run all accelerator demos."""
    demo_packed_storage()
    demo_simd()
    demo_simd_processor()
    demo_tensor_core()
    demo_batched_matmul()
    demo_accelerator_program()
    demo_neural_inference()
    demo_performance()


if __name__ == "__main__":
    run_all()

"""
Benchmark comparing Python vs native C arithmetic performance.

Runs 1 million operations per test and prints speedup ratios.
"""

import time
import random

from trinary.native_backend import (
    NATIVE_AVAILABLE,
    native_add,
    native_sub,
    native_mul,
    native_div,
    native_full_adder,
)


def _py_add(a, b): return a + b
def _py_sub(a, b): return a - b
def _py_mul(a, b): return a * b
def _py_div(a, b): return a // b
def _py_full_adder(a, b, c):
    total = a + b + c
    return (total % 3, total // 3)


N = 1_000_000


def bench(label, py_fn, native_fn, args_fn):
    args = [args_fn() for _ in range(N)]

    t0 = time.perf_counter()
    for a in args:
        py_fn(*a)
    py_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    for a in args:
        native_fn(*a)
    native_time = time.perf_counter() - t0

    speedup = py_time / native_time if native_time > 0 else float("inf")
    print(f"Python {label}: {py_time:.3f}s")
    print(f"Native {label}: {native_time:.3f}s")
    print(f"Speedup: {speedup:.1f}x")
    print()
    return py_time, native_time, speedup


def main():
    print("=" * 50)
    print("TERNARY CPU — Native Backend Benchmark")
    print(f"Operations per test: {N:,}")
    print("=" * 50)
    print()

    if not NATIVE_AVAILABLE:
        print("WARNING: Native backend not available. Build libternary.so first.")
        print("  cd src/trinary/native && make")
        return

    rng = random.Random(42)

    def int_pair():
        return (rng.randint(-10000, 10000), rng.randint(-10000, 10000))

    def non_zero_pair():
        a = rng.randint(-10000, 10000)
        b = rng.randint(-10000, 10000)
        while b == 0:
            b = rng.randint(-10000, 10000)
        return (a, b)

    def trit_triple():
        return (rng.randint(0, 2), rng.randint(0, 2), rng.randint(0, 2))

    print("--- Integer Arithmetic ---")
    bench("ADD", _py_add, native_add, int_pair)
    bench("SUB", _py_sub, native_sub, int_pair)
    bench("MUL", _py_mul, native_mul, int_pair)
    bench("DIV", _py_div, native_div, non_zero_pair)

    print("--- Trit-level Full Adder ---")
    bench("FULL_ADDER", _py_full_adder, native_full_adder, trit_triple)

    print("=" * 50)
    print("Benchmark complete.")
    print("=" * 50)


if __name__ == "__main__":
    main()

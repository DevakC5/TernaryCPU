"""Benchmarking utilities for ternary neural network operations.

Measures throughput for inference, training, and tensor operations.
"""

import time

from trinary.ai.perceptron import Perceptron
from trinary.ai.trit_tensor import TritTensor
from trinary.ai.ternary_nn import TernaryNeuralNetwork
from trinary.ai.trainer import TernaryTrainer
from trinary.ai.datasets import AND_DATASET


def _format_ops(ops_per_sec):
    """Format operations per second with appropriate suffix."""
    if ops_per_sec >= 1_000_000:
        return f"{ops_per_sec / 1_000_000:.2f}M ops/s"
    if ops_per_sec >= 1_000:
        return f"{ops_per_sec / 1_000:.2f}K ops/s"
    return f"{ops_per_sec:.2f} ops/s"


def benchmark_perceptron(n_runs=10000):
    """Benchmark perceptron forward pass speed.

    Args:
        n_runs: Number of forward passes to time.

    Returns:
        Tuple of (ops_per_sec, total_time_seconds).
    """
    p = Perceptron([2, 0, 2, 1, 2])
    inputs = [2, 2, 0, 1, 1]
    start = time.perf_counter()
    for _ in range(n_runs):
        p.forward(inputs)
    elapsed = time.perf_counter() - start
    ops = n_runs / elapsed
    return ops, elapsed


def benchmark_matmul(n_runs=5000):
    """Benchmark matrix multiplication on TritTensor.

    Multiplies two small (4×4) matrices.

    Args:
        n_runs: Number of matmul calls to time.

    Returns:
        Tuple of (ops_per_sec, total_time_seconds, shape).
    """
    a = TritTensor([
        [2, 0, 1, 0],
        [0, 2, 0, 1],
        [1, 0, 2, 0],
        [0, 1, 0, 2],
    ])
    b = TritTensor([
        [0, 1, 0, 2],
        [2, 0, 1, 0],
        [0, 2, 0, 1],
        [1, 0, 2, 0],
    ])
    start = time.perf_counter()
    for _ in range(n_runs):
        a.matmul(b)
    elapsed = time.perf_counter() - start
    ops = n_runs / elapsed
    return ops, elapsed, (a.shape, b.shape)


def benchmark_network(n_runs=5000):
    """Benchmark a multi-layer network forward pass.

    Uses a 3-layer network with 4 inputs, 3 hidden, 2 output.

    Args:
        n_runs: Number of forward passes to time.

    Returns:
        Tuple of (ops_per_sec, total_time_seconds, layer_sizes).
    """
    net = TernaryNeuralNetwork([
        [Perceptron([2, 0, 1, 2]),
         Perceptron([1, 2, 0, 1]),
         Perceptron([0, 1, 2, 0])],
        [Perceptron([2, 0, 1]),
         Perceptron([1, 2, 0])],
    ])
    inputs = [2, 1, 0, 2]
    start = time.perf_counter()
    for _ in range(n_runs):
        net.forward(inputs)
    elapsed = time.perf_counter() - start
    ops = n_runs / elapsed
    return ops, elapsed, net.layer_sizes


def benchmark_training(n_runs=1000):
    """Benchmark training epoch throughput.

    Trains a perceptron on the AND dataset.

    Args:
        n_runs: Number of full training runs to time.

    Returns:
        Tuple of (epochs_per_sec, total_time_seconds).
    """
    start = time.perf_counter()
    for _ in range(n_runs):
        p = Perceptron([1, 1], bias=1)
        t = TernaryTrainer(p, learning_rate=1, max_epochs=20, verbose=False)
        t.fit_and()
    elapsed = time.perf_counter() - start
    total_epochs = n_runs * 20
    eps = total_epochs / elapsed
    return eps, elapsed


def benchmark_hillclimb(n_runs=100):
    """Benchmark hill-climbing training on XOR.

    Args:
        n_runs: Number of training runs.

    Returns:
        Tuple of (epochs_per_sec, total_time_seconds).
    """
    from trinary.ai.optimizers import TernaryHillClimber
    start = time.perf_counter()
    for _ in range(n_runs):
        net = TernaryNeuralNetwork([
            [Perceptron([1, 1], bias=1),
             Perceptron([1, 1], bias=1)],
            [Perceptron([1, 1], bias=1)],
        ])
        climber = TernaryHillClimber(max_attempts=10, improvement_threshold=0.0)
        t = TernaryTrainer(
            net, max_epochs=50, optimizer=climber, verbose=False
        )
        from trinary.ai.datasets import XOR_DATASET
        t.train(XOR_DATASET)
    elapsed = time.perf_counter() - start
    total_epochs = n_runs * 50
    eps = total_epochs / elapsed
    return eps, elapsed


def run_all():
    """Run all benchmarks and print results."""
    print("=" * 55)
    print("Ternary Neural Network — Benchmarks")
    print("=" * 55)
    print()
    ops, sec = benchmark_perceptron()
    print(f"Perceptron forward pass:")
    print(f"  {_format_ops(ops)}  ({sec:.4f}s for 10000 runs)")
    print()
    ops, sec, (sa, sb) = benchmark_matmul()
    print(f"Matrix multiplication ({sa[0]}×{sa[1]} · {sb[0]}×{sb[1]}):")
    print(f"  {_format_ops(ops)}  ({sec:.4f}s for 5000 runs)")
    print()
    ops, sec, sizes = benchmark_network()
    print(f"Network forward pass (layers: {sizes}):")
    print(f"  {_format_ops(ops)}  ({sec:.4f}s for 5000 runs)")
    print()
    eps, sec = benchmark_training()
    print(f"Perceptron training (SGD, AND, 20 epochs):")
    print(f"  {_format_ops(eps)}  ({sec:.4f}s for 1000 runs)")
    print()
    eps, sec = benchmark_hillclimb()
    print(f"Multi-layer training (HillClimb, XOR, 50 epochs):")
    print(f"  {_format_ops(eps)}  ({sec:.4f}s for 100 runs)")
    print()


if __name__ == "__main__":
    run_all()

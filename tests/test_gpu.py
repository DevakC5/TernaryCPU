"""Tests for the Ternary GPU mode."""

import pytest
from trinary.accelerator.gpu import (
    TernaryGPU, Workgroup, ProcessingElement
)
from trinary.accelerator.viz import (
    render_simd_lanes,
    render_tensor_matrix,
    render_matmul,
    render_packed_trits,
    render_accelerator,
    render_pipeline,
)


class TestProcessingElement:
    def test_create(self):
        pe = ProcessingElement(0)
        assert pe.pe_id == 0

    def test_execute_add(self):
        pe = ProcessingElement(0)
        pe.load([2, 0, 2])
        pe.execute("add", other=[0, 2, 0])
        assert pe.result == [1, 1, 1]

    def test_execute_threshold(self):
        pe = ProcessingElement(0)
        pe.load([0, 1, 2])
        pe.execute("threshold")
        assert pe.result == [1, 2, 2]


class TestWorkgroup:
    def test_create(self):
        wg = Workgroup(0, num_pes=4)
        assert wg.wg_id == 0
        assert len(wg.pes) == 4

    def test_broadcast(self):
        wg = Workgroup(0, num_pes=2)
        wg.broadcast([2, 0])
        for pe in wg.pes:
            assert pe.local_mem.to_list() == [2, 0]

    def test_execute_kernel_add(self):
        wg = Workgroup(0, num_pes=2)
        wg.broadcast([2, 0, 2, 0])
        results = wg.execute_kernel("add", other=[0, 2, 0, 2])
        assert len(results) == 2


class TestTernaryGPU:
    def test_create_default(self):
        gpu = TernaryGPU()
        assert len(gpu.workgroups) == 2
        assert len(gpu.workgroups[0].pes) == 4

    def test_dispatch_kernel(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=2)
        results = gpu.dispatch_kernel("threshold", [[0, 1], [2, 0]])
        assert len(results) == 2
        assert gpu.cycles == 2

    def test_dispatch_kernel_add(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=2)
        results = gpu.dispatch_kernel(
            "add",
            [[2, 0], [2, 0]],
        )
        assert len(results) == 2

    def test_pipeline_add(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=2)
        result = gpu.pipeline_add([2, 0, 2, 0], [0, 2, 0, 2])
        assert len(result) > 0
        assert gpu.cycles > 0

    def test_matmul_parallel(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=2)
        a = [[2, 0], [0, 2]]
        b = [[2, 0], [0, 2]]
        result = gpu.matmul_parallel(a, b)
        assert len(result) == 2

    def test_stats(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4)
        stats = gpu.stats()
        assert "TernaryGPU" in stats
        assert "Workgroups: 2" in stats
        assert "Total PEs:  8" in stats


class TestVisualization:
    def test_render_simd_lanes(self):
        out = render_simd_lanes([2, 0, 1, 2])
        assert "Lane0" in out
        assert "Lane3" in out

    def test_render_tensor_matrix(self):
        out = render_tensor_matrix([[2, 0], [0, 2]])
        assert "2×2" in out
        assert "┌" in out

    def test_render_matmul(self):
        a = [[2, 0], [0, 2]]
        b = [[2, 0], [0, 2]]
        out = render_matmul(a, b)
        assert "Matrix Multiply" in out
        assert "×" in out

    def test_render_matmul_with_result(self):
        a = [[2, 0], [0, 2]]
        b = [[2, 0], [0, 2]]
        c = [[2, 0], [0, 2]]
        out = render_matmul(a, b, result=c)
        assert "C" in out

    def test_render_packed_trits(self):
        out = render_packed_trits([0, 1, 2, 0, 1, 2, 0, 1])
        assert "@0000" in out

    def test_render_accelerator(self):
        from trinary.accelerator import TernaryTensorAccelerator
        accel = TernaryTensorAccelerator()
        accel.memory.allocate([2, 0, 2])
        out = render_accelerator(accel)
        assert "Accelerator State" in out

    def test_render_pipeline(self):
        out = render_pipeline(["load", "matmul", "act"])
        assert "load" in out
        assert "matmul" in out
        assert "act" in out

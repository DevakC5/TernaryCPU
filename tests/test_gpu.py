"""Tests for the Ternary GPU mode."""

import pytest
from trinary.accelerator.gpu import (
    TernaryGPU, Workgroup, ProcessingElement, Warp, Stream
)
from trinary.accelerator.viz import (
    render_simd_lanes,
    render_tensor_matrix,
    render_matmul,
    render_packed_trits,
    render_accelerator,
    render_pipeline,
    render_gpu,
    render_warp,
    render_streams,
)


class TestProcessingElement:
    def test_create(self):
        pe = ProcessingElement(0)
        assert pe.pe_id == 0
        assert pe.warp_id is None

    def test_create_with_warp(self):
        pe = ProcessingElement(5, warp_id=2)
        assert pe.pe_id == 5
        assert pe.warp_id == 2

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

    def test_execute_sum(self):
        pe = ProcessingElement(0)
        pe.load([2, 0, 2])
        pe.execute("sum")
        assert pe.result == 1  # signed: 1 + (-1) + 1 = 1

    def test_execute_max(self):
        pe = ProcessingElement(0)
        pe.load([2, 0, 1])
        pe.execute("max")
        assert pe.result == 1

    def test_execute_min(self):
        pe = ProcessingElement(0)
        pe.load([2, 0, 1])
        pe.execute("min")
        assert pe.result == -1

    def test_execute_no_op(self):
        pe = ProcessingElement(0)
        pe.load([2, 1, 0])
        pe.execute("unknown_op")
        assert pe.result == [2, 1, 0]

    def test_reset(self):
        pe = ProcessingElement(0)
        pe.load([2, 1])
        pe.execute("threshold")
        assert pe.result is not None
        pe.reset()
        assert pe.result is None
        assert len(pe.data) == 0

    def test_cycles_increment(self):
        pe = ProcessingElement(0)
        pe.load([1, 1, 1])
        pe.execute("add", other=[1, 1, 1])
        assert pe.cycles == 1
        pe.execute("threshold")
        assert pe.cycles == 2


class TestWarp:
    def test_create(self):
        w = Warp(0, size=4)
        assert w.warp_id == 0
        assert w.size == 4
        assert len(w.pes) == 0
        assert w.active is True

    def test_add_pe(self):
        w = Warp(0, size=2)
        pe0 = ProcessingElement(0)
        pe1 = ProcessingElement(1)
        w.add_pe(pe0)
        w.add_pe(pe1)
        assert len(w.pes) == 2
        assert pe0.warp_id == 0
        assert pe1.warp_id == 0

    def test_add_pe_exceeds_size(self):
        w = Warp(0, size=1)
        w.add_pe(ProcessingElement(0))
        w.add_pe(ProcessingElement(1))
        assert len(w.pes) == 1

    def test_execute_kernel(self):
        w = Warp(0, size=2)
        w.add_pe(ProcessingElement(0))
        w.add_pe(ProcessingElement(1))
        results = w.execute_kernel("threshold", data_slices=[[0, 1], [2, 0]])
        assert len(results) == 2
        assert results[0] == [1, 2]
        assert results[1] == [2, 1]

    def test_broadcast(self):
        w = Warp(0, size=2)
        w.add_pe(ProcessingElement(0))
        w.add_pe(ProcessingElement(1))
        w.broadcast([2, 0])
        for pe in w.pes:
            assert pe.data == [2, 0]

    def test_active_count(self):
        w = Warp(0, size=2)
        pe0 = ProcessingElement(0)
        pe1 = ProcessingElement(1)
        w.add_pe(pe0)
        w.add_pe(pe1)
        assert w.active_count() == 2
        pe0.active = False
        assert w.active_count() == 1


class TestWorkgroup:
    def test_create_default(self):
        wg = Workgroup(0, num_pes=8, warp_size=4)
        assert wg.wg_id == 0
        assert len(wg.pes) == 8
        assert len(wg.warps) == 2

    def test_create_small(self):
        wg = Workgroup(0, num_pes=2, warp_size=4)
        assert wg.pe_count() == 2
        assert wg.num_warps() == 1

    def test_build_warps(self):
        wg = Workgroup(0, num_pes=16, warp_size=4)
        assert wg.num_warps() == 4
        for warp in wg.warps:
            assert len(warp.pes) == 4

    def test_broadcast(self):
        wg = Workgroup(0, num_pes=4, warp_size=2)
        wg.broadcast([2, 0, 2])
        for pe in wg.pes:
            assert pe.data == [2, 0, 2]

    def test_shared_memory(self):
        wg = Workgroup(0, num_pes=4, warp_size=2)
        wg.shared_store([2, 1, 0, 2])
        assert wg.shared_load() == [2, 1, 0, 2]

    def test_barrier(self):
        wg = Workgroup(0, num_pes=4, warp_size=2)
        assert wg.barrier_count == 0
        wg.barrier()
        assert wg.barrier_count == 1

    def test_execute_kernel(self):
        wg = Workgroup(0, num_pes=4, warp_size=2)
        results = wg.execute_kernel("threshold")
        assert len(results) == 4

    def test_execute_warp(self):
        wg = Workgroup(0, num_pes=8, warp_size=4)
        results = wg.execute_warp(0, "threshold")
        assert len(results) == 4

    def test_execute_warp_invalid(self):
        wg = Workgroup(0, num_pes=4, warp_size=2)
        results = wg.execute_warp(99, "threshold")
        assert results == []


class TestStream:
    def test_create(self):
        s = Stream(0)
        assert s.stream_id == 0
        assert s.has_work() is False

    def test_enqueue_dequeue(self):
        s = Stream(0)
        s.enqueue("add", [0, 1])
        assert s.has_work() is True
        item = s.dequeue()
        assert item[0] == "add"
        assert item[1] == [0, 1]
        assert s.has_work() is False

    def test_dequeue_empty(self):
        s = Stream(0)
        assert s.dequeue() is None

    def test_mark_complete(self):
        s = Stream(0)
        s.mark_complete([1, 2, 3])
        assert s.get_completed() == [[1, 2, 3]]


class TestTernaryGPU:
    def test_create_default(self):
        gpu = TernaryGPU()
        assert len(gpu.workgroups) == 4
        assert len(gpu.workgroups[0].pes) == 16

    def test_create_custom(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=8, warp_size=4)
        assert len(gpu.workgroups) == 2
        assert len(gpu.workgroups[0].pes) == 8
        assert gpu.warp_size == 4

    def test_total_pes(self):
        gpu = TernaryGPU(num_workgroups=4, pes_per_wg=16)
        assert gpu.total_pes() == 64

    def test_total_warps(self):
        gpu = TernaryGPU(num_workgroups=4, pes_per_wg=16, warp_size=4)
        assert gpu.total_warps() == 16

    def test_dispatch_kernel(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        results = gpu.dispatch_kernel("threshold", [[0, 1], [2, 0]])
        assert len(results) == 2
        assert gpu.cycles == 2

    def test_dispatch_kernel_add(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        results = gpu.dispatch_kernel(
            "add",
            [[2, 0, 2, 0], [0, 2, 0, 2]],
        )
        assert len(results) == 2

    def test_dispatch_grid(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        grid = gpu.dispatch_grid("threshold", [0, 1, 2, 0], (2, 1))
        assert len(grid) == 1
        assert len(grid[0]) == 2

    def test_create_stream(self):
        gpu = TernaryGPU()
        sid = gpu.create_stream()
        assert sid == 0
        assert 0 in gpu.streams

    def test_dispatch_stream(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        sid = gpu.create_stream()
        gpu.streams[sid].enqueue("threshold", [0, 1])
        result = gpu.dispatch_stream(sid)
        assert result is not None

    def test_dispatch_stream_invalid(self):
        gpu = TernaryGPU()
        assert gpu.dispatch_stream(99) is None

    def test_run_streams_concurrent(self):
        gpu = TernaryGPU(num_workgroups=4, pes_per_wg=4, warp_size=2)
        s0 = gpu.create_stream()
        s1 = gpu.create_stream()
        gpu.streams[s0].enqueue("threshold", [0, 1])
        gpu.streams[s1].enqueue("threshold", [2, 0])
        results = gpu.run_streams_concurrent()
        assert len(results) == 2

    def test_pipeline_add(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        result = gpu.pipeline_add([2, 0, 2, 0], [0, 2, 0, 2])
        assert len(result) > 0
        assert gpu.cycles > 0

    def test_matmul_parallel(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        a = [[2, 0], [0, 2]]
        b = [[2, 0], [0, 2]]
        result = gpu.matmul_parallel(a, b)
        assert len(result) == 2

    def test_matmul_parallel_larger(self):
        gpu = TernaryGPU(num_workgroups=4, pes_per_wg=8, warp_size=4)
        a = [[2, 0, 1], [0, 2, 1], [1, 1, 2], [2, 1, 0]]
        b = [[2, 0, 1], [0, 2, 1], [1, 1, 2]]
        result = gpu.matmul_parallel(a, b)
        assert len(result) == 4
        assert all(len(row) == 3 for row in result)

    def test_matmul_parallel_empty(self):
        gpu = TernaryGPU()
        assert gpu.matmul_parallel([], []) == []
        assert gpu.matmul_parallel([[2]], []) == []

    def test_reduce_sum(self):
        gpu = TernaryGPU(num_workgroups=4, pes_per_wg=16, warp_size=4)
        result = gpu.reduce([2, 0, 2, 0, 2, 0, 2, 0], op="sum")
        assert isinstance(result, int)

    def test_reduce_max(self):
        gpu = TernaryGPU(num_workgroups=4, pes_per_wg=16, warp_size=4)
        result = gpu.reduce([2, 0, 1, 0], op="max")
        assert isinstance(result, int)

    def test_reduce_min(self):
        gpu = TernaryGPU(num_workgroups=4, pes_per_wg=16, warp_size=4)
        result = gpu.reduce([2, 0, 1, 0], op="min")
        assert isinstance(result, int)

    def test_reduce_empty(self):
        gpu = TernaryGPU()
        assert gpu.reduce([], op="sum") == 0

    def test_scan(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        result = gpu.scan([2, 0, 2, 0])
        assert len(result) == 4
        assert all(v in (0, 1, 2) for v in result)

    def test_scan_empty(self):
        gpu = TernaryGPU()
        assert gpu.scan([]) == []

    def test_transpose(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        result = gpu.transpose([[2, 0, 1], [0, 2, 1]])
        assert result == [[2, 0], [0, 2], [1, 1]]

    def test_transpose_empty(self):
        gpu = TernaryGPU()
        assert gpu.transpose([]) == []

    def test_fused_linear(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        w = [[2, 0], [0, 2]]
        x = [2, 0]
        result = gpu.fused_linear(w, x)
        assert len(result) == 2

    def test_fused_linear_with_bias(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        w = [[2, 0], [0, 2]]
        x = [2, 0]
        b = [1, 1]
        result = gpu.fused_linear(w, x, bias=b)
        assert len(result) == 2

    def test_fused_linear_batch(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        w = [[2, 0], [0, 2]]
        x = [[2, 0], [0, 2]]
        result = gpu.fused_linear(w, x)
        assert len(result) == 2

    def test_elementwise_fused(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        result = gpu.elementwise_fused([2, 0, 2], [0, 2, 0])
        assert len(result) == 3

    def test_elementwise_fused_mismatch(self):
        gpu = TernaryGPU()
        with pytest.raises(ValueError):
            gpu.elementwise_fused([2, 0], [0])

    def test_batch_dispatch(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=4, warp_size=2)
        batch = [[2, 0], [0, 2], [1, 1]]
        results = gpu.batch_dispatch("threshold", batch)
        assert len(results) == 2

    def test_stats(self):
        gpu = TernaryGPU(num_workgroups=4, pes_per_wg=16, warp_size=4)
        stats = gpu.stats()
        assert "TernaryGPU" in stats
        assert "Workgroups:  4" in stats
        assert "Total PEs:   64" in stats
        assert "Total warps: 16" in stats

    def test_arch_summary(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=8, warp_size=4)
        summary = gpu.arch_summary()
        assert "Ternary GPU Architecture" in summary
        assert "WG[0]" in summary
        assert "WG[1]" in summary


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

    def test_render_gpu(self):
        gpu = TernaryGPU(num_workgroups=2, pes_per_wg=8, warp_size=4)
        out = render_gpu(gpu)
        assert "Ternary GPU Architecture" in out
        assert "Workgroup 0" in out
        assert "Total PEs:   16" in out

    def test_render_warp(self):
        gpu = TernaryGPU(num_workgroups=1, pes_per_wg=4, warp_size=2)
        out = render_warp(gpu.workgroups[0].warps[0])
        assert "Warp 0" in out
        assert "PE0" in out

    def test_render_streams_empty(self):
        gpu = TernaryGPU()
        out = render_streams(gpu)
        assert "No streams" in out

    def test_render_streams(self):
        gpu = TernaryGPU()
        gpu.create_stream()
        out = render_streams(gpu)
        assert "Stream 0" in out

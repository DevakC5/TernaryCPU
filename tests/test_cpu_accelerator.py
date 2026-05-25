"""CPU + Tensor Accelerator integration tests."""

from trinary.cpu import CPU
from trinary.accelerator import TernaryTensorAccelerator


class TestCPUHasAccelerator:
    def test_cpu_has_accel(self):
        cpu = CPU()
        assert hasattr(cpu, 'accel')
        assert isinstance(cpu.accel, TernaryTensorAccelerator)


class TestTLOADW:
    def test_loads_data_into_accelerator(self):
        cpu = CPU()
        for i in range(4):
            cpu.memory.store(100 + i, str([0, 1, 2, 0][i]))
        cpu.load_program(["TLOADW 100 2 2"])
        cpu.run(verbose=False)
        tid = int(cpu.registers.store("R0"))
        data = cpu.accel.memory.load_list(tid)
        assert data == [0, 1, 2, 0]

    def test_store_tensor_id_in_r0(self):
        cpu = CPU()
        for i in range(4):
            cpu.memory.store(50 + i, str(i % 3))
        cpu.load_program(["TLOADW 50 2 2"])
        cpu.run(verbose=False)
        tid = int(cpu.registers.store("R0"))
        assert isinstance(tid, int)
        assert tid >= 0


class TestTSTOREW:
    def test_stores_tensor_to_cpu_memory(self):
        cpu = CPU()
        tid = cpu.accel.memory.allocate([2, 0, 2, 0])
        cpu.load_program([f"TSTOREW {tid} 200"])
        cpu.run(verbose=False)
        for i in range(4):
            assert cpu.memory.load(200 + i) == str([2, 0, 2, 0][i])


class TestTVECADD:
    def test_vector_add_via_cpu(self):
        cpu = CPU()
        cpu.accel.memory.allocate([2, 0, 2])  # tid=0
        cpu.accel.memory.allocate([0, 2, 0])  # tid=1
        cpu.load_program(["TVECADD 0 0 1"])
        cpu.run(verbose=False)
        from trinary.conversion import ternary_to_decimal as t2d
        result_tid = int(t2d(cpu.registers.store("R0")))
        result = cpu.accel.memory.load_list(result_tid)
        assert result == [1, 1, 1]


class TestTMATMUL:
    def test_matmul_via_cpu(self):
        cpu = CPU()
        cpu.accel.memory.allocate(
            [2, 0, 0, 2], shape=(2, 2)
        )  # tid=0
        cpu.accel.memory.allocate(
            [2, 0, 0, 2], shape=(2, 2)
        )  # tid=1
        cpu.load_program(["TMATMUL 0 0 1"])
        cpu.run(verbose=False)
        from trinary.conversion import ternary_to_decimal as t2d
        result_tid = int(t2d(cpu.registers.store("R0")))
        result = cpu.accel.memory.load_list(result_tid)
        assert len(result) == 4


class TestTDOT:
    def test_dot_product_via_cpu(self):
        cpu = CPU()
        cpu.accel.memory.allocate([2, 2])  # tid=0
        cpu.accel.memory.allocate([2, 2])  # tid=1
        cpu.load_program(["TDOT 0 1"])
        cpu.run(verbose=False)
        from trinary.conversion import ternary_to_decimal as t2d
        result = int(t2d(cpu.registers.store("R0")))
        assert result == 2


class TestTACT:
    def test_activation_via_cpu(self):
        cpu = CPU()
        cpu.accel.memory.allocate([0, 1, 2])  # tid=0
        cpu.load_program(["TACT 0 0"])
        cpu.run(verbose=False)
        data = cpu.accel.memory.load_list(0)
        assert data == [1, 2, 2]


class TestAcceleratorReset:
    def test_reset_creates_fresh_accel(self):
        cpu = CPU()
        tid_a = cpu.accel.memory.allocate([2, 0])
        assert cpu.accel.memory.load_list(tid_a) == [2, 0]
        cpu.reset()
        import pytest
        with pytest.raises(KeyError):
            cpu.accel.memory.load_list(tid_a)


class TestTLOADWWithRegisters:
    def test_addr_from_register(self):
        cpu = CPU()
        for i in range(4):
            cpu.memory.store(3 + i, str([0, 1, 2, 1][i]))
        cpu.load_program([
            "LOAD R0 10",
            "LOAD R1 2",
            "LOAD R2 2",
            "TLOADW R0 R1 R2",
        ])
        cpu.run(verbose=False)
        from trinary.conversion import ternary_to_decimal as t2d
        tid = int(t2d(cpu.registers.store("R0")))
        data = cpu.accel.memory.load_list(tid)
        assert data == [0, 1, 2, 1]


class TestAccelProgramFlow:
    def test_load_dot_store(self):
        cpu = CPU()
        for i in range(4):
            cpu.memory.store(10 + i, str([2, 0, 2, 0][i]))
        cpu.load_program([
            "TLOADW 10 4 1",
            "TLOADW 10 4 1",
            "TDOT 0 1",
        ])
        cpu.run(verbose=False)
        from trinary.conversion import ternary_to_decimal as t2d
        result = int(t2d(cpu.registers.store("R0")))
        assert result == 4

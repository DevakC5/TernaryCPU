from trinary.accelerator.accelerator import TernaryTensorAccelerator
from trinary.accelerator.instruction_set import Instruction, Opcode


class TestConstruction:
    def test_default(self):
        accel = TernaryTensorAccelerator()
        assert accel.memory.capacity == 64
        assert accel.simd.lanes == 4

    def test_custom(self):
        accel = TernaryTensorAccelerator(mem_capacity=16, simd_lanes=8)
        assert accel.memory.capacity == 16
        assert accel.simd.lanes == 8


class TestTLoad:
    def test_allocates_tensor(self):
        accel = TernaryTensorAccelerator()
        tid = accel.execute(Instruction(Opcode.TLOAD))
        assert tid is not None
        assert tid in accel.memory._slots


class TestTVecAdd:
    def test_add(self):
        accel = TernaryTensorAccelerator()
        tid_a = accel.memory.allocate([2, 0, 1, 2])
        tid_b = accel.memory.allocate([0, 2, 1, 0])
        tid_c = accel.memory.allocate(length=4)
        result = accel.execute(
            Instruction(Opcode.TVECADD, dest=tid_c, src_a=tid_a, src_b=tid_b)
        )
        assert len(result) == 4
        assert all(x in (0, 1, 2) for x in result)


class TestTVecMul:
    def test_mul(self):
        accel = TernaryTensorAccelerator()
        tid_a = accel.memory.allocate([2, 0, 2, 0])
        tid_b = accel.memory.allocate([2, 0, 2, 0])
        tid_c = accel.memory.allocate(length=4)
        result = accel.execute(
            Instruction(Opcode.TVECMUL, dest=tid_c, src_a=tid_a, src_b=tid_b)
        )
        assert all(x in (0, 1, 2) for x in result)


class TestTDot:
    def test_dot(self):
        accel = TernaryTensorAccelerator()
        tid_a = accel.memory.allocate([2, 2])
        tid_b = accel.memory.allocate([2, 2])
        result = accel.execute(
            Instruction(Opcode.TDOT, dest=None, src_a=tid_a, src_b=tid_b)
        )
        # (+1)*(+1) + (+1)*(+1) = 2
        assert result == 2


class TestTMatMul:
    def test_matmul(self):
        accel = TernaryTensorAccelerator()
        a = [v for row in [[2, 0], [0, 2]] for v in row]
        b = [v for row in [[2, 0], [0, 2]] for v in row]
        tid_a = accel.memory.allocate(a, shape=(2, 2))
        tid_b = accel.memory.allocate(b, shape=(2, 2))
        result = accel.execute(
            Instruction(Opcode.TMATMUL, src_a=tid_a, src_b=tid_b)
        )
        assert result is not None
        assert result[0][0] == 2
        assert result[1][1] == 2


class TestTAct:
    def test_activation_step(self):
        accel = TernaryTensorAccelerator()
        tid = accel.memory.allocate([0, 1, 2])
        tid_out = accel.memory.allocate(length=3)
        result = accel.execute(
            Instruction(Opcode.TACT, dest=tid_out, src_a=tid, extra=0)
        )
        assert len(result) == 3
        assert all(x in (0, 1, 2) for x in result)


class TestRunProgram:
    def test_program(self):
        accel = TernaryTensorAccelerator()
        tid_a = accel.memory.allocate([2, 0, 1, 2])
        tid_b = accel.memory.allocate([0, 2, 1, 0])
        tid_c = accel.memory.allocate(length=4)
        program = [
            Instruction(Opcode.TVECADD, dest=tid_c, src_a=tid_a, src_b=tid_b),
            Instruction(Opcode.TVECMUL, dest=tid_c, src_a=tid_a, src_b=tid_b),
        ]
        results = accel.run_program(program)
        assert len(results) == 2

    def test_cycles_tracked(self):
        accel = TernaryTensorAccelerator()
        tid_a = accel.memory.allocate([2, 0])
        tid_b = accel.memory.allocate([0, 2])
        tid_c = accel.memory.allocate(length=2)
        program = [
            Instruction(Opcode.TVECADD, dest=tid_c, src_a=tid_a, src_b=tid_b),
        ]
        accel.run_program(program)
        assert accel.cycles >= 1


class TestFused:
    def test_fused_linear(self):
        accel = TernaryTensorAccelerator()
        tid_w = accel.memory.allocate([2, 0, 0, 2])  # 2x2 flattened
        tid_x = accel.memory.allocate([2, 0])
        tid_b = accel.memory.allocate([1, 1])
        result = accel.execute(
            Instruction(Opcode.TFUSED, dest=tid_b, src_a=tid_w, src_b=tid_x, extra=0)
        )
        assert result is not None

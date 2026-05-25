from trinary.accelerator.simd import SIMDProcessor


class TestConstruction:
    def test_default_lanes(self):
        simd = SIMDProcessor()
        assert simd.lanes == 4

    def test_custom_lanes(self):
        simd = SIMDProcessor(lanes=8)
        assert simd.lanes == 8

    def test_invalid_lanes_raises(self):
        try:
            SIMDProcessor(lanes=0)
            assert False
        except ValueError:
            pass


class TestLoad:
    def test_load(self):
        simd = SIMDProcessor(lanes=4)
        simd.load([2, 0, 1, 2])
        assert simd.registers == [2, 0, 1, 2]

    def test_load_wrong_length_raises(self):
        simd = SIMDProcessor(lanes=4)
        try:
            simd.load([2, 0])
            assert False
        except ValueError:
            pass

    def test_load_invalid_trit_raises(self):
        simd = SIMDProcessor(lanes=4)
        try:
            simd.load([0, 1, 2, 3])
            assert False
        except ValueError:
            pass


class TestArithmetic:
    def test_add(self):
        simd = SIMDProcessor(lanes=4)
        simd.load([2, 0, 1, 2])
        simd.add([0, 2, 1, 0])
        # (+1)+(-1)=0->1, (-1)+(+1)=0->1, 0+0=0->1, (+1)+(-1)=0->1
        assert simd.registers == [1, 1, 1, 1]

    def test_sub(self):
        simd = SIMDProcessor(lanes=4)
        simd.load([2, 0, 2, 0])
        simd.sub([0, 2, 0, 2])
        assert simd.registers == [2, 0, 2, 0]

    def test_mul(self):
        simd = SIMDProcessor(lanes=4)
        simd.load([2, 0, 2, 0])
        simd.mul([2, 0, 0, 2])
        assert simd.registers == [2, 2, 0, 0]

    def test_max(self):
        simd = SIMDProcessor(lanes=4)
        simd.load([0, 1, 2, 0])
        simd.max([2, 0, 1, 2])
        assert simd.registers == [2, 1, 2, 2]

    def test_min(self):
        simd = SIMDProcessor(lanes=4)
        simd.load([0, 1, 2, 0])
        simd.min([2, 0, 1, 2])
        assert simd.registers == [0, 0, 1, 0]


class TestDotAndThreshold:
    def test_dot(self):
        simd = SIMDProcessor(lanes=4)
        simd.load([2, 0, 2, 0])
        result = simd.dot([2, 0, 2, 0])
        # (+1)*(+1) + (-1)*(-1) + (+1)*(+1) + (-1)*(-1) = 1+1+1+1 = 4
        assert result == 4

    def test_threshold(self):
        simd = SIMDProcessor(lanes=4)
        simd.load([2, 0, 1, 2])
        simd.threshold()
        assert simd.registers == [2, 0, 1, 2]  # all already step-outputs

    def test_clear(self):
        simd = SIMDProcessor(lanes=4)
        simd.load([2, 0, 1, 2])
        simd.clear(0)
        assert simd.registers == [0, 0, 0, 0]


class TestCycles:
    def test_cycles_increment(self):
        simd = SIMDProcessor(lanes=4)
        assert simd.cycles == 0
        simd.load([2, 0, 1, 2])
        assert simd.cycles == 1
        simd.add([0, 2, 1, 0])
        assert simd.cycles == 2

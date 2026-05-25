from trinary.accelerator.vector_ops import TritSIMD


class TestAdd:
    def test_add_basic(self):
        r = TritSIMD.add_vectors([2, 0, 2], [0, 2, 0])
        # (+1)+(-1)=0->1, (-1)+(+1)=0->1, (+1)+(-1)=0->1
        assert r == [1, 1, 1]

    def test_add_positive(self):
        r = TritSIMD.add_vectors([2, 2], [2, 0])
        assert r == [2, 1]  # 1+1=+3->2, 1+(-1)=0->1

    def test_length_mismatch_raises(self):
        try:
            TritSIMD.add_vectors([0, 1], [0])
            assert False
        except ValueError:
            pass


class TestSub:
    def test_sub_basic(self):
        r = TritSIMD.sub_vectors([2, 0], [0, 2])
        # (+1)-(-1)=+2->2, (-1)-(+1)=-2->0
        assert r == [2, 0]


class TestMul:
    def test_mul_basic(self):
        r = TritSIMD.mul_vectors([2, 0, 2], [2, 0, 0])
        # (1*1)=1->2, (-1*-1)=1->2, (1*-1)=-1->0
        assert r[0] == 2
        assert r[1] == 2
        assert r[2] == 0


class TestMaxMin:
    def test_max(self):
        assert TritSIMD.max_vectors([0, 1, 2], [2, 0, 1]) == [2, 1, 2]

    def test_min(self):
        assert TritSIMD.min_vectors([0, 1, 2], [2, 0, 1]) == [0, 0, 1]


class TestDot:
    def test_dot(self):
        r = TritSIMD.dot_product([2, 2], [2, 2])
        assert r == 2  # 1*1 + 1*1 = 2

    def test_dot_opposite(self):
        r = TritSIMD.dot_product([2, 2], [0, 0])
        assert r == -2  # 1*(-1) + 1*(-1) = -2

    def test_dot_length_mismatch_raises(self):
        try:
            TritSIMD.dot_product([0, 1], [0])
            assert False
        except ValueError:
            pass


class TestThreshold:
    def test_threshold(self):
        assert TritSIMD.ternary_threshold([-3, 0, 5]) == [0, 1, 2]


class TestScaledAdd:
    def test_scaled_add(self):
        r = TritSIMD.scaled_add([2, 0], [0, 2], scale_a=2, scale_b=1)
        # (2*1 + -1)=1->2, (2*(-1) + 1)=-1->0
        assert r == [2, 0]

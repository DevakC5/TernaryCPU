from trinary.accelerator.tensor_core import TensorCore


class TestMatMul:
    def test_square(self):
        core = TensorCore()
        a = [[2, 0], [0, 2]]
        b = [[2, 0], [0, 2]]
        c = core.matmul(a, b)
        assert c[0][0] == 2
        assert c[1][1] == 2

    def test_vector(self):
        core = TensorCore()
        a = [[2, 0, 2], [0, 2, 0]]
        b = [2, 0, 2]
        c = core.matmul(a, b)
        assert len(c) == 2
        assert all(x in (0, 1, 2) for x in c)

    def test_incompatible_raises(self):
        core = TensorCore()
        try:
            core.matmul([[0, 1]], [[0, 1, 2]])
            assert False
        except ValueError:
            pass

    def test_rectangular(self):
        core = TensorCore()
        a = [[2, 0, 2], [0, 2, 0], [2, 0, 2], [0, 2, 0]]
        b = [[2, 0], [0, 2], [2, 0]]
        c = core.matmul(a, b)
        assert len(c) == 4
        assert len(c[0]) == 2


class TestBatchMatMul:
    def test_batch(self):
        core = TensorCore()
        batch_a = [[[2, 0], [0, 2]], [[0, 2], [2, 0]]]
        batch_b = [[[2, 0], [0, 2]], [[2, 0], [0, 2]]]
        results = core.batch_matmul(batch_a, batch_b)
        assert len(results) == 2

    def test_size_mismatch_raises(self):
        core = TensorCore()
        try:
            core.batch_matmul([[[0]]], [[[0]], [[0]]])
            assert False
        except ValueError:
            pass


class TestFusedLinear:
    def test_basic(self):
        core = TensorCore()
        w = [[2, 0], [0, 2]]
        x = [2, 0]
        bias = [1, 1]
        out = core.fused_linear(w, x, bias)
        assert len(out) == 2

    def test_no_bias(self):
        core = TensorCore()
        w = [[2, 0, 2]]
        x = [2, 0, 2]
        out = core.fused_linear(w, x)
        assert len(out) == 1

    def test_bias_length_mismatch_raises(self):
        core = TensorCore()
        try:
            core.fused_linear([[2, 0]], [0, 0], bias=[1, 1, 1])
            assert False
        except ValueError:
            pass


class TestTensorAdd:
    def test_add(self):
        core = TensorCore()
        a = [[2, 0], [0, 2]]
        b = [[0, 2], [2, 0]]
        c = core.tensor_add(a, b)
        # (+1)+(-1)=0->1, (-1)+(+1)=0->1
        assert c[0] == [1, 1]
        assert c[1] == [1, 1]

    def test_shape_mismatch_raises(self):
        core = TensorCore()
        try:
            core.tensor_add([[0]], [[0, 0]])
            assert False
        except ValueError:
            pass


class TestTensorMul:
    def test_mul(self):
        core = TensorCore()
        a = [[2, 0, 2], [0, 2, 0]]
        b = [[2, 0, 2], [0, 2, 0]]
        c = core.tensor_mul(a, b)
        # (+1)*(+1)=+1->2, (-1)*(-1)=+1->2
        assert c[0] == [2, 2, 2]
        assert c[1] == [2, 2, 2]

from trinary.ai.trit_tensor import TritTensor


class TestValidation:
    def test_empty_list_raises(self):
        try:
            TritTensor([])
            assert False
        except ValueError:
            pass

    def test_invalid_digit_raises(self):
        try:
            TritTensor([0, 1, 3])
            assert False
        except ValueError:
            pass

    def test_negative_digit_raises(self):
        try:
            TritTensor([-1, 0, 2])
            assert False
        except ValueError:
            pass

    def test_invalid_in_matrix_raises(self):
        try:
            TritTensor([[0, 1], [2, 3]])
            assert False
        except ValueError:
            pass

    def test_jagged_rows_raise(self):
        try:
            TritTensor([[0, 1], [2]])
            assert False
        except ValueError:
            pass

    def test_valid_vector(self):
        t = TritTensor([0, 1, 2])
        assert t.shape == (3,)

    def test_valid_matrix(self):
        t = TritTensor([[0, 1], [2, 1]])
        assert t.shape == (2, 2)


class TestShape:
    def test_vector_shape(self):
        t = TritTensor([0, 1, 2, 0])
        assert t.shape == (4,)

    def test_matrix_shape(self):
        t = TritTensor([[0, 1, 2], [2, 1, 0]])
        assert t.shape == (2, 3)

    def test_is_vector(self):
        assert TritTensor([0, 1]).is_vector() is True
        assert TritTensor([[0, 1]]).is_vector() is False

    def test_is_matrix(self):
        assert TritTensor([[0, 1]]).is_matrix() is True
        assert TritTensor([0, 1]).is_matrix() is False


class TestTranspose:
    def test_transpose_matrix(self):
        t = TritTensor([[0, 1, 2], [2, 1, 0]])
        tt = t.transpose()
        assert tt.shape == (3, 2)
        assert tt.data == [[0, 2], [1, 1], [2, 0]]

    def test_transpose_square(self):
        t = TritTensor([[0, 1], [2, 1]])
        tt = t.transpose()
        assert tt.data == [[0, 2], [1, 1]]

    def test_transpose_vector(self):
        t = TritTensor([0, 1, 2])
        tt = t.transpose()
        assert tt.shape == (3,)
        assert tt.data == [0, 1, 2]


class TestFlatten:
    def test_flatten_matrix(self):
        t = TritTensor([[0, 1], [2, 1], [0, 2]])
        flat = t.flatten()
        assert flat.shape == (6,)
        assert flat.data == [0, 1, 2, 1, 0, 2]

    def test_flatten_vector(self):
        t = TritTensor([0, 1, 2])
        flat = t.flatten()
        assert flat.shape == (3,)
        assert flat.data == [0, 1, 2]


class TestDot:
    def test_dot_basic(self):
        a = TritTensor([2, 1, 0])     # [+1, 0, -1]
        b = TritTensor([2, 2, 0])     # [+1, +1, -1]
        result = a.dot(b)
        # (1*1 + 0*1 + (-1)*(-1)) = 1 + 0 + 1 = 2
        assert result == 2

    def test_dot_all_positive(self):
        a = TritTensor([2, 2])         # [+1, +1]
        b = TritTensor([2, 2])         # [+1, +1]
        result = a.dot(b)
        assert result == 2

    def test_dot_opposite(self):
        a = TritTensor([2, 2])         # [+1, +1]
        b = TritTensor([0, 0])         # [-1, -1]
        result = a.dot(b)
        assert result == -2

    def test_dot_length_mismatch_raises(self):
        try:
            TritTensor([0, 1]).dot(TritTensor([0, 1, 2]))
            assert False
        except ValueError:
            pass

    def test_dot_matrix_raises(self):
        try:
            TritTensor([[0, 1]]).dot(TritTensor([0, 1]))
            assert False
        except ValueError:
            pass


class TestMatMul:
    def test_matmul_vector(self):
        a = TritTensor([[2, 1, 0], [0, 1, 2]])  # 2x3
        b = TritTensor([2, 1, 0])               # 3
        result = a.matmul(b)
        assert result.shape == (2,)
        assert all(x in (0, 1, 2) for x in result.data)

    def test_matmul_matrix(self):
        a = TritTensor([[2, 0], [0, 2]])  # 2x2
        b = TritTensor([[2, 0], [0, 2]])  # 2x2
        result = a.matmul(b)
        assert result.shape == (2, 2)
        # [+1,-1; -1,+1] x [+1,-1; -1,+1] = [+2,+0; +0,+2] -> step -> [2,1; 1,2]
        assert result.data[0][0] == 2
        assert result.data[1][1] == 2

    def test_matmul_incompatible_raises(self):
        try:
            a = TritTensor([[0, 1], [2, 1]])
            b = TritTensor([[0, 1, 2]])
            a.matmul(b)
            assert False
        except ValueError:
            pass

    def test_matmul_vector_incompatible_raises(self):
        try:
            a = TritTensor([[0, 1], [2, 1]])
            b = TritTensor([0, 0, 0])
            a.matmul(b)
            assert False
        except ValueError:
            pass

    def test_matmul_requires_matrix(self):
        try:
            TritTensor([0, 1]).matmul(TritTensor([0, 1]))
            assert False
        except ValueError:
            pass


class TestApply:
    def test_apply_vector(self):
        t = TritTensor([0, 1, 2])
        result = t.apply(lambda x: 1)
        assert result.data == [1, 1, 1]

    def test_apply_matrix(self):
        t = TritTensor([[0, 1], [2, 1]])
        result = t.apply(lambda x: 2 if x == 0 else 0)
        assert result.data == [[2, 0], [0, 0]]


class TestToFromSigned:
    def test_to_signed_vector(self):
        t = TritTensor([0, 1, 2])
        signed = t.to_signed()
        assert signed == [-1, 0, 1]

    def test_to_signed_matrix(self):
        t = TritTensor([[0, 1], [2, 1]])
        signed = t.to_signed()
        assert signed == [[-1, 0], [1, 0]]

    def test_from_signed_vector(self):
        t = TritTensor([0, 0, 0])
        t.from_signed([-1, 0, 1])
        assert t.data == [0, 1, 2]

    def test_from_signed_matrix(self):
        t = TritTensor([[0, 0], [0, 0]])
        t.from_signed([[-1, 0], [1, 0]])
        assert t.data == [[0, 1], [2, 1]]

    def test_from_signed_wrong_size_raises(self):
        try:
            t = TritTensor([0, 0])
            t.from_signed([-1, 0, 1])
            assert False
        except ValueError:
            pass


class TestEquality:
    def test_equal_tensors(self):
        assert TritTensor([0, 1, 2]) == TritTensor([0, 1, 2])

    def test_unequal_tensors(self):
        assert TritTensor([0, 1, 2]) != TritTensor([2, 1, 0])

    def test_different_shapes(self):
        assert TritTensor([0, 1]) != TritTensor([[0, 1]])

from trinary.accelerator.packed_trits import PackedTritArray


class TestPacking:
    def test_empty(self):
        p = PackedTritArray()
        assert len(p) == 0
        assert list(p) == []

    def test_single_trit(self):
        p = PackedTritArray([2])
        assert p[0] == 2

    def test_four_trits(self):
        p = PackedTritArray([0, 1, 2, 0])
        assert list(p) == [0, 1, 2, 0]

    def test_many_trits(self):
        trits = [0, 1, 2] * 10
        p = PackedTritArray(trits)
        assert list(p) == trits
        assert len(p) == 30

    def test_invalid_digit_raises(self):
        try:
            PackedTritArray([0, 3])
            assert False
        except ValueError:
            pass


class TestGetSet:
    def test_get(self):
        p = PackedTritArray([2, 1, 0])
        assert p[0] == 2
        assert p[1] == 1
        assert p[2] == 0

    def test_set(self):
        p = PackedTritArray([0, 0, 0])
        p[1] = 2
        assert p[1] == 2

    def test_set_invalid_raises(self):
        p = PackedTritArray([0, 0])
        try:
            p[0] = 3
            assert False
        except ValueError:
            pass

    def test_negative_index(self):
        p = PackedTritArray([0, 1, 2])
        assert p[-1] == 2
        assert p[-3] == 0

    def test_index_error(self):
        p = PackedTritArray([0, 1])
        try:
            _ = p[5]
            assert False
        except IndexError:
            pass


class TestAppendExtend:
    def test_append(self):
        p = PackedTritArray()
        p.append(2)
        p.append(0)
        p.append(1)
        assert list(p) == [2, 0, 1]

    def test_extend(self):
        p = PackedTritArray([0, 1])
        p.extend([2, 0, 2])
        assert list(p) == [0, 1, 2, 0, 2]

    def test_extend_many(self):
        p = PackedTritArray()
        p.extend([0, 1, 2] * 50)
        assert len(p) == 150


class TestPop:
    def test_pop(self):
        p = PackedTritArray([0, 1, 2])
        v = p.pop()
        assert v == 2
        assert list(p) == [0, 1]

    def test_pop_index(self):
        p = PackedTritArray([0, 1, 2])
        v = p.pop(0)
        assert v == 0
        assert list(p) == [1, 2]


class TestSigned:
    def test_to_signed(self):
        p = PackedTritArray([0, 1, 2])
        assert p.to_signed() == [-1, 0, 1]

    def test_from_signed(self):
        p = PackedTritArray()
        p.from_signed([-1, 0, 1])
        assert list(p) == [0, 1, 2]


class TestCompression:
    def test_bytes(self):
        p = PackedTritArray([0, 1, 2, 0, 1])
        assert p.memory_bytes() == 2

    def test_ratio(self):
        p = PackedTritArray([0] * 100)
        assert p.compression_ratio() > 10  # 28 * 100 / 25 ≈ 112x
        assert p.compression_ratio() > 10


class TestSlice:
    def test_slice(self):
        p = PackedTritArray([0, 1, 2, 0, 1, 2])
        s = p[1:4]
        assert list(s) == [1, 2, 0]

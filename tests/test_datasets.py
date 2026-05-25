from trinary.ai.datasets import (
    AND_DATASET,
    OR_DATASET,
    XOR_DATASET,
    NAND_DATASET,
    TERNARY_EQUALITY,
    TINY_PATTERNS,
    get_dataset,
    list_datasets,
)


class TestANDDataset:
    def test_length(self):
        assert len(AND_DATASET) == 4

    def test_all_ternary_inputs(self):
        for inputs, target in AND_DATASET:
            for x in inputs:
                assert x in (0, 1, 2)
            for t in target:
                assert t in (0, 1, 2)

    def test_correct_output(self):
        assert AND_DATASET == [
            ([0, 0], [0]),
            ([0, 2], [0]),
            ([2, 0], [0]),
            ([2, 2], [2]),
        ]


class TestORDataset:
    def test_length(self):
        assert len(OR_DATASET) == 4

    def test_correct_output(self):
        assert OR_DATASET == [
            ([0, 0], [0]),
            ([0, 2], [2]),
            ([2, 0], [2]),
            ([2, 2], [2]),
        ]


class TestXORDataset:
    def test_length(self):
        assert len(XOR_DATASET) == 4

    def test_correct_output(self):
        assert XOR_DATASET == [
            ([0, 0], [0]),
            ([0, 2], [2]),
            ([2, 0], [2]),
            ([2, 2], [0]),
        ]


class TestNANDDataset:
    def test_length(self):
        assert len(NAND_DATASET) == 4

    def test_correct_output(self):
        assert NAND_DATASET == [
            ([0, 0], [2]),
            ([0, 2], [2]),
            ([2, 0], [2]),
            ([2, 2], [0]),
        ]


class TestTernaryEquality:
    def test_length(self):
        assert len(TERNARY_EQUALITY) == 9

    def test_all_combinations(self):
        seen = set()
        for inputs, target in TERNARY_EQUALITY:
            key = tuple(inputs)
            assert key not in seen
            seen.add(key)
            assert target in ([0], [2])
            if inputs[0] == inputs[1]:
                assert target == [2]
            else:
                assert target == [0]


class TestTinyPatterns:
    def test_length(self):
        assert len(TINY_PATTERNS) == 2

    def test_all_ternary(self):
        for inputs, target in TINY_PATTERNS:
            assert len(inputs) == 9
            for x in inputs:
                assert x in (0, 1, 2)
            assert target[0] in (0, 1, 2)


class TestGetDataset:
    def test_valid_names(self):
        for name in ["and", "or", "xor", "nand"]:
            ds = get_dataset(name)
            assert len(ds) == 4

    def test_invalid_name_raises(self):
        try:
            get_dataset("nonexistent")
            assert False
        except KeyError:
            pass


class TestListDatasets:
    def test_returns_list(self):
        names = list_datasets()
        assert isinstance(names, list)
        assert "and" in names
        assert "xor" in names

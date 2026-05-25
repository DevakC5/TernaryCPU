"""Built-in datasets for ternary neural network training.

Each dataset is a list of (inputs, target) tuples where both
inputs and targets are lists of ternary digits (0/1/2).
"""

AND_DATASET = [
    ([0, 0], [0]),
    ([0, 2], [0]),
    ([2, 0], [0]),
    ([2, 2], [2]),
]

OR_DATASET = [
    ([0, 0], [0]),
    ([0, 2], [2]),
    ([2, 0], [2]),
    ([2, 2], [2]),
]

XOR_DATASET = [
    ([0, 0], [0]),
    ([0, 2], [2]),
    ([2, 0], [2]),
    ([2, 2], [0]),
]

NAND_DATASET = [
    ([0, 0], [2]),
    ([0, 2], [2]),
    ([2, 0], [2]),
    ([2, 2], [0]),
]

TERNARY_TRUTH_TABLE = [
    ([0, 0], [1]),
    ([0, 1], [1]),
    ([0, 2], [1]),
    ([1, 0], [1]),
    ([1, 1], [1]),
    ([1, 2], [1]),
    ([2, 0], [1]),
    ([2, 1], [1]),
    ([2, 2], [1]),
]

TERNARY_EQUALITY = [
    ([0, 0], [2]),
    ([0, 1], [0]),
    ([0, 2], [0]),
    ([1, 0], [0]),
    ([1, 1], [2]),
    ([1, 2], [0]),
    ([2, 0], [0]),
    ([2, 1], [0]),
    ([2, 2], [2]),
]


TINY_PATTERNS = [
    ([2, 0, 2, 0, 2, 0, 2, 0, 2], [2]),
    ([0, 2, 0, 2, 0, 2, 0, 2, 0], [0]),
]


PATTERN_CROSS = [
    ([0, 2, 0, 2, 2, 2, 0, 2, 0], [2]),
    ([2, 0, 2, 0, 2, 0, 2, 0, 2], [0]),
]


ALL_DATASETS = {
    "and": AND_DATASET,
    "or": OR_DATASET,
    "xor": XOR_DATASET,
    "nand": NAND_DATASET,
    "ternary_truth_table": TERNARY_TRUTH_TABLE,
    "ternary_equality": TERNARY_EQUALITY,
    "tiny_patterns": TINY_PATTERNS,
    "pattern_cross": PATTERN_CROSS,
}


def get_dataset(name):
    """Retrieve a dataset by name.

    Args:
        name: String key in ALL_DATASETS.

    Returns:
        List of (inputs, target) tuples.

    Raises:
        KeyError: If name is not found.
    """
    if name not in ALL_DATASETS:
        raise KeyError(
            f"Unknown dataset '{name}'. "
            f"Available: {', '.join(sorted(ALL_DATASETS))}"
        )
    return ALL_DATASETS[name]


def list_datasets():
    """Return the names of all available datasets."""
    return sorted(ALL_DATASETS.keys())

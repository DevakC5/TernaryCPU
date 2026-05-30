"""MNIST handwriting recognition dataset for ternary neural networks.

Loads the MNIST dataset from local IDX files and converts to ternary format.
Pixel values (0-255) are quantized to ternary digits {0, 1, 2} via thresholds.
Labels are one-hot encoded in ternary: digit d → [0]*d + [2] + [0]*(9-d).

Usage:
    from trinary.ai.mnist import load_mnist, mnist_datasets

    train, test = load_mnist()
    # train = [(inputs, target), ...]  where inputs is 784 trits, target is 10 trits

    datasets = mnist_datasets(train_size=1000, test_size=200)
    # datasets["mnist_train"] and datasets["mnist_test"] ready for TernaryTrainer
"""

import struct
import os
import random

_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "mnist")
_data_dir = os.path.normpath(_data_dir)


def _read_idx_images(filepath):
    """Read IDX format image file (e.g. train-images-idx3-ubyte)."""
    with open(filepath, "rb") as f:
        magic, num, rows, cols = struct.unpack(">IIII", f.read(16))
        data = f.read()
    images = []
    for i in range(num):
        offset = i * rows * cols
        img = list(data[offset : offset + rows * cols])
        images.append(img)
    return images, num, rows, cols


def _read_idx_labels(filepath):
    """Read IDX format label file (e.g. train-labels-idx1-ubyte)."""
    with open(filepath, "rb") as f:
        magic, num = struct.unpack(">II", f.read(8))
        labels = list(f.read())
    return labels, num


def _pixel_to_trit(pixel):
    """Convert a pixel value (0-255) to a ternary digit (0, 1, 2).

    Thresholds: 0-84 → 0 (dark), 85-169 → 1 (mid), 170-255 → 2 (bright).
    """
    if pixel < 85:
        return 0
    elif pixel < 170:
        return 1
    else:
        return 2


def _label_to_ternary(label):
    """Convert a digit label (0-9) to one-hot ternary list of length 10.

    Digit d → [0]*d + [2] + [0]*(9-d).
    """
    target = [0] * 10
    target[label] = 2
    return target


def load_mnist(data_dir=None, ternary=True):
    """Load MNIST dataset from local IDX files.

    Args:
        data_dir: Path to directory containing IDX files. If None, uses data/mnist/.
        ternary: If True, convert pixels to {0,1,2} and labels to one-hot ternary.
                 If False, return raw pixels (0-255) and integer labels.

    Returns:
        (train_data, test_data) tuple.
        Each is a list of (inputs, target) tuples.
        If ternary=True: inputs is 784 trits, target is 10 trits (one-hot).
        If ternary=False: inputs is 784 ints (0-255), target is int (0-9).
    """
    if data_dir is None:
        data_dir = _data_dir

    train_imgs, n_train, rows, cols = _read_idx_images(
        os.path.join(data_dir, "train-images-idx3-ubyte")
    )
    train_labels, _ = _read_idx_labels(
        os.path.join(data_dir, "train-labels-idx1-ubyte")
    )
    test_imgs, n_test, _, _ = _read_idx_images(
        os.path.join(data_dir, "t10k-images-idx3-ubyte")
    )
    test_labels, _ = _read_idx_labels(
        os.path.join(data_dir, "t10k-labels-idx1-ubyte")
    )

    if ternary:
        train_data = [
            ([_pixel_to_trit(p) for p in img], _label_to_ternary(lbl))
            for img, lbl in zip(train_imgs, train_labels)
        ]
        test_data = [
            ([_pixel_to_trit(p) for p in img], _label_to_ternary(lbl))
            for img, lbl in zip(test_imgs, test_labels)
        ]
    else:
        train_data = list(zip(train_imgs, train_labels))
        test_data = list(zip(test_imgs, test_labels))

    return train_data, test_data


def mnist_datasets(train_size=1000, test_size=200, seed=42):
    """Load MNIST as named datasets ready for TernaryTrainer.

    Args:
        train_size: Number of training samples to include.
        test_size: Number of test samples to include.
        seed: Random seed for reproducible sampling.

    Returns:
        Dict with keys "mnist_train" and "mnist_test".
    """
    train_full, test_full = load_mnist(ternary=True)

    rng = random.Random(seed)
    train_sample = rng.sample(train_full, min(train_size, len(train_full)))
    test_sample = rng.sample(test_full, min(test_size, len(test_full)))

    return {
        "mnist_train": train_sample,
        "mnist_test": test_sample,
    }


def print_sample(data, index=0):
    """Print a single MNIST sample as ASCII art.

    Args:
        data: Dataset list from load_mnist().
        index: Sample index to print.
    """
    inputs, target = data[index]

    # Determine label from one-hot
    if isinstance(target, list):
        label = target.index(2) if 2 in target else -1
    else:
        label = target

    # Map trits to ASCII
    trit_chars = {0: " ", 1: ".", 2: "#"}

    print(f"Label: {label}")
    for row in range(28):
        line = ""
        for col in range(28):
            trit = inputs[row * 28 + col]
            line += trit_chars.get(trit, "?")
        print(f"  {line}")

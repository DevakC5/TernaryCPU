#!/bin/bash
# Download MNIST dataset for ternary NN training
set -e
DIR="$(cd "$(dirname "$0")" && pwd)/mnist"
mkdir -p "$DIR"
echo "Downloading MNIST to $DIR..."
curl -L -o "$DIR/train-images-idx3-ubyte.gz" "https://storage.googleapis.com/cvdf-datasets/mnist/train-images-idx3-ubyte.gz"
curl -L -o "$DIR/train-labels-idx1-ubyte.gz" "https://storage.googleapis.com/cvdf-datasets/mnist/train-labels-idx1-ubyte.gz"
curl -L -o "$DIR/t10k-images-idx3-ubyte.gz" "https://storage.googleapis.com/cvdf-datasets/mnist/t10k-images-idx3-ubyte.gz"
curl -L -o "$DIR/t10k-labels-idx1-ubyte.gz" "https://storage.googleapis.com/cvdf-datasets/mnist/t10k-labels-idx1-ubyte.gz"
gunzip -f "$DIR/"*.gz
echo "Done. Files:"
ls -lh "$DIR/"

#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NATIVE_DIR="$SCRIPT_DIR/src/trinary/native"

echo "=== TernaryCPU Native Build ==="
echo "Building libternary.so from $NATIVE_DIR"
echo

cd "$NATIVE_DIR"
gcc -shared -fPIC -Wall -Wextra -std=c99 alu.c gpu_kernels.c -o "$SCRIPT_DIR/src/trinary/libternary.so"

echo "Success: libternary.so placed at src/trinary/libternary.so"
echo
echo "Run tests:  python -m pytest tests/test_native_backend.py -v"
echo "Run benchmark:  python -m trinary.native_benchmark"

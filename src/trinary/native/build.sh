#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="$(dirname "$SCRIPT_DIR")"

echo "Building libternary.so..."
gcc -shared -fPIC -Wall -Wextra -std=c99 "$SCRIPT_DIR/alu.c" "$SCRIPT_DIR/gpu_kernels.c" -o "$LIB_DIR/libternary.so"

echo "Success: libternary.so placed at $LIB_DIR/libternary.so"

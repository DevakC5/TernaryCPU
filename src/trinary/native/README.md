# Native C Backend for TernaryCPU

This directory provides a C native acceleration layer for ternary arithmetic.

## Why a hybrid architecture?

The Python simulator is clean and educational, but pure Python arithmetic
has overhead. This native backend accelerates the hot path (add, sub, mul,
div) by moving it to C, while keeping the high-level orchestrator (CPU,
assembler, UI) in Python where flexibility matters more.

## Files

| File | Purpose |
|---|---|
| `ternary.h` | Public C API header |
| `alu.c` | Implementation of ternary arithmetic primitives |
| `Makefile` | Build via `make` |
| `build.sh` | Shell script to compile and place `libternary.so` |

## Building

```sh
make
```

Or:

```sh
./build.sh
```

Output: `src/trinary/libternary.so`

## C API

```c
int ternary_add(int a, int b);
int ternary_sub(int a, int b);
int ternary_mul(int a, int b);
int ternary_div(int a, int b);         // returns INT_MIN on division by zero
int ternary_full_adder(int a, int b, int carry_in, int* carry_out);
```

## Python bindings

The module `trinary.native_backend` loads `libternary.so` via ctypes
and wraps each function in a clean Python interface.

```python
from trinary.native_backend import native_add, native_sub
result = native_add(10, 20)  # 30
```

## Integration

Set `USE_NATIVE = True` in `trinary.alu` to prefer the C backend.
When the shared library is unavailable, the ALU falls back to pure
Python automatically.

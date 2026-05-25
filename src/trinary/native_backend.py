"""
ctypes bindings for the native C acceleration layer.

Loads libternary.so and exposes clean Python wrappers. Falls back
gracefully when the library is not available so the simulator still
works with pure Python.
"""

import ctypes
import os
import warnings

NATIVE_AVAILABLE = False

_lib_paths = [
    os.path.join(os.path.dirname(__file__), "libternary.so"),
    os.path.join(os.path.dirname(__file__), "native", "libternary.so"),
    "libternary.so",
]

_lib = None
for _path in _lib_paths:
    if os.path.exists(_path):
        try:
            _lib = ctypes.CDLL(_path)
            NATIVE_AVAILABLE = True
            break
        except (OSError, ctypes.CDLLError) as _e:
            warnings.warn(f"Failed to load {_path}: {_e}")

if NATIVE_AVAILABLE:
    _lib.ternary_add.argtypes = [ctypes.c_int, ctypes.c_int]
    _lib.ternary_add.restype = ctypes.c_int

    _lib.ternary_sub.argtypes = [ctypes.c_int, ctypes.c_int]
    _lib.ternary_sub.restype = ctypes.c_int

    _lib.ternary_mul.argtypes = [ctypes.c_int, ctypes.c_int]
    _lib.ternary_mul.restype = ctypes.c_int

    _lib.ternary_div.argtypes = [ctypes.c_int, ctypes.c_int]
    _lib.ternary_div.restype = ctypes.c_int

    _lib.ternary_full_adder.argtypes = [
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)
    ]
    _lib.ternary_full_adder.restype = ctypes.c_int


def _require_native():
    if not NATIVE_AVAILABLE:
        raise RuntimeError(
            "Native backend not available. Build libternary.so first "
            "with: cd src/trinary/native && make"
        )


def native_add(a: int, b: int) -> int:
    _require_native()
    return _lib.ternary_add(a, b)


def native_sub(a: int, b: int) -> int:
    _require_native()
    return _lib.ternary_sub(a, b)


def native_mul(a: int, b: int) -> int:
    _require_native()
    return _lib.ternary_mul(a, b)


def native_div(a: int, b: int) -> int:
    _require_native()
    return _lib.ternary_div(a, b)


def native_full_adder(a: int, b: int, carry_in: int):
    _require_native()
    carry_out = ctypes.c_int(0)
    s = _lib.ternary_full_adder(a, b, carry_in, ctypes.byref(carry_out))
    return (s, carry_out.value)

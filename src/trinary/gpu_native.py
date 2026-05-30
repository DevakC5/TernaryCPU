"""
ctypes bindings for the native C GPU acceleration layer.

Provides fast implementations of ternary GPU vector/matrix operations.
Falls back gracefully when libternary.so is unavailable.
"""

import ctypes
import os
import warnings

GPU_NATIVE_AVAILABLE = False

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
            GPU_NATIVE_AVAILABLE = True
            break
        except (OSError, ctypes.CDLLError):
            pass

_int_p = ctypes.POINTER(ctypes.c_int)

if GPU_NATIVE_AVAILABLE:
    _lib.gpu_vec_add.argtypes = [_int_p, _int_p, _int_p, ctypes.c_int]
    _lib.gpu_vec_add.restype = None

    _lib.gpu_vec_mul.argtypes = [_int_p, _int_p, _int_p, ctypes.c_int]
    _lib.gpu_vec_mul.restype = None

    _lib.gpu_vec_dot.argtypes = [_int_p, _int_p, ctypes.c_int]
    _lib.gpu_vec_dot.restype = ctypes.c_int

    _lib.gpu_vec_threshold.argtypes = [_int_p, _int_p, ctypes.c_int]
    _lib.gpu_vec_threshold.restype = None

    _lib.gpu_vec_sum.argtypes = [_int_p, ctypes.c_int]
    _lib.gpu_vec_sum.restype = ctypes.c_int

    _lib.gpu_vec_max.argtypes = [_int_p, ctypes.c_int]
    _lib.gpu_vec_max.restype = ctypes.c_int

    _lib.gpu_vec_min.argtypes = [_int_p, ctypes.c_int]
    _lib.gpu_vec_min.restype = ctypes.c_int

    _lib.gpu_reduce.argtypes = [_int_p, ctypes.c_int, ctypes.c_int]
    _lib.gpu_reduce.restype = ctypes.c_int

    _lib.gpu_scan.argtypes = [_int_p, _int_p, ctypes.c_int]
    _lib.gpu_scan.restype = None

    _lib.gpu_transpose.argtypes = [_int_p, ctypes.c_int, ctypes.c_int, _int_p]
    _lib.gpu_transpose.restype = None

    _lib.gpu_matmul.argtypes = [
        _int_p, ctypes.c_int, ctypes.c_int,
        _int_p, ctypes.c_int, ctypes.c_int,
        _int_p,
    ]
    _lib.gpu_matmul.restype = None

    _lib.gpu_fused_linear.argtypes = [
        _int_p, ctypes.c_int, ctypes.c_int,
        _int_p, _int_p, _int_p, ctypes.c_int,
    ]
    _lib.gpu_fused_linear.restype = None

    _lib.gpu_elementwise_fused.argtypes = [
        _int_p, _int_p, ctypes.c_int, _int_p,
        ctypes.c_int, ctypes.c_int,
    ]
    _lib.gpu_elementwise_fused.restype = None


def _to_c_array(data):
    """Convert a Python list of ints to a ctypes int array."""
    arr = (ctypes.c_int * len(data))(*data)
    return arr


def native_vec_add(a, b):
    n = len(a)
    out = (ctypes.c_int * n)()
    _lib.gpu_vec_add(_to_c_array(a), _to_c_array(b), out, n)
    return [out[i] for i in range(n)]


def native_vec_mul(a, b):
    n = len(a)
    out = (ctypes.c_int * n)()
    _lib.gpu_vec_mul(_to_c_array(a), _to_c_array(b), out, n)
    return [out[i] for i in range(n)]


def native_vec_dot(a, b):
    return _lib.gpu_vec_dot(_to_c_array(a), _to_c_array(b), len(a))


def native_vec_threshold(a):
    n = len(a)
    out = (ctypes.c_int * n)()
    _lib.gpu_vec_threshold(_to_c_array(a), out, n)
    return [out[i] for i in range(n)]


def native_vec_sum(a):
    return _lib.gpu_vec_sum(_to_c_array(a), len(a))


def native_vec_max(a):
    return _lib.gpu_vec_max(_to_c_array(a), len(a))


def native_vec_min(a):
    return _lib.gpu_vec_min(_to_c_array(a), len(a))


def native_reduce(data, op="sum"):
    op_map = {"sum": 0, "max": 1, "min": 2}
    return _lib.gpu_reduce(_to_c_array(data), len(data), op_map[op])


def native_scan(data):
    n = len(data)
    out = (ctypes.c_int * n)()
    _lib.gpu_scan(_to_c_array(data), out, n)
    return [out[i] for i in range(n)]


def native_transpose(matrix):
    if not matrix or not matrix[0]:
        return []
    rows = len(matrix)
    cols = len(matrix[0])
    flat = [v for row in matrix for v in row]
    out = (ctypes.c_int * (rows * cols))()
    _lib.gpu_transpose(_to_c_array(flat), rows, cols, out)
    return [[out[r * rows + c] for c in range(rows)] for r in range(cols)]


def native_matmul(a, b):
    a_rows = len(a)
    a_cols = len(a[0]) if a else 0
    b_rows = len(b)
    b_cols = len(b[0]) if b else 0
    flat_a = [v for row in a for v in row]
    flat_b = [v for row in b for v in row]
    out = (ctypes.c_int * (a_rows * b_cols))()
    _lib.gpu_matmul(
        _to_c_array(flat_a), a_rows, a_cols,
        _to_c_array(flat_b), b_rows, b_cols,
        out,
    )
    return [[out[r * b_cols + c] for c in range(b_cols)] for r in range(a_rows)]


def native_fused_linear(weights, inputs, bias=None, activation="threshold"):
    w_rows = len(weights)
    w_cols = len(weights[0]) if weights else 0
    flat_w = [v for row in weights for v in row]
    flat_x = list(inputs)
    flat_b = list(bias) if bias else None
    act_id = 1 if activation == "relu" else 0
    out = (ctypes.c_int * w_rows)()
    bias_arr = _to_c_array(flat_b) if flat_b else None
    _lib.gpu_fused_linear(
        _to_c_array(flat_w), w_rows, w_cols,
        _to_c_array(flat_x), bias_arr, out, act_id,
    )
    return [out[i] for i in range(w_rows)]


def native_elementwise_fused(a, b, op1="add", op2="threshold"):
    n = len(a)
    op1_id = 0 if op1 == "add" else 1
    op2_id = 0 if op2 == "threshold" else 1
    out = (ctypes.c_int * n)()
    _lib.gpu_elementwise_fused(
        _to_c_array(a), _to_c_array(b), n, out, op1_id, op2_id,
    )
    return [out[i] for i in range(n)]

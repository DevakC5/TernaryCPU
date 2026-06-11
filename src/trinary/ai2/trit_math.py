"""Trit-native math: LUT-based arithmetic on trits {0,1,2} → {-1,0,+1}.

All operations work directly on trit values using precomputed lookup
tables — no branches, no per-element signed conversion in hot paths.

Dot products accumulate in int32 and collapse via ternary_step once.
"""

# signed(a) + signed(b) → ternary_step(result)
TRIT_ADD = [
    [0, 0, 1],  # a=0(-1): -1+{-1,0,+1} = {-2,-1,0} → {0,0,1}
    [0, 1, 2],  # a=1(0):   0+{-1,0,+1} = {-1,0,+1} → {0,1,2}
    [1, 2, 2],  # a=2(+1): +1+{-1,0,+1} = {0,+1,+2} → {1,2,2}
]

# signed(a) * signed(b) → ternary_step(result)
TRIT_MUL = [
    [2, 1, 0],  # a=0(-1): -1*{-1,0,+1} = {+1,0,-1} → {2,1,0}
    [1, 1, 1],  # a=1(0):   0*{-1,0,+1} = {0,0,0}   → {1,1,1}
    [0, 1, 2],  # a=2(+1): +1*{-1,0,+1} = {-1,0,+1} → {0,1,2}
]

# signed(a) * signed(b) as raw int (for accumulation before ternary_step)
DOT_TERM = [
    [1, 0, -1],   # (-1)*(-1)=1, (-1)*0=0, (-1)*(+1)=-1
    [0, 0, 0],    # 0*(-1)=0, 0*0=0, 0*(+1)=0
    [-1, 0, 1],   # (+1)*(-1)=-1, (+1)*0=0, (+1)*(+1)=1
]


def ternary_step(value: int) -> int:
    """Collapse any integer to trit {0,1,2} via ternary_step."""
    if value < -1:
        return 0
    if value == -1:
        return 0
    if value == 0:
        return 1
    if value == 1:
        return 2
    return 2


def trit_dot(xs: list, ys: list) -> int:
    """Dot product of two trit vectors.

    Accumulates raw signed products in int32, then collapses once
    via ternary_step.  Result is a trit {0,1,2}.
    """
    total = 0
    dt = DOT_TERM
    for x, y in zip(xs, ys):
        total += dt[x][y]
    return ternary_step(total)


def trit_dot_raw(xs: list, ys: list) -> int:
    """Dot product returning raw int (before ternary_step).

    Used internally when the caller wants the accumulated value
    (e.g., for gradient computation).
    """
    total = 0
    dt = DOT_TERM
    for x, y in zip(xs, ys):
        total += dt[x][y]
    return total


def trit_matmul(A: list, B: list) -> list:
    """Matrix multiply A @ B. Both are 2D lists of trits.

    A: (M, K), B: (K, N) → result: (M, N)
    """
    M = len(A)
    K = len(A[0])
    N = len(B[0])
    result = [[0] * N for _ in range(M)]
    for i in range(M):
        row = A[i]
        for j in range(N):
            col = [B[k][j] for k in range(K)]
            result[i][j] = trit_dot(row, col)
    return result


def trit_matmul_raw(A: list, B: list) -> list:
    """Matrix multiply returning raw int accumulations (pre-ternary_step)."""
    M = len(A)
    K = len(A[0])
    N = len(B[0])
    result = [[0] * N for _ in range(M)]
    dt = DOT_TERM
    for i in range(M):
        row = A[i]
        for j in range(N):
            total = 0
            for k in range(K):
                total += dt[row[k]][B[k][j]]
            result[i][j] = total
    return result


# Trit → signed value: 0→-1, 1→0, 2→+1
_SIGNED = [-1, 0, 1]


def trit_linear(weight: list, bias: list | None, inputs: list,
                in_features: int, out_features: int) -> list:
    """Linear layer: output = ternary_step(W @ inputs + bias).

    weight: flat list of trits (out_features * in_features)
    bias: flat list of trits (out_features) or None
    inputs: flat list of trits (in_features)

    Returns flat list of trits (out_features).
    """
    out = [0] * out_features
    dt = DOT_TERM
    sv = _SIGNED
    for i in range(out_features):
        total = 0
        base = i * in_features
        for j in range(in_features):
            total += dt[weight[base + j]][inputs[j]]
        if bias is not None:
            total += sv[bias[i]]
        out[i] = ternary_step(total)
    return out


def trit_linear_raw(weight: list, bias: list | None, inputs: list,
                    in_features: int, out_features: int) -> list:
    """Linear layer returning raw int pre-activation values."""
    out = [0] * out_features
    dt = DOT_TERM
    sv = _SIGNED
    for i in range(out_features):
        total = 0
        base = i * in_features
        for j in range(in_features):
            total += dt[weight[base + j]][inputs[j]]
        if bias is not None:
            total += sv[bias[i]]
        out[i] = total
    return out


def trit_add_trit(a: int, b: int) -> int:
    """Add two trits, return trit result."""
    return TRIT_ADD[a][b]

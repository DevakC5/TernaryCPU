/**
 * gpu_kernels.c — Native C acceleration for ternary GPU operations.
 *
 * Provides fast implementations of the hot inner loops:
 *   vector add/mul/dot/threshold, reduction (sum/max/min),
 *   prefix scan, matrix transpose, and matrix multiply.
 *
 * All functions operate on flat int arrays of ternary digits {0,1,2}.
 * Signed mapping: 0→-1, 1→0, 2→+1 (same as trinary.ai.activations).
 */

#include "ternary.h"
#include <string.h>

/* ── signed conversion helpers ────────────────────────────────── */

static inline int trit_to_signed(int t) {
    if (t == 0) return -1;
    if (t == 1) return 0;
    return 1;  /* t == 2 */
}

static inline int signed_to_trit(int s) {
    if (s < 0) return 0;
    if (s == 0) return 1;
    return 2;
}

static inline int ternary_step(int v) {
    if (v < 0) return 0;
    if (v == 0) return 1;
    return 2;
}

static inline int clamp3(int v) {
    if (v < -1) return -1;
    if (v > 1) return 1;
    return v;
}

/* ── element-wise vector operations ──────────────────────────── */

void gpu_vec_add(const int *a, const int *b, int *out, int n) {
    for (int i = 0; i < n; i++) {
        int s = trit_to_signed(a[i]) + trit_to_signed(b[i]);
        out[i] = ternary_step(s);
    }
}

void gpu_vec_mul(const int *a, const int *b, int *out, int n) {
    for (int i = 0; i < n; i++) {
        int s = trit_to_signed(a[i]) * trit_to_signed(b[i]);
        out[i] = ternary_step(s);
    }
}

int gpu_vec_dot(const int *a, const int *b, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += trit_to_signed(a[i]) * trit_to_signed(b[i]);
    }
    return sum;
}

void gpu_vec_threshold(const int *a, int *out, int n) {
    for (int i = 0; i < n; i++) {
        out[i] = ternary_step(a[i]);
    }
}

/* ── reduction operations ────────────────────────────────────── */

int gpu_vec_sum(const int *a, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += trit_to_signed(a[i]);
    }
    return sum;
}

int gpu_vec_max(const int *a, int n) {
    if (n <= 0) return 0;
    int mx = trit_to_signed(a[0]);
    for (int i = 1; i < n; i++) {
        int s = trit_to_signed(a[i]);
        if (s > mx) mx = s;
    }
    return mx;
}

int gpu_vec_min(const int *a, int n) {
    if (n <= 0) return 0;
    int mn = trit_to_signed(a[0]);
    for (int i = 1; i < n; i++) {
        int s = trit_to_signed(a[i]);
        if (s < mn) mn = s;
    }
    return mn;
}

/* ── parallel reduction kernel ───────────────────────────────── */

int gpu_reduce(const int *data, int n, int op) {
    /* op: 0=sum, 1=max, 2=min */
    if (n <= 0) return 0;
    switch (op) {
        case 0: return gpu_vec_sum(data, n);
        case 1: return gpu_vec_max(data, n);
        case 2: return gpu_vec_min(data, n);
        default: return 0;
    }
}

/* ── prefix scan (inclusive) ─────────────────────────────────── */

void gpu_scan(const int *data, int *out, int n) {
    if (n <= 0) return;
    int prefix = 0;
    for (int i = 0; i < n; i++) {
        prefix += trit_to_signed(data[i]);
        out[i] = signed_to_trit(clamp3(prefix));
    }
}

/* ── matrix transpose ────────────────────────────────────────── */

void gpu_transpose(const int *mat, int rows, int cols, int *out) {
    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
            out[c * rows + r] = mat[r * cols + c];
        }
    }
}

/* ── matrix multiply ─────────────────────────────────────────── */

void gpu_matmul(const int *a, int a_rows, int a_cols,
                const int *b, int b_rows, int b_cols,
                int *out) {
    (void)b_rows;  /* caller validates a_cols == b_rows */
    for (int r = 0; r < a_rows; r++) {
        for (int c = 0; c < b_cols; c++) {
            int sum = 0;
            for (int k = 0; k < a_cols; k++) {
                sum += trit_to_signed(a[r * a_cols + k])
                     * trit_to_signed(b[k * b_cols + c]);
            }
            out[r * b_cols + c] = ternary_step(sum);
        }
    }
}

/* ── fused linear: activation(W @ x + bias) ──────────────────── */

void gpu_fused_linear(const int *weights, int w_rows, int w_cols,
                      const int *inputs, const int *bias,
                      int *out, int activation) {
    /* activation: 0=threshold, 1=relu */
    for (int r = 0; r < w_rows; r++) {
        int sum = 0;
        for (int k = 0; k < w_cols; k++) {
            sum += trit_to_signed(weights[r * w_cols + k])
                 * trit_to_signed(inputs[k]);
        }
        if (bias) {
            sum += trit_to_signed(bias[r]);
        }
        if (activation == 1) {
            /* ternary relu: non-positive → 1 (neutral), positive → 2 */
            out[r] = (sum > 0) ? 2 : 1;
        } else {
            out[r] = ternary_step(sum);
        }
    }
}

/* ── fused elementwise: op1 then op2 in one pass ─────────────── */

void gpu_elementwise_fused(const int *a, const int *b, int n,
                           int *out, int op1, int op2) {
    /* op1: 0=add, 1=mul;  op2: 0=threshold */
    for (int i = 0; i < n; i++) {
        int s;
        if (op1 == 0) {
            s = trit_to_signed(a[i]) + trit_to_signed(b[i]);
        } else {
            s = trit_to_signed(a[i]) * trit_to_signed(b[i]);
        }
        int mid = ternary_step(s);
        if (op2 == 0) {
            out[i] = ternary_step(mid);
        } else {
            out[i] = mid;
        }
    }
}

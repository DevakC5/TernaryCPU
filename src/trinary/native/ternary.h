#ifndef TERNARY_H
#define TERNARY_H

#define DIVISION_BY_ZERO -2147483647 - 1

/* ── ALU operations (alu.c) ──────────────────────────────────── */

int ternary_add(int a, int b);
int ternary_sub(int a, int b);
int ternary_mul(int a, int b);
int ternary_div(int a, int b);
int ternary_full_adder(int a, int b, int carry_in, int* carry_out);

/* ── GPU vector operations (gpu_kernels.c) ───────────────────── */

/* Element-wise: out[i] = f(a[i], b[i]) */
void gpu_vec_add(const int *a, const int *b, int *out, int n);
void gpu_vec_mul(const int *a, const int *b, int *out, int n);
int  gpu_vec_dot(const int *a, const int *b, int n);
void gpu_vec_threshold(const int *a, int *out, int n);

/* Reductions */
int  gpu_vec_sum(const int *a, int n);
int  gpu_vec_max(const int *a, int n);
int  gpu_vec_min(const int *a, int n);
int  gpu_reduce(const int *data, int n, int op);

/* Prefix scan (inclusive) */
void gpu_scan(const int *data, int *out, int n);

/* Matrix ops — flat row-major arrays */
void gpu_transpose(const int *mat, int rows, int cols, int *out);
void gpu_matmul(const int *a, int a_rows, int a_cols,
                const int *b, int b_rows, int b_cols,
                int *out);

/* Fused linear: out = activation(W @ x + bias) */
void gpu_fused_linear(const int *weights, int w_rows, int w_cols,
                      const int *inputs, const int *bias,
                      int *out, int activation);

/* Fused elementwise: out = op2(op1(a[i], b[i])) */
void gpu_elementwise_fused(const int *a, const int *b, int n,
                           int *out, int op1, int op2);

#endif

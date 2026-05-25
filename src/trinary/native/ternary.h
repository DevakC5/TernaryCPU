#ifndef TERNARY_H
#define TERNARY_H

#define DIVISION_BY_ZERO -2147483647 - 1

int ternary_add(int a, int b);
int ternary_sub(int a, int b);
int ternary_mul(int a, int b);
int ternary_div(int a, int b);
int ternary_full_adder(int a, int b, int carry_in, int* carry_out);

#endif

#include "ternary.h"

int ternary_add(int a, int b) {
    return a + b;
}

int ternary_sub(int a, int b) {
    return a - b;
}

int ternary_mul(int a, int b) {
    return a * b;
}

int ternary_div(int a, int b) {
    if (b == 0) {
        return DIVISION_BY_ZERO;
    }
    return a / b;
}

int ternary_full_adder(int a, int b, int carry_in, int* carry_out) {
    int total = a + b + carry_in;
    *carry_out = total / 3;
    return total % 3;
}

"""Arithmetic operations for the ternary computing system.

All operations work natively on signed-magnitude ternary strings
without converting through decimal. Uses the ripple-carry adder
for magnitude arithmetic and sign-magnitude logic for negatives.
"""

from trinary.adder import ripple_carry_adder


def _is_negative(s):
    return s.startswith("-")


def _magnitude(s):
    return s[1:] if _is_negative(s) else s


def _negate(s):
    if s == "0":
        return "0"
    return "-" + s[1:] if _is_negative(s) else "-" + s


def _strip_leading_zeros(s):
    body = _magnitude(s)
    body = body.lstrip("0")
    if not body:
        return "0"
    neg = "-" if _is_negative(s) else ""
    return neg + body


def _compare_magnitude(a, b):
    """Compare absolute values of two ternary strings.
    Returns 1 if |a| > |b|, -1 if |a| < |b|, 0 if equal."""
    ma = _magnitude(a)
    mb = _magnitude(b)
    ma = ma.lstrip("0") or "0"
    mb = mb.lstrip("0") or "0"
    if len(ma) > len(mb):
        return 1
    if len(ma) < len(mb):
        return -1
    if ma > mb:
        return 1
    if ma < mb:
        return -1
    return 0


def _add_magnitudes(a, b):
    """Add two non-negative ternary magnitude strings using ripple-carry.
    Result may have an extra leading digit from carry-out."""
    result, carry = ripple_carry_adder(a, b)
    if carry > 0:
        result = str(carry) + result
    return result


def _subtract_magnitudes(a, b):
    """Subtract b from a where |a| >= |b| and both are non-negative.
    Returns |a| - |b| as a ternary string."""
    a_rev = a[::-1]
    b_rev = b[::-1]
    max_len = max(len(a), len(b))
    a_rev = a_rev.ljust(max_len, "0")
    b_rev = b_rev.ljust(max_len, "0")

    result_digits = []
    borrow = 0
    for i in range(max_len):
        digit_a = int(a_rev[i]) - borrow
        digit_b = int(b_rev[i])
        if digit_a < digit_b:
            digit_a += 3
            borrow = 1
        else:
            borrow = 0
        result_digits.append(str(digit_a - digit_b))

    result = "".join(reversed(result_digits))
    return _strip_leading_zeros(result)


def _multiply_magnitudes(a, b):
    """Multiply two non-negative ternary magnitude strings.
    Uses digit-by-digit multiplication with ripple-carry summation."""
    if _strip_leading_zeros(a) == "0" or _strip_leading_zeros(b) == "0":
        return "0"

    a_stripped = _strip_leading_zeros(a)
    b_stripped = _strip_leading_zeros(b)
    a_digits = a_stripped[::-1]
    b_digits = b_stripped[::-1]

    partials = []
    for i, bd in enumerate(b_digits):
        b_val = int(bd)
        row = ["0"] * i
        carry = 0
        for ad in a_digits:
            prod = int(ad) * b_val + carry
            row.append(str(prod % 3))
            carry = prod // 3
        if carry > 0:
            row.append(str(carry))
        partials.append("".join(reversed(row)))

    result = "0"
    for p in partials:
        result = _add_magnitudes(result, p)

    return _strip_leading_zeros(result)


def _divide_magnitudes(a, b):
    """Divide magnitude a by magnitude b using base-3 long division.
    Returns (quotient, remainder) as ternary strings."""
    if _strip_leading_zeros(b) == "0":
        raise ValueError("Cannot divide by zero.")

    a_stripped = _strip_leading_zeros(a) or "0"
    b_stripped = _strip_leading_zeros(b) or "0"

    if _compare_magnitude(a_stripped, b_stripped) < 0:
        return ("0", a_stripped)

    quotient = []
    remainder = "0"
    for digit in a_stripped:
        current = _add_magnitudes(
            _multiply_magnitudes(remainder, "10") if remainder != "0" else "0",
            digit
        ) if remainder != "0" else digit
        if current.startswith("0"):
            current = current.lstrip("0") or "0"

        if _compare_magnitude(current, b_stripped) >= 0:
            q_digit = 0
            temp = "0"
            for d in (2, 1, 0):
                test = _multiply_magnitudes(b_stripped, str(d))
                if _compare_magnitude(test, current) <= 0:
                    q_digit = d
                    temp = test
                    break
            quotient.append(str(q_digit))
            remainder = _subtract_magnitudes(current, temp)
        else:
            quotient.append("0")
            remainder = current

    result = "".join(quotient).lstrip("0") or "0"
    return (result, remainder)


def add_ternary(a, b):
    """Add two signed-magnitude ternary strings natively."""
    if a == "0":
        return b
    if b == "0":
        return a

    a_neg = _is_negative(a)
    b_neg = _is_negative(b)
    a_mag = _strip_leading_zeros(_magnitude(a)) or "0"
    b_mag = _strip_leading_zeros(_magnitude(b)) or "0"

    if a_neg == b_neg:
        result = _add_magnitudes(a_mag, b_mag)
        if a_neg and result != "0":
            result = "-" + result
        return result
    else:
        cmp = _compare_magnitude(a_mag, b_mag)
        if cmp > 0:
            result = _subtract_magnitudes(a_mag, b_mag)
            if a_neg and result != "0":
                result = "-" + result
            return result
        elif cmp < 0:
            result = _subtract_magnitudes(b_mag, a_mag)
            if b_neg and result != "0":
                result = "-" + result
            return result
        else:
            return "0"


def subtract_ternary(a, b):
    """Subtract b from a using native signed-magnitude arithmetic."""
    return add_ternary(a, _negate(b))


def multiply_ternary(a, b):
    """Multiply two signed-magnitude ternary strings natively."""
    if a == "0" or b == "0":
        return "0"
    a_neg = _is_negative(a)
    b_neg = _is_negative(b)
    a_mag = _strip_leading_zeros(_magnitude(a)) or "0"
    b_mag = _strip_leading_zeros(_magnitude(b)) or "0"
    result = _multiply_magnitudes(a_mag, b_mag)
    if a_neg != b_neg and result != "0":
        result = "-" + result
    return result


def divide_ternary(a, b):
    """Divide a by b using native signed-magnitude arithmetic (floor division)."""
    a_neg = _is_negative(a)
    b_neg = _is_negative(b)
    a_mag = _strip_leading_zeros(_magnitude(a)) or "0"
    b_mag = _strip_leading_zeros(_magnitude(b)) or "0"
    quotient, _ = _divide_magnitudes(a_mag, b_mag)
    if quotient != "0" and a_neg != b_neg:
        quotient = "-" + quotient
    return quotient

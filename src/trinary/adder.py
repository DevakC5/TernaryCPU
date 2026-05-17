"""
Ternary adder implementations.

Provides ternary half adder, full adder, and ripple carry adder using
standard unbalanced ternary: sum = (a + b) % 3, carry = (a + b) // 3.
"""

from trinary.logic import validate_trit


def half_adder(a, b):
    """Ternary half adder. Adds two trits, returns (sum, carry).

    Truth table:
        A B -> Sum Carry
        0 0 -> 0    0
        0 1 -> 1    0
        0 2 -> 2    0
        1 0 -> 1    0
        1 1 -> 2    0
        1 2 -> 0    1
        2 0 -> 2    0
        2 1 -> 0    1
        2 2 -> 1    1

    Args:
        a (int): first trit (0, 1, or 2)
        b (int): second trit (0, 1, or 2)

    Returns:
        tuple[int, int]: (sum, carry)
    """
    validate_trit(a)
    validate_trit(b)
    total = a + b
    return (total % 3, total // 3)


def full_adder(a, b, carry_in):
    """Ternary full adder. Adds three trits, returns (sum, carry_out).

    Truth table (27 combinations):
        A B Cin -> Cout Sum
        All where (A + B + Cin) // 3 = carry_out, % 3 = sum

    Args:
        a (int): first trit (0, 1, or 2)
        b (int): second trit (0, 1, or 2)
        carry_in (int): input carry trit (0, 1, or 2)

    Returns:
        tuple[int, int]: (sum, carry_out)
    """
    validate_trit(a)
    validate_trit(b)
    validate_trit(carry_in)
    total = a + b + carry_in
    return (total % 3, total // 3)


def validate_ternary_string(s):
    """Validate a ternary string (contains only 0, 1, 2)."""
    if not isinstance(s, str) or not s:
        raise ValueError("Input must be a non-empty string")
    for c in s:
        if c not in "012":
            raise ValueError(f"Invalid trit: {c}. Must be 0, 1, or 2")
    return True


def ripple_carry_adder(a_str, b_str, initial_carry=0):
    """Ternary Ripple Carry Adder - chains full adders across multi-trit numbers.

    Chain: carry_out[i] -> carry_in[i+1]

    Args:
        a_str (str): first ternary number as string (e.g., "102")
        b_str (str): second ternary number as string (e.g., "21")
        initial_carry (int): initial carry_in for least significant position (default 0)

    Returns:
        tuple: (sum_string, final_carry)
            - sum_string: ternary sum as string
            - final_carry: carry out from most significant position

    Example:
        a = "102" (11 in decimal)
        b = "21"  (7 in decimal)
        Result: "200" (18 in decimal), carry = 0
    """
    validate_ternary_string(a_str)
    validate_ternary_string(b_str)
    validate_trit(initial_carry)

    a_rev = a_str[::-1]
    b_rev = b_str[::-1]

    max_len = max(len(a_str), len(b_str))

    a_rev = a_rev.ljust(max_len, "0")
    b_rev = b_rev.ljust(max_len, "0")

    sum_digits = []
    carry = initial_carry

    for i in range(max_len):
        a_digit = int(a_rev[i])
        b_digit = int(b_rev[i])
        s, carry = full_adder(a_digit, b_digit, carry)
        sum_digits.append(str(s))

    result = "".join(reversed(sum_digits))
    final_carry = carry
    if carry > 0:
        result = str(carry) + result
        final_carry = 0
    return (result, final_carry)


def ripple_carry_adder_detailed(a_str, b_str, initial_carry=0):
    """Ripple carry adder with step-by-step trace for debugging/research.

    Returns:
        tuple: (sum_string, final_carry, trace_list)
            trace_list contains each step: (position, a, b, carry_in, sum, carry_out)
    """
    validate_ternary_string(a_str)
    validate_ternary_string(b_str)
    validate_trit(initial_carry)

    a_rev = a_str[::-1]
    b_rev = b_str[::-1]
    max_len = max(len(a_str), len(b_str))

    a_rev = a_rev.ljust(max_len, "0")
    b_rev = b_rev.ljust(max_len, "0")

    sum_digits = []
    carry = initial_carry
    trace = []

    for i in range(max_len):
        a_digit = int(a_rev[i])
        b_digit = int(b_rev[i])
        s, carry = full_adder(a_digit, b_digit, carry)
        sum_digits.append(str(s))
        trace.append({
            "position": i,
            "a": a_digit,
            "b": b_digit,
            "carry_in": carry if i == 0 else old_carry,
            "sum": s,
            "carry_out": carry
        })
        old_carry = carry

    result = "".join(reversed(sum_digits))
    final_carry = carry
    if carry > 0:
        result = str(carry) + result
        final_carry = 0
    return (result, final_carry, trace)


def print_ripple_adder_steps(a_str, b_str, initial_carry=0):
    """Print step-by-step ripple carry addition for visualization."""
    print("\n" + "=" * 65)
    print(f"TERNARY RIPPLE CARRY ADDER")
    print(f"  {a_str} + {b_str} (initial carry: {initial_carry})")
    print("=" * 65)
    print(f"{'Pos':>3} | {'A':>1} {'B':>1} | {'Cin':>3} | {'Sum':>3} | {'Cout':>4}")
    print("-" * 45)

    a_rev = a_str[::-1]
    b_rev = b_str[::-1]
    max_len = max(len(a_str), len(b_str))

    a_rev = a_rev.ljust(max_len, "0")
    b_rev = b_rev.ljust(max_len, "0")

    sum_digits = []
    carry = initial_carry
    old_carry = initial_carry

    for i in range(max_len):
        a_digit = int(a_rev[i])
        b_digit = int(b_rev[i])
        s, carry = full_adder(a_digit, b_digit, old_carry)
        sum_digits.append(str(s))
        print(f"{i:>3} | {a_digit} {b_digit} | {old_carry:>3} | {s:>3} | {carry:>4}")
        old_carry = carry

    result = "".join(reversed(sum_digits))
    final_carry = carry
    if carry > 0:
        result = str(carry) + result
        final_carry = 0
    print("-" * 45)
    print(f"Result: {result} | Final Carry: {final_carry}")
    print("=" * 65)


def print_half_adder_truth_table():
    """Print the half adder truth table."""
    print("=== Half Adder ===")
    print("A B -> Sum Carry")
    for a in (0, 1, 2):
        for b in (0, 1, 2):
            s, c = half_adder(a, b)
            print(f"{a} {b} -> {s}    {c}")


def print_full_adder_truth_table():
    """Print the full adder truth table."""
    print("\n=== Full Adder ===")
    print("A B Cin -> Cout Sum")
    for a in (0, 1, 2):
        for b in (0, 1, 2):
            for cin in (0, 1, 2):
                s, c = full_adder(a, b, cin)
                print(f"{a} {b} {cin} -> {c}    {s}")


def print_full_truth_table_detailed():
    """Print detailed truth table for research/visualization/papers."""
    print("\n" + "=" * 60)
    print("TERNARY FULL ADDER - COMPLETE TRUTH TABLE")
    print("All 27 combinations: a + b + carry_in = sum, carry_out")
    print("=" * 60)
    print(f"{'#':>3} | {'A':>1} {'B':>1} {'Cin':>3} | {'Sum':>3} {'Cout':>4} | {'Total':>6}")
    print("-" * 40)
    count = 0
    for a in (0, 1, 2):
        for b in (0, 1, 2):
            for cin in (0, 1, 2):
                count += 1
                total = a + b + cin
                s, c = full_adder(a, b, cin)
                print(f"{count:>3} | {a} {b} {cin:>3} | {s:>3} {c:>4} | {total:>6}")
    print("-" * 40)


def print_all_sums():
    """Print all possible a+b+carry combinations."""
    print("\n" + "=" * 50)
    print("ALL 27 COMBINATIONS: A + B + Carry_in")
    print("=" * 50)
    results = []
    for a in (0, 1, 2):
        for b in (0, 1, 2):
            for cin in (0, 1, 2):
                total = a + b + cin
                s = total % 3
                c = total // 3
                results.append((a, b, cin, total, s, c))
    header = f"{'A':>1} + {'B':>1} + {'Cin':>3} = {'Dec':>3} | {'Ternary':>7} | {'Sum':>3} + {'Cout':>4}"
    print(header)
    print("-" * 50)
    for a, b, cin, total, s, c in results:
        ternary_sum = f"{s}{c}" if c > 0 else f"{s}"
        print(f"{a:>1} + {b:>1} + {cin:>3} = {total:>3} | {total:>7} | {s:>3} + {c:>4}")
    print("-" * 50)
    print("Decimal -> Ternary (Sum Carry)")


if __name__ == "__main__":
    print_full_truth_table_detailed()
    print_all_sums()

    print("\n" + "=" * 65)
    print("RIPPLE CARRY ADDER EXAMPLES")
    print("=" * 65)

    examples = [
        ("102", "21"),    # 11 + 7 = 18
        ("20", "10"),     # 6 + 3 = 9
        ("222", "111"),   # 26 + 13 = 39
        ("1000", "1"),    # 27 + 1 = 28
        ("2", "2"),       # 2 + 2 = 4
        ("12", "21"),     # 5 + 7 = 12
    ]

    for a, b in examples:
        s, c = ripple_carry_adder(a, b)
        print(f"  {a} + {b} = {s} (carry: {c})")

    print("\n" + "=" * 65)
    print("DETAILED STEP-BY-STEP")
    print("=" * 65)
    print_ripple_adder_steps("102", "21")

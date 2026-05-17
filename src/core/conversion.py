"""Conversion utilities for binary, decimal, and ternary numbers."""


class Trit:
    """Represent a single ternary digit.

    A Trit can only hold one of the ternary digit values: 0, 1, or 2.
    """

    ALLOWED_VALUES = (0, 1, 2)

    def __init__(self, value):
        if not isinstance(value, int):
            raise ValueError("Trit value must be an integer.")
        if value not in self.ALLOWED_VALUES:
            raise ValueError("Trit value must be 0, 1, or 2.")

        self.value = value

    def __repr__(self):
        return f"Trit({self.value})"

    def __str__(self):
        return str(self.value)


def validate_binary(binary):
    """Validate that a string contains only binary digits (0 or 1)."""
    if not isinstance(binary, str) or not binary:
        raise ValueError("Binary input must be a non-empty string.")

    if any(char not in "01" for char in binary):
        raise ValueError("Binary input may only contain 0 and 1.")

    return True


def validate_ternary(ternary):
    """Validate that a string contains only ternary digits (0, 1, or 2)."""
    if not isinstance(ternary, str) or not ternary:
        raise ValueError("Ternary input must be a non-empty string.")

    if any(char not in "012" for char in ternary):
        raise ValueError("Ternary input may only contain 0, 1, and 2.")

    return True


def binary_to_decimal(binary):
    """Convert a binary string to its decimal integer value."""
    validate_binary(binary)

    decimal_value = 0
    for index, digit in enumerate(reversed(binary)):
        decimal_value += int(digit) * (2 ** index)

    return decimal_value


def decimal_to_ternary(decimal):
    """Convert a non-negative decimal integer to a ternary string."""
    if not isinstance(decimal, int) or decimal < 0:
        raise ValueError("Decimal input must be a non-negative integer.")

    if decimal == 0:
        return "0"

    digits = []
    while decimal > 0:
        digits.append(str(decimal % 3))
        decimal //= 3

    return "".join(reversed(digits))


def ternary_to_binary(ternary):
    """Convert a ternary string to its binary string equivalent."""
    validate_ternary(ternary)

    decimal_value = 0
    for index, digit in enumerate(reversed(ternary)):
        decimal_value += int(digit) * (3 ** index)

    if decimal_value == 0:
        return "0"

    binary_digits = []
    while decimal_value > 0:
        binary_digits.append(str(decimal_value % 2))
        decimal_value //= 2

    return "".join(reversed(binary_digits))


def ternary_to_decimal(ternary):
    """Convert a ternary string to its decimal integer value."""
    validate_ternary(ternary)

    decimal_value = 0
    for index, digit in enumerate(reversed(ternary)):
        decimal_value += int(digit) * (3 ** index)

    return decimal_value


def decimal_to_binary(decimal):
    """Convert a non-negative decimal integer to a binary string."""
    if not isinstance(decimal, int) or decimal < 0:
        raise ValueError("Decimal input must be a non-negative integer.")

    if decimal == 0:
        return "0"

    binary_digits = []
    while decimal > 0:
        binary_digits.append(str(decimal % 2))
        decimal //= 2

    return "".join(reversed(binary_digits))


def main():
    """Run simple command-line conversion examples."""
    try:
        binary_input = input("Enter a binary number: ").strip()
        decimal_output = binary_to_decimal(binary_input)
        print(f"Binary: {binary_input} -> Decimal: {decimal_output}")

        ternary_output = decimal_to_ternary(decimal_output)
        print(f"Decimal: {decimal_output} -> Ternary: {ternary_output}")

        ternary_input = input("Enter a ternary number: ").strip()
        decimal_output = ternary_to_decimal(ternary_input)
        print(f"Ternary: {ternary_input} -> Decimal: {decimal_output}")

        binary_output = ternary_to_binary(ternary_input)
        print(f"Ternary: {ternary_input} -> Binary: {binary_output}")

    except ValueError as error:
        print(f"Input error: {error}")


if __name__ == "__main__":
    main()


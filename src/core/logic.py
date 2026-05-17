"""
Ternary logic gate implementations.

This module provides simple, beginner-friendly implementations of
ternary logic gates using the trit encoding:

0 = FALSE
1 = NEUTRAL / MAYBE
2 = TRUE

The functions validate inputs and raise clear errors for invalid trits.
"""

# Valid ternary states
VALID_TRITS = (0, 1, 2)


def validate_trit(value):
	"""Validate that `value` is a ternary trit (0, 1, or 2).

	Raises:
		ValueError: if `value` is not one of the valid trits.
	"""
	if value not in VALID_TRITS:
		raise ValueError(f"Invalid trit: {value!r}. Expected one of {VALID_TRITS}.")


def tnot(value):
	"""Ternary NOT gate (TNOT).

	Truth table:
		0 -> 2
		1 -> 1
		2 -> 0

	The neutral state (1) remains unchanged; FALSE and TRUE are swapped.

	Args:
		value (int): input trit

	Returns:
		int: resulting trit after TNOT
	"""
	validate_trit(value)
	mapping = {0: 2, 1: 1, 2: 0}
	return mapping[value]


def tand(a, b):
	"""Ternary AND gate (TAND).

	Implements "minimum-value" logic: the result is the lower of the two
	trit values. This generalizes boolean AND where FALSE < TRUE.

	Args:
		a (int): first trit
		b (int): second trit

	Returns:
		int: min(a, b)
	"""
	validate_trit(a)
	validate_trit(b)
	return min(a, b)


def tor(a, b):
	"""Ternary OR gate (TOR).

	Implements "maximum-value" logic: the result is the higher of the two
	trit values. This generalizes boolean OR where TRUE > FALSE.

	Args:
		a (int): first trit
		b (int): second trit

	Returns:
		int: max(a, b)
	"""
	validate_trit(a)
	validate_trit(b)
	return max(a, b)


def generate_truth_tables():
	"""Print truth tables for TNOT, TAND, and TOR.

	This helper is intended for debugging and visualization in research
	notebooks or the command line. It prints all input combinations.
	"""
	print("TNOT truth table:")
	print("Input -> Output")
	for v in VALID_TRITS:
		print(f" {v} -> {tnot(v)}")

	print("\nTAND truth table:")
	print("A B -> A AND B")
	for a in VALID_TRITS:
		for b in VALID_TRITS:
			print(f" {a} {b} -> {tand(a, b)}")

	print("\nTOR truth table:")
	print("A B -> A OR B")
	for a in VALID_TRITS:
		for b in VALID_TRITS:
			print(f" {a} {b} -> {tor(a, b)}")


if __name__ == "__main__":
	generate_truth_tables()


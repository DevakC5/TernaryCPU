"""SIMDProcessor — simulated SIMD lanes for parallel trit processing.

Models a multi-lane execution unit where each lane holds one
trit. A 4-lane processor processes 4 trits per instruction cycle.
"""

from trinary.ai.activations import ternary_step, trit_to_signed


class SIMDProcessor:
    """SIMD processor with configurable lane count.

    Each lane holds a single ternary digit. Operations execute
    across all lanes simultaneously.

    Args:
        lanes: Number of trit lanes (default 4).
    """

    def __init__(self, lanes=4):
        if lanes < 1:
            raise ValueError("Must have at least 1 lane")
        self.lanes = lanes
        self.registers = [1] * lanes  # all lanes start at neutral (1)
        self.cycles = 0

    def load(self, values):
        """Load trits into all lanes.

        Args:
            values: List of ternary digits.

        Raises:
            ValueError: If length doesn't match lane count.
        """
        if len(values) != self.lanes:
            raise ValueError(
                f"Expected {self.lanes} values, got {len(values)}"
            )
        for v in values:
            if v not in (0, 1, 2):
                raise ValueError(f"Invalid trit: {v}")
        self.registers = list(values)
        self.cycles += 1

    def add(self, other):
        """Element-wise add with another vector.

        Args:
            other: List of ternary digits.

        Returns:
            List of result trits.
        """
        self.cycles += 1
        result = []
        for i in range(self.lanes):
            s = trit_to_signed(self.registers[i]) + trit_to_signed(other[i])
            result.append(ternary_step(s))
        self.registers = result
        return result

    def sub(self, other):
        """Element-wise subtract."""
        self.cycles += 1
        result = []
        for i in range(self.lanes):
            s = trit_to_signed(self.registers[i]) - trit_to_signed(other[i])
            result.append(ternary_step(s))
        self.registers = result
        return result

    def mul(self, other):
        """Element-wise multiply."""
        self.cycles += 1
        result = []
        for i in range(self.lanes):
            s = trit_to_signed(self.registers[i]) * trit_to_signed(other[i])
            result.append(ternary_step(s))
        self.registers = result
        return result

    def max(self, other):
        """Element-wise maximum."""
        self.cycles += 1
        result = [max(self.registers[i], other[i]) for i in range(self.lanes)]
        self.registers = result
        return result

    def min(self, other):
        """Element-wise minimum."""
        self.cycles += 1
        result = [min(self.registers[i], other[i]) for i in range(self.lanes)]
        self.registers = result
        return result

    def dot(self, other):
        """Dot product across all lanes.

        This is a reduction operation — returns a single integer.

        Args:
            other: List of ternary digits.

        Returns:
            Integer dot product (sum of signed products).
        """
        self.cycles += self.lanes
        total = 0
        for i in range(self.lanes):
            total += trit_to_signed(self.registers[i]) * trit_to_signed(other[i])
        return total

    def threshold(self):
        """Apply ternary_step to all lanes."""
        self.cycles += 1
        self.registers = [ternary_step(trit_to_signed(r)) for r in self.registers]
        return self.registers

    def clear(self, value=1):
        """Set all lanes to the same value.

        Args:
            value: Ternary digit (default 1 = neutral).
        """
        if value not in (0, 1, 2):
            raise ValueError(f"Invalid trit: {value}")
        self.registers = [value] * self.lanes
        self.cycles += 1

    def show_state(self):
        """Return an ASCII string showing lane states."""
        lines = [f"SIMD ({self.lanes} lanes, {self.cycles} cycles)"]
        for i in range(self.lanes):
            sym = {0: "-", 1: "0", 2: "+"}.get(self.registers[i], "?")
            lines.append(f"  Lane {i}: trit={self.registers[i]} ({sym})")
        return "\n".join(lines)

    def __repr__(self):
        return f"SIMDProcessor(lanes={self.lanes}, regs={self.registers})"

"""
Ternary Register File.

Simulates R0, R1, R2, R3 registers that store ternary values.
Operations: LOAD, STORE, MOVE.
"""

from trinary.conversion import validate_ternary


class RegisterFile:
    """Ternary register file with 4 registers (R0-R3)."""

    REGISTER_NAMES = ("R0", "R1", "R2", "R3")

    def __init__(self):
        self.registers = {name: "0" for name in self.REGISTER_NAMES}

    def validate_register(self, name):
        """Validate register name."""
        if name not in self.REGISTER_NAMES:
            raise ValueError(f"Invalid register: {name}. Must be one of {self.REGISTER_NAMES}")
        return True

    def validate_value(self, value):
        """Validate ternary value (optional leading -)."""
        if not isinstance(value, str):
            raise ValueError("Register value must be a string")
        body = value[1:] if value and value[0] == "-" else value
        for c in body:
            if c not in "012":
                raise ValueError(f"Invalid trit: {c}. Must be 0, 1, or 2")
        return True

    def load(self, register, value):
        """LOAD - Load a ternary value into a register.

        Args:
            register (str): Register name (R0, R1, R2, R3)
            value (str): Ternary value to store

        Returns:
            str: The loaded value

        Example:
            load("R0", "102") -> "102"
        """
        self.validate_register(register)
        self.validate_value(value)
        self.registers[register] = value
        return value

    def store(self, register):
        """STORE - Get the value stored in a register.

        Args:
            register (str): Register name (R0, R1, R2, R3)

        Returns:
            str: The value stored in the register

        Example:
            store("R0") -> "102"
        """
        self.validate_register(register)
        return self.registers[register]

    def move(self, src, dst):
        """MOVE - Copy value from source register to destination register.

        Args:
            src (str): Source register name (R0, R1, R2, R3)
            dst (str): Destination register name (R0, R1, R2, R3)

        Returns:
            str: The value copied to destination

        Example:
            move("R0", "R1") -> "102"  (copies R0's value to R1)
        """
        self.validate_register(src)
        self.validate_register(dst)
        value = self.registers[src]
        self.registers[dst] = value
        return value

    def clear(self, register):
        """CLEAR - Set a register to "0".

        Args:
            register (str): Register name (R0, R1, R2, R3)

        Returns:
            str: "0"
        """
        self.validate_register(register)
        self.registers[register] = "0"
        return "0"

    def dump(self):
        """Dump all register contents."""
        return dict(self.registers)

    def __repr__(self):
        return f"RegisterFile({self.registers})"


def main():
    """Interactive register demo."""
    rf = RegisterFile()

    print("=" * 50)
    print("TERNARY REGISTER FILE")
    print("=" * 50)

    print("\n--- LOAD operations ---")
    print(f"LOAD R0, '102' -> {rf.load('R0', '102')}")
    print(f"LOAD R1, '21'  -> {rf.load('R1', '21')}")
    print(f"LOAD R2, '0'   -> {rf.load('R2', '0')}")
    print(f"LOAD R3, '222' -> {rf.load('R3', '222')}")

    print("\n--- STORE operations ---")
    print(f"STORE R0 -> {rf.store('R0')}")
    print(f"STORE R1 -> {rf.store('R1')}")

    print("\n--- MOVE operations ---")
    print(f"MOVE R0 -> R2: {rf.move('R0', 'R2')}")
    print(f"STORE R2 -> {rf.store('R2')}")

    print("\n--- DUMP all registers ---")
    print(rf.dump())

    print("=" * 50)


if __name__ == "__main__":
    main()
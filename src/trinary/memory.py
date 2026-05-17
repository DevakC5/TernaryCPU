"""
Ternary Memory (RAM) Simulator.

Simulates addressable memory for the CPU.
Stores ternary values at integer addresses.
"""



class Memory:
    """Ternary RAM - addressable memory for CPU."""

    def __init__(self, size=256):
        """Initialize memory.

        Args:
            size (int): Number of addressable locations (default 256)
        """
        self.size = size
        self.data = {i: "0" for i in range(size)}

    def validate_address(self, address):
        """Validate memory address."""
        if not isinstance(address, int):
            raise ValueError(f"Address must be an integer, got {type(address)}")
        if address < 0 or address >= self.size:
            raise ValueError(f"Address {address} out of range (0-{self.size-1})")
        return True

    def validate_value(self, value):
        """Validate ternary value (optional leading -)."""
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        body = value[1:] if value and value[0] == "-" else value
        for c in body:
            if c not in "012":
                raise ValueError(f"Invalid trit: {c}. Must be 0, 1, or 2")
        return True

    def store(self, address, value):
        """STOREM - Store value at address.

        Args:
            address (int): Memory address (0 to size-1)
            value (str): Ternary value to store

        Returns:
            str: The stored value

        Example:
            memory.store(100, "102")  # Store "102" at address 100
        """
        self.validate_address(address)
        self.validate_value(value)
        self.data[address] = value
        return value

    def load(self, address):
        """LOADM - Load value from address.

        Args:
            address (int): Memory address (0 to size-1)

        Returns:
            str: The value stored at address

        Example:
            memory.load(100)  # Returns "102"
        """
        self.validate_address(address)
        return self.data[address]

    def clear(self, address):
        """Clear a memory location (set to "0").

        Args:
            address (int): Memory address

        Returns:
            str: "0"
        """
        self.validate_address(address)
        self.data[address] = "0"
        return "0"

    def clear_all(self):
        """Clear entire memory."""
        self.data = {i: "0" for i in range(self.size)}

    def dump(self, start=0, end=None):
        """Dump memory contents.

        Args:
            start (int): Start address
            end (int): End address (default: start + 16)

        Returns:
            dict: Memory contents in range
        """
        if end is None:
            end = min(start + 16, self.size)
        return {addr: self.data[addr] for addr in range(start, end)}

    def dump_hex(self, start=0, end=None):
        """Dump memory as hex-style table.

        Args:
            start (int): Start address
            end (int): End address (default: start + 16)
        """
        if end is None:
            end = min(start + 16, self.size)

        print(f"\n{'ADDR':>4} | {'VALUE':>10}")
        print("-" * 20)
        for addr in range(start, end):
            print(f"{addr:>4} | {self.data[addr]:>10}")

    def __repr__(self):
        return f"Memory(size={self.size}, used={len([v for v in self.data.values() if v != '0'])})"


def demo():
    """Demo memory operations."""
    mem = Memory(size=256)

    print("=" * 50)
    print("TERNARY MEMORY (RAM) SIMULATOR")
    print("=" * 50)

    print("\n--- STORE operations ---")
    print(f"STOREM 100, '102' -> {mem.store(100, '102')}")
    print(f"STOREM 101, '21'  -> {mem.store(101, '21')}")
    print(f"STOREM 200, '0'   -> {mem.store(200, '0')}")

    print("\n--- LOAD operations ---")
    print(f"LOADM 100 -> {mem.load(100)}")
    print(f"LOADM 101 -> {mem.load(101)}")

    print("\n--- DUMP memory (0-15) ---")
    mem.dump_hex(0, 16)

    print("\n--- DUMP memory (96-112) ---")
    mem.dump_hex(96, 112)

    print("=" * 50)


if __name__ == "__main__":
    demo()
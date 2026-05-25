"""
Ternary Assembler.

Converts symbolic assembly with labels to addresses.

Features:
- Symbolic labels (e.g., "start:", "loop:")
- Auto-resolves labels to addresses
- Two-pass assembly (labels first, then code)

Example:
    start:
        LOAD R0 10
        CALL add_func
        HALT

    add_func:
        ADD R0 R1
        RET

Produces:
    0: LOAD R0 10
    1: CALL 4      # resolved to address of add_func
    2: HALT
    3: (padding for alignment)
    4: ADD R0 R1
    5: RET
"""

from trinary.cpu import CPU


class Assembler:
    """Two-pass assembler for ternary CPU."""

    OPCODES = {
        "LOAD", "MOV", "CLR",
        "ADD", "SUB", "MUL", "DIV", "AND", "OR", "NOT",
        "CMP", "JMP", "JZ", "JNZ",
        "PUSH", "POP", "CALL", "RET", "HALT",
        "STOREM", "LOADM",
        "INT", "IRET", "EI", "DI", "SETIVT", "SETTIMER",
        "TLOADW", "TSTOREW", "TVECADD", "TMATMUL", "TDOT", "TACT",
    }

    BRANCH_OPCODES = {"JMP", "JZ", "JNZ", "CALL"}

    def __init__(self):
        self.labels = {}

    def parse_line(self, line):
        """Parse a line into (label, opcode, operands).

        Returns:
            tuple: (label_or_none, opcode_or_none, operands_list)
        """
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            return None, None, []
        for marker in ("#", ";"):
            if marker in line:
                line = line[:line.index(marker)].strip()

        if ":" in line:
            label, rest = line.split(":", 1)
            label = label.strip()
            rest = rest.strip()
            if not rest:
                return label, None, []
            parts = rest.split()
            opcode = parts[0].upper()
            operands = parts[1:] if len(parts) > 1 else []
            return label, opcode, operands

        parts = line.split()
        opcode = parts[0].upper()
        operands = parts[1:] if len(parts) > 1 else []
        return None, opcode, operands

    def first_pass(self, lines):
        """First pass: collect all labels and their addresses.

        Args:
            lines (list): Source code lines

        Returns:
            int: Number of instruction lines (excluding labels alone)
        """
        self.labels = {}
        address = 0
        for line in lines:
            label, opcode, operands = self.parse_line(line)
            if label and opcode is None:
                self.labels[label] = address
            elif opcode is not None:
                address += 1
        return address

    def resolve_operand(self, operand):
        """Resolve an operand (label -> address or keep as-is).

        Args:
            operand (str): Operand to resolve

        Returns:
            str: Resolved operand
        """
        if operand in self.labels:
            return str(self.labels[operand])
        return operand

    def second_pass(self, lines):
        """Second pass: assemble with resolved labels.

        Args:
            lines (list): Source code lines

        Returns:
            list: Assembled program (list of instruction strings)
        """
        program = []
        for line in lines:
            label, opcode, operands = self.parse_line(line)
            if opcode is None:
                continue
            resolved_ops = [self.resolve_operand(op) for op in operands]
            instruction = " ".join([opcode] + resolved_ops)
            program.append(instruction)
        return program

    def assemble(self, source):
        """Assemble source code.

        Args:
            source (str): Assembly source code

        Returns:
            tuple: (program_list, label_dict)
        """
        lines = source.strip().split("\n")
        self.first_pass(lines)
        program = self.second_pass(lines)
        return program, self.labels


def demo():
    """Demo assembler with labels."""
    asm = Assembler()

    source = """
# Simple demo of label-based assembly

start:
    LOAD R0 10
    LOAD R1 12
    CALL add_func
    HALT

add_func:
    ADD R0 R1
    MOV R2 R0
    RET
"""

    print("=" * 60)
    print("TERNARY ASSEMBLER - LABEL RESOLUTION")
    print("=" * 60)

    print("\n--- Source Code ---")
    print(source)

    program, labels = asm.assemble(source)

    print("--- Resolved Labels ---")
    for label, addr in sorted(labels.items()):
        print(f"  {label}: {addr}")

    print("\n--- Assembled Program ---")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")

    print("\n--- Execution ---")
    print("-" * 60)

    cpu = CPU()
    cpu.load_program(program)
    cpu.run()


def demo_loop():
    """Demo with loop/branch."""
    asm = Assembler()

    source = """
# Countdown loop demo (5 in ternary is 12, 1 in ternary is 1)

    LOAD R0 12
    LOAD R1 0
    LOAD R2 1

loop:
    CMP R0 R1
    JZ done
    ADD R1 R0
    SUB R0 R2
    JMP loop

done:
    HALT
"""

    print("\n" + "=" * 60)
    print("LOOP DEMO")
    print("=" * 60)

    program, labels = asm.assemble(source)
    print(f"Labels: {labels}")
    print("Program:")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")

    print("\n--- Execution ---")
    cpu = CPU()
    cpu.load_program(program)
    cpu.run()


if __name__ == "__main__":
    demo()
    demo_loop()
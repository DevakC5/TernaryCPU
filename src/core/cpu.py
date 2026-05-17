"""
Ternary CPU Simulator.

Implements a fetch-decode-execute cycle with a simple ISA.

Instruction Format:
    OPCODE dst src  (two operands)
    OPCODE dst      (one operand)

Opcodes:
    LOAD  dst value    - Load immediate into register
    MOV   dst src     - Copy src register to dst register
    CLR   dst         - Clear register (set to "0")
    ADD   dst src     - dst = dst + src
    SUB   dst src     - dst = dst - src
    AND   dst src     - dst = dst AND src
    OR    dst src     - dst = dst OR src
    NOT   dst         - dst = NOT dst
    CMP   dst src     - Compare dst and src (sets internal flags)
    JMP   addr        - Jump to address
    JZ    addr        - Jump if zero/equal
    JNZ   addr        - Jump if not zero

Registers: R0, R1, R2, R3
"""

import sys
from pathlib import Path

_src = Path(__file__).resolve().parent.parent
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from core.registers import RegisterFile
from core.alu import alu


class CPU:
    """Ternary CPU with fetch-decode-execute cycle."""

    OPCODES = {
        "LOAD", "MOV", "CLR",
        "ADD", "SUB", "AND", "OR", "NOT",
        "CMP", "JMP", "JZ", "JNZ"
    }

    def __init__(self):
        self.registers = RegisterFile()
        self.pc = 0
        self.flags = {
            "ZERO": False,
            "EQUAL": False,
            "GREATER": False,
            "LESS": False,
        }
        self.program = []
        self.halted = False

    def reset(self):
        """Reset CPU state."""
        self.registers = RegisterFile()
        self.pc = 0
        self.flags = {"ZERO": False, "EQUAL": False, "GREATER": False, "LESS": False}
        self.halted = False

    def load_program(self, instructions):
        """Load program into memory.

        Args:
            instructions (list): List of instruction strings
        """
        self.program = list(instructions)
        self.pc = 0
        self.halted = False

    def parse_instruction(self, instruction):
        """Parse instruction into (opcode, operands).

        Args:
            instruction (str): e.g., "LOAD R0 102"

        Returns:
            tuple: (opcode, [operands])
        """
        parts = instruction.strip().split()
        if not parts:
            return None, []

        opcode = parts[0].upper()
        if opcode not in self.OPCODES:
            raise ValueError(f"Invalid opcode: {opcode}")

        operands = parts[1:]
        return opcode, operands

    def execute_instruction(self, instruction):
        """Execute a single instruction.

        Args:
            instruction (str): e.g., "ADD R0 R1"
        """
        if self.halted:
            return

        opcode, operands = self.parse_instruction(instruction)

        if opcode == "LOAD":
            dst, value = operands
            self.registers.load(dst, value)

        elif opcode == "MOV":
            dst, src = operands
            self.registers.move(src, dst)

        elif opcode == "CLR":
            dst = operands[0]
            self.registers.clear(dst)

        elif opcode == "ADD":
            dst, src = operands
            a = self.registers.store(dst)
            b = self.registers.store(src)
            result, _ = alu("ADD", a, b)
            self.registers.load(dst, result)

        elif opcode == "SUB":
            dst, src = operands
            a = self.registers.store(dst)
            b = self.registers.store(src)
            result, _ = alu("SUB", a, b)
            self.registers.load(dst, result)

        elif opcode == "AND":
            dst, src = operands
            a = self.registers.store(dst)
            b = self.registers.store(src)
            result, _ = alu("AND", a, b)
            self.registers.load(dst, result)

        elif opcode == "OR":
            dst, src = operands
            a = self.registers.store(dst)
            b = self.registers.store(src)
            result, _ = alu("OR", a, b)
            self.registers.load(dst, result)

        elif opcode == "NOT":
            dst = operands[0]
            a = self.registers.store(dst)
            result, _ = alu("NOT", a)
            self.registers.load(dst, result)

        elif opcode == "CMP":
            dst, src = operands
            a = self.registers.store(dst)
            b = self.registers.store(src)
            result, _ = alu("CMP", a, b)
            self.flags["EQUAL"] = (result == "EQ")
            self.flags["GREATER"] = (result == "GT")
            self.flags["LESS"] = (result == "LT")
            self.flags["ZERO"] = (a == b or a == "0")

        elif opcode == "JMP":
            addr = int(operands[0])
            self.pc = addr
            return

        elif opcode == "JZ":
            if self.flags["ZERO"] or self.flags["EQUAL"]:
                addr = int(operands[0])
                self.pc = addr
                return

        elif opcode == "JNZ":
            if not self.flags["ZERO"] and not self.flags["EQUAL"]:
                addr = int(operands[0])
                self.pc = addr
                return

        self.pc += 1

    def step(self):
        """Execute one instruction (fetch-decode-execute)."""
        if self.pc >= len(self.program):
            self.halted = True
            return False

        instruction = self.program[self.pc]
        self.execute_instruction(instruction)
        return not self.halted

    def run(self, verbose=True):
        """Run the entire program.

        Args:
            verbose (bool): Print each step

        Returns:
            dict: Final register state
        """
        step_num = 0
        while not self.halted and self.pc < len(self.program):
            step_num += 1
            instruction = self.program[self.pc]
            old_pc = self.pc
            old_regs = self.registers.dump()
            self.step()
            new_regs = self.registers.dump()
            if verbose:
                print(f"[{step_num:3}] PC:{old_pc:2}->{self.pc:2} | {instruction:20} | {new_regs}")

        if verbose:
            print(f"\n--- HALTED at PC={self.pc} ---")
            print(f"Registers: {self.registers.dump()}")
            print(f"Flags: {self.flags}")

        return self.registers.dump()


def demo():
    """Demo program."""
    cpu = CPU()

    program = [
        "LOAD R0 102",
        "LOAD R1 21",
        "ADD R0 R1",
        "MOV R2 R0",
        "CLR R1",
    ]

    print("=" * 70)
    print("TERNARY CPU - FETCH-DECODE-EXECUTE")
    print("=" * 70)
    print("\nProgram:")
    for i, instr in enumerate(program):
        print(f"  {i}: {instr}")
    print("\nExecution:")
    print("-" * 70)

    cpu.load_program(program)
    cpu.run(verbose=True)

    print("=" * 70)


def demo_sub():
    """Demo subtraction program."""
    cpu = CPU()

    program = [
        "LOAD R0 102",
        "LOAD R1 21",
        "SUB R0 R1",
    ]

    print("\n--- SUB Demo ---")
    cpu.load_program(program)
    cpu.run()


if __name__ == "__main__":
    demo()
    demo_sub()
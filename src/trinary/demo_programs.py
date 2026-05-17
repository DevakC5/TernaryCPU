"""
Demo Programs for Ternary Computer.

Examples: Countdown, Factorial, Fibonacci, Calculator.
"""

from trinary.cpu import CPU
from trinary.assembler import Assembler


def demo_countdown():
    """Countdown from N to 0."""
    print("=" * 60)
    print("DEMO: COUNTDOWN LOOP")
    print("=" * 60)

    source = """
start:
    LOAD R0 12
    LOAD R1 0
    LOAD R2 1
loop:
    CMP R0 R1
    JZ done
    SUB R0 R2
    JMP loop
done:
    HALT
"""

    asm = Assembler()
    program, labels = asm.assemble(source)

    print(f"\nProgram: {program}")
    print(f"Labels: {labels}")

    print("\n--- Execution ---")
    cpu = CPU()
    cpu.load_program(program)
    cpu.run()

    print(f"\nResult: Countdown finished, R0 = {cpu.registers.store('R0')}")


def demo_fibonacci():
    """Fibonacci sequence (manual unroll)."""
    print("\n" + "=" * 60)
    print("DEMO: FIBONACCI")
    print("=" * 60)

    source = """
    LOAD R0 0
    LOAD R1 1
    LOAD R2 0
    ADD R2 R0
    ADD R2 R1
    MOV R0 R1
    MOV R1 R2
    LOAD R2 0
    ADD R2 R0
    ADD R2 R1
    MOV R0 R1
    MOV R1 R2
    HALT
"""

    asm = Assembler()
    program, labels = asm.assemble(source)

    print(f"Program: {program}\n")
    cpu = CPU()
    cpu.load_program(program)
    cpu.run()

    print(f"\nResult: R1 = {cpu.registers.store('R1')} (F(3)=2 in ternary)")


def demo_factorial():
    """Factorial: 3! = 6."""
    print("\n" + "=" * 60)
    print("DEMO: FACTORIAL (3!)")
    print("=" * 60)

    source = """
    LOAD R0 1
    ADD R0 R0
    MOV R1 R0
    ADD R0 R1
    ADD R0 R1
    HALT
"""

    asm = Assembler()
    program, labels = asm.assemble(source)
    print(f"Program: {program}\n")
    cpu = CPU()
    cpu.load_program(program)
    cpu.run()
    print(f"\nResult: R0 = {cpu.registers.store('R0')} (3! = 6 = 20 in ternary)")


def demo_sum():
    """Sum of 1 to N."""
    print("\n" + "=" * 60)
    print("DEMO: SUM OF 1 TO N")
    print("=" * 60)

    source = """
start:
    LOAD R0 12
    LOAD R1 0
    LOAD R2 0
    LOAD R3 1
loop:
    ADD R2 R3
    CMP R2 R0
    JZ done
    ADD R1 R2
    JMP loop
done:
    HALT
"""

    asm = Assembler()
    program, labels = asm.assemble(source)

    print(f"Program: {program}")
    print(f"Labels: {labels}")

    print("\n--- Execution ---")
    cpu = CPU()
    cpu.load_program(program)
    cpu.run()

    print(f"\nResult: Sum = {cpu.registers.store('R1')}")
    print("         (15 in decimal = 120 in ternary)")


def demo_calculator():
    """Simple calculator with add/subtract."""
    print("\n" + "=" * 60)
    print("DEMO: SIMPLE CALCULATOR")
    print("=" * 60)

    source = """
start:
    LOAD R0 101
    LOAD R1 12
    ADD R0 R1
    LOAD R2 10
    SUB R0 R2
    LOAD R3 2
    ADD R0 R3
    HALT
"""

    asm = Assembler()
    program, labels = asm.assemble(source)

    print("Operation: ((10 + 5) - 3) + 2 = 14\n")
    print(f"Program: {program}")

    print("\n--- Execution ---")
    cpu = CPU()
    cpu.load_program(program)
    cpu.run()

    print(f"\nResult: {cpu.registers.store('R0')} (should be 14 = 112 in ternary)")


def demo_subroutine_average():
    """Calculate sum using subroutine."""
    print("\n" + "=" * 60)
    print("DEMO: SUBROUTINE")
    print("=" * 60)

    source = """
main:
    LOAD R0 10
    LOAD R1 20
    CALL add_routines
    HALT

add_routines:
    ADD R0 R1
    RET
"""

    asm = Assembler()
    program, labels = asm.assemble(source)

    print(f"Program: {program}\n")
    cpu = CPU()
    cpu.load_program(program)
    cpu.run()

    print(f"\nSum result: R0 = {cpu.registers.store('R0')}")
    print("Note: Division requires additional loop implementation")


def demo_logical_operations():
    """Demo logical operations."""
    print("\n" + "=" * 60)
    print("DEMO: LOGICAL OPERATIONS")
    print("=" * 60)

    source = """
start:
    LOAD R0 102
    LOAD R1 21
    AND R0 R1
    HALT
"""

    asm = Assembler()
    program, labels = asm.assemble(source)

    print(f"Program: {program}\n")

    # Run step by step to show each operation
    cpu = CPU()

    # AND
    cpu.load_program(["LOAD R0 102", "LOAD R1 21", "AND R0 R1", "HALT"])
    cpu.run(verbose=False)
    print(f"AND result: R0 = {cpu.registers.store('R0')}")

    # OR
    cpu.load_program(["LOAD R0 102", "LOAD R1 21", "OR R0 R1", "HALT"])
    cpu.run(verbose=False)
    print(f"OR result: R0 = {cpu.registers.store('R0')}")

    # NOT
    cpu.load_program(["LOAD R0 102", "NOT R0", "HALT"])
    cpu.run(verbose=False)
    print(f"NOT result: R0 = {cpu.registers.store('R0')}")


def demo_comparison():
    """Demo comparison and conditional jumps."""
    print("\n" + "=" * 60)
    print("DEMO: COMPARISON & CONDITIONAL JUMPS")
    print("=" * 60)

    source = """
start:
    LOAD R0 101
    LOAD R1 202
    CMP R0 R1
    HALT
"""

    asm = Assembler()
    program, labels = asm.assemble(source)

    print("Comparing 10 vs 20:\n")
    cpu = CPU()
    cpu.load_program(program)
    cpu.run()

    print(f"Flags: {cpu.flags}")
    print(f"Expected: LESS (10 < 20)")


def demo_stack():
    """Demo push/pop operations."""
    print("\n" + "=" * 60)
    print("DEMO: STACK OPERATIONS")
    print("=" * 60)

    source = """
start:
    LOAD R0 10
    LOAD R1 20
    LOAD R2 100
    PUSH R0
    PUSH R1
    PUSH R2
    POP R3
    POP R2
    POP R1
    HALT
"""

    asm = Assembler()
    program, labels = asm.assemble(source)

    print(f"Program: {program}\n")
    cpu = CPU()
    cpu.load_program(program)
    cpu.run()

    print("\nStack visualization:")
    print("  PUSH R0: 255->10")
    print("  PUSH R1: 254->20")
    print("  PUSH R2: 253->100")
    print("  POP R3:  <-100")
    print("  POP R2:  <-20")
    print("  POP R1:  <-10")

    print(f"\nFinal: R1={cpu.registers.store('R1')}, R2={cpu.registers.store('R2')}, R3={cpu.registers.store('R3')}")


def run_all_demos():
    """Run demo programs."""
    demo_countdown()
    demo_sum()
    demo_calculator()
    demo_logical_operations()
    demo_comparison()
    demo_stack()
    demo_fibonacci()
    demo_factorial()

    print("\n" + "=" * 60)
    print("ALL DEMOS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_all_demos()
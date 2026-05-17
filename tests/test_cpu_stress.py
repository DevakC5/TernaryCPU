from trinary.cpu import CPU
from trinary.assembler import Assembler


asm = Assembler()


def assemble(source):
    program, labels = asm.assemble(source)
    return program


class TestCPUStress:
    def test_5deep_nested_calls(self):
        """5-level call chain. Each doubles: 2 * 2^5 = 64 (ternary 2101)."""
        cpu = CPU()
        cpu.load_program(assemble("""
start:
    LOAD R0 2
    CALL level1
    HALT
level1:
    ADD R0 R0
    CALL level2
    RET
level2:
    ADD R0 R0
    CALL level3
    RET
level3:
    ADD R0 R0
    CALL level4
    RET
level4:
    ADD R0 R0
    CALL level5
    RET
level5:
    ADD R0 R0
    RET
"""))
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "2101"

    def test_push_pop_stack_10(self):
        """Push 1..10, pop back, verify each. Uses CMP register-to-register."""
        cpu = CPU()
        cpu.load_program(assemble("""
start:
    LOAD R0 0
    LOAD R1 1
    LOAD R2 0
    LOAD R3 101
push_loop:
    ADD R0 R1
    PUSH R0
    CMP R0 R3
    JZ pop_start
    JMP push_loop
pop_start:
pop_loop:
    POP R2
    CMP R0 R2
    JNZ fail
    SUB R0 R1
    CLR R3
    CMP R0 R3
    JZ done
    JMP pop_loop
fail:
    LOAD R0 0
    HALT
done:
    HALT
"""))
        cpu.run(verbose=False)
        assert cpu.registers.store("R2") == "1"

    def test_long_countdown(self):
        """Count down from 30 (ternary 1010) to 0 via loop."""
        cpu = CPU()
        cpu.load_program(assemble("""
start:
    LOAD R0 1010
    LOAD R1 0
    LOAD R2 1
loop:
    CMP R0 R1
    JZ done
    SUB R0 R2
    JMP loop
done:
    HALT
"""))
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "0"

    def test_all_alu_ops_sequential(self):
        """Chain every ALU op, end with CMP + JZ."""
        cpu = CPU()
        cpu.load_program(assemble("""
start:
    LOAD R0 10
    LOAD R1 2
    ADD R0 R1
    SUB R0 R1
    MUL R0 R1
    DIV R0 R1
    AND R0 R1
    OR R0 R1
    NOT R0
    LOAD R0 10
    LOAD R1 10
    CMP R0 R1
    JZ ok
    LOAD R2 1
    HALT
ok:
    HALT
"""))
        cpu.run(verbose=False)
        assert cpu.flags["EQUAL"]

    def test_heavy_instruction_count(self):
        """200 ADD ops -> R0 = 200 decimal = 21102 ternary."""
        cpu = CPU()
        prog = ["LOAD R0 0", "LOAD R1 1"]
        for _ in range(200):
            prog.append("ADD R0 R1")
        prog.append("HALT")
        cpu.load_program(prog)
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "21102"

    def test_mul_large_values(self):
        """MUL: 10 * 2 = 20 (ternary 202)."""
        cpu = CPU()
        cpu.load_program(assemble("""
start:
    LOAD R0 101
    LOAD R1 2
    MUL R0 R1
    HALT
"""))
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "202"

    def test_all_conditional_jumps(self):
        """Exercise JMP, JZ, JNZ with CMP + flags."""
        cpu = CPU()
        cpu.load_program(assemble("""
start:
    LOAD R0 1
    LOAD R1 1
    CMP R0 R1
    JZ eq_jump
    JMP fail
eq_jump:
    LOAD R2 1
    LOAD R0 1
    LOAD R1 2
    CMP R0 R1
    JNZ neq_jump
    JMP fail
neq_jump:
    LOAD R3 1
    HALT
fail:
    HALT
"""))
        cpu.run(verbose=False)
        assert cpu.registers.store("R2") == "1"
        assert cpu.registers.store("R3") == "1"

    def test_mixed_arithmetic_chain(self):
        """(10+5)*2-3 = 27. No HALT until end."""
        cpu = CPU()
        cpu.load_program(assemble("""
start:
    LOAD R0 101
    LOAD R1 12
    ADD R0 R1
    LOAD R1 2
    MUL R0 R1
    LOAD R1 10
    SUB R0 R1
    HALT
"""))
        cpu.run(verbose=False)

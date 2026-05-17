from trinary.cpu import CPU


class TestCPU:
    def test_add(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 102", "LOAD R1 21", "ADD R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "200"

    def test_sub(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 102", "LOAD R1 21", "SUB R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "11"

    def test_mul(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 2", "LOAD R1 2", "MUL R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "11"

    def test_div(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 10", "LOAD R1 2", "DIV R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "1"

    def test_and(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 102", "LOAD R1 21", "AND R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "001"

    def test_or(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 102", "LOAD R1 21", "OR R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "122"

    def test_not(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 102", "NOT R0", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "120"

    def test_cmp_eq(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 10", "LOAD R1 10", "CMP R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.flags["EQUAL"]

    def test_cmp_gt(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 10", "LOAD R1 1", "CMP R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.flags["GREATER"]

    def test_cmp_lt(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 1", "LOAD R1 10", "CMP R0 R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.flags["LESS"]

    def test_jmp(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 1", "JMP 3", "LOAD R0 2", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "1"

    def test_push_pop(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 10", "PUSH R0", "POP R1", "HALT"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R1") == "10"

    def test_call_ret(self):
        cpu = CPU()
        cpu.load_program([
            "LOAD R0 1",
            "CALL 4",
            "MOV R3 R0",   # save result in R3
            "HALT",
            "LOAD R0 2",   # subroutine at address 4
            "RET",
        ])
        cpu.run(verbose=False)
        assert cpu.registers.store("R3") == "2"

    def test_halt(self):
        cpu = CPU()
        cpu.load_program(["LOAD R0 1", "HALT", "LOAD R0 2"])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "1"

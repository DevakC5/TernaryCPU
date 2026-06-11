from trinary.cpu import CPU, StackOverflowError, StackUnderflowError


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

    def test_ei_di(self):
        cpu = CPU()
        cpu.load_program(["EI", "DI", "HALT"])
        cpu.run(verbose=False)
        assert not cpu.iflag

    def test_setivt(self):
        cpu = CPU()
        cpu.load_program(["SETIVT 0 10", "SETIVT 1 20", "HALT"])
        cpu.run(verbose=False)
        assert cpu.ivt[0] == 10
        assert cpu.ivt[1] == 20

    def test_settimer(self):
        cpu = CPU()
        cpu.load_program(["SETTIMER 50", "HALT"])
        cpu.run(verbose=False)
        assert cpu.timer_period == 50
        assert cpu.timer_counter > 0

    def test_int_and_iret(self):
        """INT pushes context, jumps to handler; IRET restores context."""
        cpu = CPU()
        cpu.load_program([
            "SETIVT 0 3",
            "INT 0",
            "HALT",
            "LOAD R0 1",
            "IRET",
        ])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "0"

    def test_int_disables_interrupts(self):
        """INT clears iflag so nested interrupts are blocked until EI."""
        cpu = CPU()
        cpu.load_program([
            "SETIVT 0 4",
            "SETIVT 1 6",
            "INT 0",
            "HALT",
            "INT 1",
            "IRET",
            "LOAD R0 1",
            "IRET",
        ])
        cpu.run(verbose=False)
        assert cpu.registers.store("R0") == "0"

    def test_interrupt_via_step(self):
        """Single interrupt: EI → trigger → HALT → handler → IRET → HALT."""
        cpu = CPU()
        cpu.load_program([
            "SETIVT 0 3",
            "EI",
            "HALT",
            "LOAD R0 1",
            "IRET",
        ])

        cpu.step()  # 0: SETIVT 0 3 → IVT[0]=3
        cpu.step()  # 1: EI → iflag=T
        cpu.pending_interrupt = 0

        cpu.step()  # 2: HALT, then interrupt: push PC=2, PC=3
        assert cpu.pc == 3
        assert not cpu.iflag

        cpu.step()  # 3: LOAD R0 1
        assert cpu.registers.store("R0") == "1"

        cpu.step()  # 4: IRET → pop PC=2, iflag=T
        assert cpu.pc == 2
        assert cpu.iflag

        cpu.step()  # 2: HALT again → halted
        assert cpu.halted

    def test_interrupt_preserves_main_state(self):
        """Register state after interrupt preserves main values."""
        cpu = CPU()
        cpu.load_program([
            "SETIVT 0 7",
            "LOAD R0 0",
            "LOAD R1 1",
            "LOAD R2 0",
            "EI",
            "ADD R2 R1",
            "HALT",
            "ADD R0 R1",
            "IRET",
        ])
        cpu.step()  # 0: SETIVT
        cpu.step(); cpu.step(); cpu.step()  # 1-3: LOADs
        cpu.step()  # 4: EI
        cpu.pending_interrupt = 0

        cpu.step()  # 5: ADD R2 R1, then interrupt: push PC=6, PC=7
        assert cpu.registers.store("R2") == "1"
        assert cpu.pc == 7

        cpu.step()  # 7: ADD R0 R1
        assert cpu.registers.store("R0") == "1"

        cpu.step()  # 8: IRET → pop PC=6
        assert cpu.pc == 6

        cpu.step()  # 6: HALT
        assert cpu.halted
        assert cpu.registers.store("R2") == "1"
        assert cpu.registers.store("R0") == "0"

    def test_nested_interrupt_soft_via_int(self):
        """Nested interrupts via INT: int0 handler calls int1."""
        cpu = CPU()
        # int0 handler at 5-7: EI, INT 1, IRET
        # int1 handler at 8-9: LOAD R0 1, IRET
        cpu.load_program([
            "SETIVT 0 5",
            "SETIVT 1 8",
            "EI",
            "HALT",
            "",
            "EI",
            "INT 1",
            "IRET",
            "LOAD R0 1",
            "IRET",
        ])
        cpu.step()  # 0: SETIVT 0 5
        cpu.step()  # 1: SETIVT 1 8
        cpu.step()  # 2: EI → iflag=T
        cpu.pending_interrupt = 0

        cpu.step()  # 3: HALT → service int0: push PC=3, PC=5
        assert cpu.pc == 5
        assert not cpu.iflag

        cpu.step()  # 5: EI → iflag=T
        cpu.step()  # 6: INT 1 → push PC+1=7, PC=8, iflag=F
        assert cpu.pc == 8

        cpu.step()  # 8: LOAD R0 1
        assert cpu.registers.store("R0") == "1"

        cpu.step()  # 9: IRET → pop PC=7, iflag=T
        assert cpu.pc == 7

        cpu.step()  # 7: IRET (in int0) → pop PC=3, iflag=T
        assert cpu.pc == 3

        cpu.step()  # 3: HALT
        assert cpu.halted

    def test_timer_decrements_and_fires(self):
        """Timer counter decrements and sets pending_interrupt at 0."""
        cpu = CPU()
        cpu.load_program(["SETTIMER 5", "HALT"])
        cpu.step()  # SETTIMER: period=5, counter=5, cost=1 → counter=4
        assert cpu.timer_period == 5
        assert cpu.timer_counter == 4
        assert cpu.pending_interrupt is None

        cpu.timer_counter = 1
        cpu.step()  # HALT: counter=1-1=0 → fire! counter=5, pending=0
        assert cpu.pending_interrupt == 0
        assert cpu.timer_counter == 5

    def test_stack_overflow_on_interrupt(self):
        """INT raises StackOverflowError when stack is full."""
        cpu = CPU()
        cpu.load_program([
            "SETIVT 0 4",
            "INT 0",
            "HALT",
            "IRET",
        ])
        cpu.sp = 127
        import pytest
        with pytest.raises(StackOverflowError):
            cpu.run(verbose=False)

    def test_stack_underflow_on_iret(self):
        """IRET raises StackUnderflowError on empty stack."""
        cpu = CPU()
        cpu.load_program(["IRET"])
        import pytest
        with pytest.raises(StackUnderflowError):
            cpu.run(verbose=False)

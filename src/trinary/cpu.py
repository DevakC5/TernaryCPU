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
    MUL   dst src     - dst = dst * src
    DIV   dst src     - dst = dst / src
    AND   dst src     - dst = dst AND src
    OR    dst src     - dst = dst OR src
    NOT   dst         - dst = NOT dst
    CMP   dst src     - Compare dst and src (sets internal flags)
    JMP   addr        - Jump to address
    JZ    addr        - Jump if zero/equal
    JNZ   addr        - Jump if not zero
    PUSH  src         - Push register to stack
    POP   dst         - Pop from stack to register
    CALL  addr        - Call subroutine (push PC, jump)
    RET               - Return from subroutine (pop PC)
    INT   n           - Software interrupt (push PC, jump to IVT[n])
    IRET              - Return from interrupt (pop PC, enable interrupts)
    EI                - Enable interrupts
    DI                - Disable interrupts
    SETIVT n addr     - Set IVT entry n to handler address
    SETTIMER period   - Set timer period in cycles (0 = disable)

Tensor Accelerator Coprocessor (isa: src/trinary/accelerator/):
    TLOADW addr rows cols - Load CPU memory into accelerator tensor, TID -> R0
    TSTOREW tid addr      - Store accelerator tensor to CPU memory
    TVECADD dst src_a src_b - Vector add on accelerator, result TID -> R0
    TMATMUL dst src_a src_b - Matrix multiply on accelerator, result TID -> R0
    TDOT src_a src_b       - Dot product on accelerator, scalar -> R0
    TACT tid type          - Apply activation (0=step) on accelerator in-place

Interrupts: IVT has 8 entries (0-7). Timer fires interrupt 0.
Stack: Grows downward from STACK_BASE (default 255)
Registers: R0, R1, R2, R3, SP (stack pointer)
"""

from trinary.registers import RegisterFile
from trinary.alu import alu
from trinary.memory import Memory
from trinary.accelerator import TernaryTensorAccelerator
from trinary.hardware import (
    Clock, Pipeline, HazardUnit, Cache, BranchPredictor,
    Bus, DMA, InterruptController, Profiler,
    get_latency, is_branch,
)


class StackOverflowError(Exception):
    """Stack overflow."""

class StackUnderflowError(Exception):
    """Stack underflow."""


class CPU:
    """Ternary CPU with fetch-decode-execute cycle and stack."""

    OPCODES = {
        "LOAD", "MOV", "CLR",
        "ADD", "SUB", "MUL", "DIV", "AND", "OR", "NOT",
        "CMP", "JMP", "JZ", "JNZ",
        "PUSH", "POP", "CALL", "RET", "HALT",
        "STOREM", "LOADM",
        "INT", "IRET", "EI", "DI", "SETIVT", "SETTIMER",
        "TLOADW", "TSTOREW", "TVECADD", "TMATMUL", "TDOT", "TACT",
    }

    CYCLES = {
        "LOAD": 1, "MOV": 1, "CLR": 1,
        "ADD": 1, "SUB": 1, "MUL": 3, "DIV": 5,
        "AND": 1, "OR": 1, "NOT": 1,
        "CMP": 1,
        "JMP": 1, "JZ": 1, "JNZ": 1,
        "PUSH": 2, "POP": 2,
        "CALL": 3, "RET": 3,
        "HALT": 1,
        "STOREM": 2, "LOADM": 2,
        "INT": 3, "IRET": 3,
        "EI": 1, "DI": 1,
        "SETIVT": 2, "SETTIMER": 1,
        "TLOADW": 10, "TSTOREW": 10, "TVECADD": 4, "TMATMUL": 20, "TDOT": 6, "TACT": 3,
    }

    STACK_BASE = 255
    STACK_MIN = 128
    IVT_SIZE = 8

    def __init__(self, memory=None, realistic_timing=False):
        self.registers = RegisterFile()
        self.memory = memory if memory else Memory(512)
        self.sp = self.STACK_BASE  # Stack pointer for PUSH/POP
        self.pc = 0
        self.call_stack = []  # Separate stack for CALL/RET addresses
        self.flags = {
            "ZERO": False,
            "EQUAL": False,
            "GREATER": False,
            "LESS": False,
        }
        self.program = []
        self.halted = False
        self.cycles = 0
        self.ivt = [0] * self.IVT_SIZE  # Interrupt Vector Table
        self.iflag = False  # Interrupt enable flag
        self.timer_period = 0  # Timer period in cycles (0 = disabled)
        self.timer_counter = 0  # Timer countdown
        self.pending_interrupt = None  # Interrupt number pending, or None
        self.accel = TernaryTensorAccelerator()
        self.realistic_timing = realistic_timing
        if realistic_timing:
            self._init_hardware()

    def _init_hardware(self):
        self.clock = Clock()
        self.pipeline = Pipeline()
        self.hazard = HazardUnit()
        self.icache = Cache(name="L1I", size_bytes=256, line_size=8)
        self.dcache = Cache(name="L1D", size_bytes=256, line_size=8)
        self.bp = BranchPredictor(mode='two_bit')
        self.bus = Bus()
        self.dma = DMA(bus=self.bus)
        self.intc = InterruptController()
        self.profiler = Profiler()

    def reset(self):
        """Reset CPU state."""
        self.registers = RegisterFile()
        self.sp = self.STACK_BASE
        self.call_stack = []
        self.pc = 0
        self.flags = {"ZERO": False, "EQUAL": False, "GREATER": False, "LESS": False}
        self.halted = False
        self.cycles = 0
        self.ivt = [0] * self.IVT_SIZE
        self.iflag = False
        self.timer_period = 0
        self.timer_counter = 0
        self.pending_interrupt = None
        self.accel = TernaryTensorAccelerator()
        if hasattr(self, 'realistic_timing') and self.realistic_timing:
            self._init_hardware()

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

        elif opcode == "MUL":
            dst, src = operands
            a = self.registers.store(dst)
            b = self.registers.store(src)
            result, _ = alu("MUL", a, b)
            self.registers.load(dst, result)

        elif opcode == "DIV":
            dst, src = operands
            a = self.registers.store(dst)
            b = self.registers.store(src)
            result, _ = alu("DIV", a, b)
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
            self.flags["ZERO"] = (result == "EQ")

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

        elif opcode == "PUSH":
            src = operands[0]
            value = self.registers.store(src)
            if self.sp < self.STACK_MIN:
                raise StackOverflowError("Stack overflow")
            self.memory.store(self.sp, value)
            self.sp -= 1

        elif opcode == "POP":
            dst = operands[0]
            if self.sp >= self.STACK_BASE:
                raise StackUnderflowError("Stack underflow")
            self.sp += 1
            value = self.memory.load(self.sp)
            self.registers.load(dst, value)

        elif opcode == "CALL":
            return_addr = self.pc + 1
            self.call_stack.append(return_addr)
            addr = int(operands[0])
            self.pc = addr
            return

        elif opcode == "RET":
            if not self.call_stack:
                raise StackUnderflowError("Stack underflow")
            return_addr = self.call_stack.pop()
            self.pc = return_addr
            return

        elif opcode == "HALT":
            self.halted = True
            return

        elif opcode == "STOREM":
            addr_op, src = operands
            if addr_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                addr = t2d(self.registers.store(addr_op))
            else:
                addr = int(addr_op)
            value = self.registers.store(src)
            self.memory.store(addr, value)

        elif opcode == "LOADM":
            addr_op, dst = operands
            if addr_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                addr = t2d(self.registers.store(addr_op))
            else:
                addr = int(addr_op)
            value = self.memory.load(addr)
            self.registers.load(dst, value)

        elif opcode == "INT":
            int_num = int(operands[0])
            if int_num < 0 or int_num >= len(self.ivt):
                raise ValueError(f"Invalid interrupt number: {int_num}")
            return_addr = self.pc + 1
            if self.sp < self.STACK_MIN:
                raise StackOverflowError("Stack overflow")
            from trinary.conversion import decimal_to_ternary as d2t
            self.memory.store(self.sp, d2t(return_addr))
            self.sp -= 1
            self.iflag = False
            self.pc = self.ivt[int_num]
            return

        elif opcode == "IRET":
            if self.sp >= self.STACK_BASE:
                raise StackUnderflowError("Stack underflow")
            self.sp += 1
            from trinary.conversion import ternary_to_decimal as t2d
            return_addr = t2d(self.memory.load(self.sp))
            self.pc = return_addr
            self.iflag = True
            return

        elif opcode == "EI":
            self.iflag = True

        elif opcode == "DI":
            self.iflag = False

        elif opcode == "SETIVT":
            int_op, addr_op = operands
            if int_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                int_num = int(t2d(self.registers.store(int_op)))
            else:
                int_num = int(int_op)
            if addr_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                addr = int(t2d(self.registers.store(addr_op)))
            else:
                addr = int(addr_op)
            if 0 <= int_num < len(self.ivt):
                self.ivt[int_num] = addr

        elif opcode == "SETTIMER":
            op = operands[0]
            if op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                period = int(t2d(self.registers.store(op)))
            else:
                period = int(op)
            self.timer_period = period
            self.timer_counter = period

        elif opcode == "TLOADW":
            addr_op, rows_op, cols_op = operands
            if addr_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                addr = int(t2d(self.registers.store(addr_op)))
            else:
                addr = int(addr_op)
            if rows_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                rows = int(t2d(self.registers.store(rows_op)))
            else:
                rows = int(rows_op)
            if cols_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                cols = int(t2d(self.registers.store(cols_op)))
            else:
                cols = int(cols_op)
            data = []
            for i in range(rows * cols):
                val = self.memory.load(addr + i).lstrip("-")
                data.append(int(val) if val.isdigit() else 1)
            tid = self.accel.memory.allocate(data, shape=(rows, cols))
            from trinary.conversion import decimal_to_ternary as d2t
            self.registers.load("R0", d2t(tid))

        elif opcode == "TSTOREW":
            tid_op, addr_op = operands
            if tid_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                tid = int(t2d(self.registers.store(tid_op)))
            else:
                tid = int(tid_op)
            if addr_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                addr = int(t2d(self.registers.store(addr_op)))
            else:
                addr = int(addr_op)
            data = self.accel.memory.load_list(tid)
            for i, v in enumerate(data):
                self.memory.store(addr + i, str(v))

        elif opcode == "TVECADD":
            dst_op, src_a_op, src_b_op = operands
            if dst_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                dst = int(t2d(self.registers.store(dst_op)))
            else:
                dst = int(dst_op)
            if src_a_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                src_a = int(t2d(self.registers.store(src_a_op)))
            else:
                src_a = int(src_a_op)
            if src_b_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                src_b = int(t2d(self.registers.store(src_b_op)))
            else:
                src_b = int(src_b_op)
            a = self.accel.memory.load_list(src_a)
            b = self.accel.memory.load_list(src_b)
            from trinary.accelerator import TritSIMD
            result = TritSIMD.add_vectors(a, b)
            tid = self.accel.memory.allocate(result)
            from trinary.conversion import decimal_to_ternary as d2t
            self.registers.load("R0", d2t(tid))

        elif opcode == "TMATMUL":
            dst_op, src_a_op, src_b_op = operands
            if dst_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                dst = int(t2d(self.registers.store(dst_op)))
            else:
                dst = int(dst_op)
            if src_a_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                src_a = int(t2d(self.registers.store(src_a_op)))
            else:
                src_a = int(src_a_op)
            if src_b_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                src_b = int(t2d(self.registers.store(src_b_op)))
            else:
                src_b = int(src_b_op)
            result = self.accel.core.matmul(
                self.accel.memory.load_2d(src_a),
                self.accel.memory.load_2d(src_b),
            )
            flat = [v for row in result for v in row]
            tid = self.accel.memory.allocate(flat,
                shape=(len(result), len(result[0]) if result else 0))
            from trinary.conversion import decimal_to_ternary as d2t
            self.registers.load("R0", d2t(tid))

        elif opcode == "TDOT":
            src_a_op, src_b_op = operands
            if src_a_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                src_a = int(t2d(self.registers.store(src_a_op)))
            else:
                src_a = int(src_a_op)
            if src_b_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                src_b = int(t2d(self.registers.store(src_b_op)))
            else:
                src_b = int(src_b_op)
            a = self.accel.memory.load_list(src_a)
            b = self.accel.memory.load_list(src_b)
            from trinary.accelerator import TritSIMD
            result = TritSIMD.dot_product(a, b)
            from trinary.conversion import decimal_to_ternary as d2t
            self.registers.load("R0", d2t(result))

        elif opcode == "TACT":
            tid_op, type_op = operands
            if tid_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                tid = int(t2d(self.registers.store(tid_op)))
            else:
                tid = int(tid_op)
            if type_op in self.registers.REGISTER_NAMES:
                from trinary.conversion import ternary_to_decimal as t2d
                act_type = int(t2d(self.registers.store(type_op)))
            else:
                act_type = int(type_op)
            data = self.accel.memory.load_list(tid)
            from trinary.accelerator import TritSIMD
            if act_type == 0:
                result = TritSIMD.ternary_threshold(data)
            else:
                result = data[:]
            self.accel.memory.store(tid, result)

        self.pc += 1

    def step(self):
        """Execute one instruction (fetch-decode-execute).

        After execution, checks for timer expiry and pending hardware interrupts.

        Returns:
            int: Total cycle cost (instruction + optional interrupt context switch).
        """
        if self.realistic_timing:
            return self._step_realistic()
        return self._step_fast()

    def _step_fast(self):
        """Fast (non-pipelined) step — original behavior, no pipeline overhead."""
        if self.pc >= len(self.program):
            self.halted = True
            return 0

        instruction = self.program[self.pc]
        opcode = instruction.strip().split()[0].upper() if instruction.strip() else ""
        self.execute_instruction(instruction)
        cost = self.CYCLES.get(opcode, 1)
        self.cycles += cost

        if self.timer_period > 0:
            self.timer_counter -= cost
            if self.timer_counter <= 0:
                self.timer_counter = self.timer_period
                self.pending_interrupt = 0

        if self.pending_interrupt is not None and self.iflag:
            int_num = self.pending_interrupt
            self.pending_interrupt = None
            if int_num < len(self.ivt):
                handler_addr = self.ivt[int_num]
                if handler_addr is not None and handler_addr >= 0:
                    return_addr = self.pc
                    if self.sp < self.STACK_MIN:
                        raise StackOverflowError("Stack overflow")
                    from trinary.conversion import decimal_to_ternary as d2t
                    self.memory.store(self.sp, d2t(return_addr))
                    self.sp -= 1
                    self.iflag = False
                    self.pc = handler_addr
                    self.halted = False
                    ictx_cost = 2
                    self.cycles += ictx_cost
                    cost += ictx_cost

        return cost

    def _step_realistic(self):
        """Cycle-accurate step with pipeline timing.

        Executes one instruction per call with proper cycle timing.
        Pipeline stages are simulated for visualization.
        DMA runs concurrently on every cycle.

        Returns:
            int: Cycles consumed by this step.
        """
        self.clock.tick()
        self.profiler.record_cycle()
        self.dma.tick(memory=self.memory)
        self.pipeline.advance()

        cost = 1

        if not self.halted and self.pc < len(self.program):
            instr_str = self.program[self.pc]
            parts = instr_str.strip().split()
            opcode = parts[0].upper() if parts else ""
            operands = parts[1:] if len(parts) > 1 else []
            lat = get_latency(opcode)

            self.pipeline.fetch(instr_str, opcode, operands, cycles=lat)

            if is_branch(opcode):
                cost += self._execute_branch(instr_str, opcode, operands)
            else:
                self.execute_instruction(instr_str)

            self.profiler.record_instruction()

        if self.timer_period > 0:
            self.timer_counter -= cost
            if self.timer_counter <= 0:
                self.timer_counter = self.timer_period
                self.intc.request(0)

        irq = self.intc.acknowledge()
        if irq is not None and irq < len(self.ivt):
            self.pipeline.flush()
            self.pc = self.ivt[irq]
            self.halted = False
            cost += 2

        self.cycles += cost
        self.profiler.cycles = self.clock.cycle
        return cost

    def _execute_branch(self, instr_str, opcode, operands):
        """Execute a branch instruction with prediction tracking."""
        if opcode == "JMP":
            self.pipeline.flush()
            self.profiler.record_stall('control')
            self.execute_instruction(instr_str)
            self.bp.update(self.pc, True)
            return 2

        if opcode in ("JZ", "JNZ"):
            should = (opcode == "JZ" and self.flags.get("ZERO", False)) or \
                     (opcode == "JNZ" and not self.flags.get("ZERO", False))
            predicted = self.bp.predict(self.pc)
            self.execute_instruction(instr_str)
            if predicted != should:
                self.bp.record_mispredict()
                self.profiler.record_branch(correct=False)
                self.pipeline.flush()
                self.profiler.record_stall('control')
                self.bp.update(self.pc, should)
                return 2
            self.profiler.record_branch(correct=True)
            self.bp.update(self.pc, should)
            return 1

        if opcode == "CALL":
            self.execute_instruction(instr_str)
            self.bp.update(self.pc, True)
            return 1

        return 1

    def run(self, verbose=True):
        """Run the entire program.

        Args:
            verbose (bool): Print each step

        Returns:
            dict: Final register state
        """
        step_num = 0
        total_cycles = 0
        while not self.halted and self.pc < len(self.program):
            step_num += 1
            instruction = self.program[self.pc]
            old_pc = self.pc
            old_sp = self.sp
            old_regs = self.registers.dump()
            cost = self.step()
            total_cycles += cost
            new_regs = self.registers.dump()
            sp_change = f" SP:{old_sp}->{self.sp}" if old_sp != self.sp else ""
            if verbose:
                print(f"[{step_num:3}] PC:{old_pc:2}->{self.pc:2} | {instruction:20} "
                      f"| {new_regs}{sp_change} | ~{cost}cy")

        if verbose:
            ipc = step_num / total_cycles if total_cycles else 0
            print(f"\n--- HALTED at PC={self.pc} ---")
            print(f"Registers: {self.registers.dump()}")
            print(f"Stack Pointer: SP={self.sp}")
            print(f"Call Stack: {self.call_stack}")
            print(f"Flags: {self.flags}")
            print(f"Cycles: {total_cycles} | Instructions: {step_num} | IPC: {ipc:.3f}")

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


def demo_stack():
    """Demo stack operations."""
    cpu = CPU()

    program = [
        "LOAD R0 10",
        "LOAD R1 12",
        "LOAD R2 20",
        "PUSH R0",
        "PUSH R1",
        "PUSH R2",
        "POP R3",
        "POP R2",
        "POP R1",
    ]

    print("\n--- PUSH/POP Demo ---")
    cpu.load_program(program)
    cpu.run()


def demo_subroutine():
    """Demo CALL/RET subroutines."""
    cpu = CPU()

    program = [
        "LOAD R0 10",
        "LOAD R1 12",
        "CALL 5",
        "ADD R0 R1",
        "HALT",
        # Subroutine at address 5:
        "ADD R0 R1",
        "MOV R2 R0",
        "RET",
    ]

    print("\n--- CALL/RET Demo ---")
    cpu.load_program(program)
    cpu.run()


if __name__ == "__main__":
    demo()
    demo_sub()
    demo_stack()
    demo_subroutine()
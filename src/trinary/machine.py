"""
Ternary Machine Code Encoder/Decoder.

Converts between assembly mnemonics and ternary machine code.

Instruction Format (ternary string):
    [OPCODE (1 trit)] [DST (1 trit)] [SRC/VALUE (variable)]

Opcodes (ternary):
    000 = LOAD   - Load immediate
    001 = MOV    - Move register
    002 = CLR    - Clear register
    010 = ADD    - Add
    011 = SUB    - Subtract
    012 = AND    - Logical AND
    020 = OR     - Logical OR
    021 = NOT    - Logical NOT
    022 = CMP    - Compare
    100 = JMP    - Unconditional jump
    101 = JZ     - Jump if zero
    102 = JNZ    - Jump if not zero
    110 = PUSH   - Push to stack
    111 = POP    - Pop from stack
    112 = CALL   - Call subroutine
    120 = RET    - Return
    121 = HALT   - Halt

Register encoding (trit):
    0 = R0
    1 = R1
    2 = R2
    3 = R3
"""

from trinary.assembler import Assembler


OPCODE_MAP = {
    "LOAD": "000",
    "MOV": "001",
    "CLR": "002",
    "ADD": "010",
    "SUB": "011",
    "AND": "012",
    "OR": "020",
    "NOT": "021",
    "CMP": "022",
    "JMP": "100",
    "JZ": "101",
    "JNZ": "102",
    "PUSH": "110",
    "POP": "111",
    "CALL": "112",
    "RET": "120",
    "HALT": "121",
    "MUL": "122",
    "DIV": "200",
    "STOREM": "201",
    "LOADM": "202",
}

OPCODE_REVERSE = {v: k for k, v in OPCODE_MAP.items()}

REGISTER_MAP = {
    "R0": "0",
    "R1": "1",
    "R2": "2",
    "R3": "3",
}

REGISTER_REVERSE = {v: k for k, v in REGISTER_MAP.items()}


def encode_register(reg):
    """Encode register to trit."""
    if reg in REGISTER_MAP:
        return REGISTER_MAP[reg]
    return reg


def decode_register(trit):
    """Decode trit to register."""
    if trit in REGISTER_REVERSE:
        return REGISTER_REVERSE[trit]
    return trit


def encode_immediate(value):
    """Encode immediate value (ternary string) to ternary string."""
    return value


def encode_address(addr):
    """Encode address (decimal string/int) to ternary."""
    from trinary.conversion import decimal_to_ternary
    if isinstance(addr, str):
        if addr.isdigit():
            addr = int(addr)
    return decimal_to_ternary(int(addr))


def encode_instruction(instr, labels=None):
    """Encode one instruction to ternary machine code.

    Args:
        instr (str): e.g., "LOAD R0 10" or "CALL 4"
        labels (dict): label->address mapping

    Returns:
        str: ternary machine code
    """
    if labels is None:
        labels = {}

    parts = instr.strip().split()
    opcode = parts[0]
    operands = parts[1:] if len(parts) > 1 else []

    op_code = OPCODE_MAP.get(opcode)
    if not op_code:
        raise ValueError(f"Unknown opcode: {opcode}")

    if opcode in ("RET", "HALT", "NOT"):
        return op_code

    if opcode in ("STOREM", "LOADM"):
        reg = encode_register(operands[1])
        addr = operands[0]
        if addr.isdigit():
            addr_ternary = encode_address(addr)
        else:
            from trinary.conversion import decimal_to_ternary
            addr_ternary = decimal_to_ternary(int(addr))
        return op_code + reg + addr_ternary

    if opcode in ("JMP", "JZ", "JNZ", "CALL"):
        addr = operands[0]
        if addr in labels:
            addr = str(labels[addr])
        addr_ternary = encode_address(addr)
        return op_code + addr_ternary

    if len(operands) == 1:
        if opcode == "CLR":
            dst = encode_register(operands[0])
            return op_code + dst
        if opcode == "NOT":
            dst = encode_register(operands[0])
            return op_code + dst
        if opcode == "PUSH":
            src = encode_register(operands[0])
            return op_code + src
        if opcode == "POP":
            dst = encode_register(operands[0])
            return op_code + dst

    if len(operands) == 2:
        dst = encode_register(operands[0])
        src = operands[1]

        if opcode == "LOAD":
            src_ternary = encode_immediate(src)
            return op_code + dst + src_ternary

        src_encoded = encode_register(src)
        return op_code + dst + src_encoded

    return op_code


def decode_instruction(machine_code):
    """Decode ternary machine code to assembly.

    Args:
        machine_code (str): ternary string

    Returns:
        str: assembly instruction
    """
    if len(machine_code) < 3:
        return f"INVALID: {machine_code}"

    opcode_trits = machine_code[:3]
    rest = machine_code[3:]

    opcode = OPCODE_REVERSE.get(opcode_trits, opcode_trits)

    if opcode in ("RET", "HALT"):
        return opcode

    if opcode in ("JMP", "JZ", "JNZ", "CALL"):
        if rest:
            from trinary.conversion import ternary_to_decimal
            addr = ternary_to_decimal(rest)
            return f"{opcode} {addr}"
        return f"{opcode} ?"

    if opcode == "NOT":
        dst = decode_register(rest[0]) if rest else "?"
        return f"{opcode} {dst}"

    if opcode in ("PUSH", "POP"):
        src = decode_register(rest[0]) if rest else "?"
        return f"{opcode} {src}"

    if opcode == "STOREM":
        if rest:
            reg = decode_register(rest[0])
            addr_trits = rest[1:]
            if addr_trits:
                from trinary.conversion import ternary_to_decimal
                addr = ternary_to_decimal(addr_trits)
                return f"{opcode} {addr} {reg}"
            return f"{opcode} {reg} ?"
        return f"{opcode} ?"

    if opcode == "LOADM":
        if rest:
            reg = decode_register(rest[0])
            addr_trits = rest[1:]
            if addr_trits:
                from trinary.conversion import ternary_to_decimal
                addr = ternary_to_decimal(addr_trits)
                return f"{opcode} {addr} {reg}"
            return f"{opcode} {reg} ?"
        return f"{opcode} ?"

    if opcode == "CLR":
        dst = decode_register(rest[0]) if rest else "?"
        return f"{opcode} {dst}"

    if len(rest) >= 2:
        dst = decode_register(rest[0])
        src = rest[1]

        if opcode == "LOAD":
            src_value = rest[1:]
            return f"{opcode} {dst} {src_value}"

        src_reg = decode_register(src)
        return f"{opcode} {dst} {src_reg}"

    return f"{opcode} ?"


class Machine:
    """Ternary machine - assembler + encoder."""

    def __init__(self):
        self.assembler = Assembler()

    def assemble(self, source):
        """Assemble source to machine code.

        Args:
            source (str): assembly source

        Returns:
            list: list of ternary machine code strings
        """
        program, labels = self.assembler.assemble(source)
        machine_code = []
        for instr in program:
            code = encode_instruction(instr, labels)
            machine_code.append(code)
        return machine_code, program, labels

    def disassemble(self, machine_code_list):
        """Disassemble machine code to assembly.

        Args:
            machine_code_list (list): list of ternary strings

        Returns:
            list: list of assembly instructions
        """
        return [decode_instruction(code) for code in machine_code_list]


def demo():
    """Demo machine code encoding."""
    m = Machine()

    source = """
start:
    LOAD R0 10
    LOAD R1 12
    CALL add_func
    HALT

add_func:
    ADD R0 R1
    RET
"""

    print("=" * 60)
    print("TERNARY MACHINE CODE ENCODER")
    print("=" * 60)

    print("\n--- Source Assembly ---")
    print(source)

    machine_code, program, labels = m.assemble(source)

    print("--- Labels ---")
    for label, addr in sorted(labels.items()):
        print(f"  {label}: {addr}")

    print("\n--- Assembly -> Machine Code ---")
    print(f"{'Addr':>4} | {'Assembly':<20} | {'Machine Code'}")
    print("-" * 50)
    for i, (mc, asm) in enumerate(zip(machine_code, program)):
        print(f"{i:>4} | {asm:<20} | {mc}")

    print("\n--- Disassembly (verify) ---")
    dis = m.disassemble(machine_code)
    for i, (d, mc) in enumerate(zip(dis, machine_code)):
        print(f"{i:>4}: {mc} -> {d}")


def demo_opcodes():
    """Show all opcode encodings."""
    print("\n" + "=" * 60)
    print("OPCODE ENCODING TABLE")
    print("=" * 60)
    print(f"{'Mnemonic':<8} | {'Ternary'}")
    print("-" * 20)
    for mnemonic, ternary in sorted(OPCODE_MAP.items()):
        print(f"{mnemonic:<8} | {ternary}")


if __name__ == "__main__":
    demo()
    demo_opcodes()
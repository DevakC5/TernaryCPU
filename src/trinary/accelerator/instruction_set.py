"""Instruction set definition for the Ternary Tensor Accelerator.

Defines opcode constants and the Instruction data class.
"""

from enum import IntEnum


class Opcode(IntEnum):
    TVECADD = 0
    TVECSUB = 1
    TVECMUL = 2
    TDOT = 3
    TMATMUL = 4
    TACT = 5
    TLOAD = 6
    TSTORE = 7
    TFUSED = 8
    TCONV = 9


TVECADD = Opcode.TVECADD
TVECSUB = Opcode.TVECSUB
TVECMUL = Opcode.TVECMUL
TDOT = Opcode.TDOT
TMATMUL = Opcode.TMATMUL
TACT = Opcode.TACT
TLOAD = Opcode.TLOAD
TSTORE = Opcode.TSTORE
TFUSED = Opcode.TFUSED
TCONV = Opcode.TCONV


class Instruction:
    """A single accelerator instruction.

    Args:
        opcode: An Opcode value.
        dest: Destination tensor ID or register index (optional).
        src_a: Source A tensor ID or register index (optional).
        src_b: Source B tensor ID or register index (optional).
        extra: Extra parameter (activation type, scale, etc.).
    """

    def __init__(self, opcode, dest=None, src_a=None, src_b=None, extra=None):
        self.opcode = opcode if isinstance(opcode, Opcode) else Opcode(opcode)
        self.dest = dest
        self.src_a = src_a
        self.src_b = src_b
        self.extra = extra

    def __repr__(self):
        parts = [f"{self.opcode.name}"]
        if self.dest is not None:
            parts.append(f"dst={self.dest}")
        if self.src_a is not None:
            parts.append(f"a={self.src_a}")
        if self.src_b is not None:
            parts.append(f"b={self.src_b}")
        if self.extra is not None:
            parts.append(f"extra={self.extra}")
        return f"Instruction({' '.join(parts)})"


OPCODE_NAMES = {op.value: op.name for op in Opcode}


INSTRUCTION_FORMATS = {
    Opcode.TVECADD: ("TVECADD dst src_a src_b", "Element-wise add"),
    Opcode.TVECSUB: ("TVECSUB dst src_a src_b", "Element-wise subtract"),
    Opcode.TVECMUL: ("TVECMUL dst src_a src_b", "Element-wise multiply"),
    Opcode.TDOT: ("TDOT dst src_a src_b", "Dot product, result stored as scalar trit"),
    Opcode.TMATMUL: ("TMATMUL dst src_a src_b", "Matrix multiply"),
    Opcode.TACT: ("TACT dst src [act]", "Activation (0=step, 1=relu)"),
    Opcode.TLOAD: ("TLOAD dst addr/length", "Load tensor from CPU memory"),
    Opcode.TSTORE: ("TSTORE src addr", "Store tensor to CPU memory"),
    Opcode.TFUSED: ("TFUSED dst weights bias [act]", "Fused linear+activation"),
    Opcode.TCONV: ("TCONV dst input kernel", "Convolution (experimental)"),
}

"""Timing — instruction latency tables and cycle cost calculators."""


INSTRUCTION_LATENCIES = {
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
    "TLOADW": 10, "TSTOREW": 10,
    "TVECADD": 4, "TMATMUL": 20,
    "TDOT": 6, "TACT": 3,
}

STAGE_LATENCIES = {
    "IF": 1,
    "ID": 1,
    "EX": 1,
    "MEM": 1,
    "WB": 1,
}


def get_latency(opcode):
    """Get the latency (cycle cost) for an opcode.

    Args:
        opcode: Instruction opcode string.

    Returns:
        int: Base latency in cycles.
    """
    return INSTRUCTION_LATENCIES.get(opcode, 1)


def is_branch(opcode):
    return opcode in ("JMP", "JZ", "JNZ", "CALL")


def is_load(opcode):
    return opcode in ("LOAD", "LOADM", "POP")


def is_store(opcode):
    return opcode in ("STOREM", "PUSH", "TSTOREW")


def is_tensor_op(opcode):
    return opcode in ("TLOADW", "TSTOREW", "TVECADD", "TMATMUL", "TDOT", "TACT")


def reads_registers(opcode):
    """Return list of register operands read (by position)."""
    reads = {
        "MOV": [1], "ADD": [1], "SUB": [1], "MUL": [1], "DIV": [1],
        "AND": [1], "OR": [1], "NOT": [0],
        "CMP": [0, 1],
        "PUSH": [0],
        "STOREM": [1], "LOADM": [0],
        "INT": [], "SETIVT": [0, 1], "SETTIMER": [0],
    }
    return reads.get(opcode, [])


def writes_registers(opcode):
    """Return list of register operands written (by position)."""
    writes = {
        "LOAD": [0], "MOV": [0],
        "ADD": [0], "SUB": [0], "MUL": [0], "DIV": [0],
        "AND": [0], "OR": [0], "NOT": [0],
        "CMP": [],
        "POP": [0],
        "LOADM": [1],
        "TLOADW": [], "TVECADD": [], "TMATMUL": [], "TDOT": [],
    }
    return writes.get(opcode, [])

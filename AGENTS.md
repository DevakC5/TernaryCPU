# AGENTS.md

## Project

Trinary — a ternary (base-3) computer simulation in pure Python. Covers conversion, logic gates, adders, ALU, register file, RAM, CPU (fetch-decode-execute), two-pass assembler, machine-code encoder/decoder, benchmarks, and ASCII architecture diagrams.

## Structure & Setup

```
src/trinary/           ← installable package (pip install -e .)
  __init__.py
  conversion.py        Trit class + binary/ternary/decimal converters
  logic.py             TNOT, TAND, TOR gates + truth table printer
  adder.py             Half/full/ripple-carry adder (native base-3)
  arithmetic.py        ADD, SUB, MUL, DIV via decimal round-trip
  alu.py               ALU: ADD, SUB, MUL, DIV, AND, OR, NOT, CMP
  registers.py         RegisterFile: LOAD, STORE, MOVE, CLEAR on R0–R3
  memory.py            256-address RAM with store/load/dump
  cpu.py               CPU: fetch-decode-execute, 19 opcodes, stack, flags, subroutines
  assembler.py         Two-pass assembler: labels → addresses, branch resolution
  machine.py           Machine-code encoder/decoder: assembly ↔ ternary opcode strings
  demo_programs.py     Countdown, Fibonacci, sum, calculator, subroutine, logic, stack, factorial demos
  benchmark.py         Instruction counts, digit density, carry propagation, memory benchmarks
  diagrams.py          ASCII art: CPU arch, memory layout, fetch-decode-execute, data flow
tests/
  test_conversion.py   pytest tests for converters
  test_arithmetic.py   pytest tests for arithmetic
  test_alu.py          pytest tests for ALU (incl. MUL/DIV)
  test_assembler.py    pytest tests for assembler (incl. inline comments)
  test_cpu.py          pytest tests for CPU (all 19 opcodes)
  legacy/              Old input()-based scripts (not collected by pytest)
docs/
ARCHITECTURE.md
pyproject.toml
```

## Commands

```sh
pip install -e .                  # one-time setup
python -m pytest tests/ -v        # run all tests
python -m trinary.cpu             # CPU fetch-decode-execute demos
python -m trinary.demo_programs   # all demo programs
python -m trinary.benchmark       # benchmark suite
python -m trinary.diagrams        # ASCII architecture diagrams
python -m trinary.logic           # ternary logic truth tables
python -m trinary.conversion      # interactive conversion CLI
```

No `__init__.py` in `src/` — the `pyproject.toml` `[tool.setuptools.packages.find]` handles it.

## Key facts

- **21 opcodes**: LOAD, MOV, CLR, ADD, SUB, MUL, DIV, AND, OR, NOT, CMP, JMP, JZ, JNZ, PUSH, POP, CALL, RET, HALT, STOREM, LOADM.
- **MUL/DIV** assigned to ternary opcodes `122` / `200`. All other opcodes use the original ARCHITECTURE.md encodings.
- **Negative numbers** use signed-magnitude with a leading `-` prefix (e.g., `"-10"` = −3 in decimal). All converters, arithmetic, ALU, and validation support it.
- **Inline comments** (`#`) are stripped by the assembler's `parse_line` — the old demos no longer break.
- **Two addition paths**: `adder.py` (native base-3 ripple-carry, only 0–2) vs `arithmetic.py` (decimal round-trip, handles negatives). The ALU's ADD now uses `arithmetic.add_ternary`.
- **ALU `CMP`** returns `"EQ"`/`"LT"`/`"GT"` strings; the CPU maps to boolean flags (ZERO, EQUAL, GREATER, LESS).
- **CPU executes assembly strings** — machine-code encoding in `machine.py` is a separate layer.
- **Stack** vs **call stack**: `sp` (PUSH/POP, memory-based, grows down 255→128) vs `call_stack` (CALL/RET, Python list).
- **CMP flag ZERO** is set when `a == b or a == "0"` — not strictly when result is zero.
- **No automated tests** before May 2026 — existing scripts used `input()`. Now pytest.

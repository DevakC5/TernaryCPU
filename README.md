# Trinary — Ternary Computer Simulation

A ternary (base-3) computer simulation in pure Python. Covers conversion, logic gates, adders, ALU, register file, RAM, CPU (fetch-decode-execute), two-pass assembler, machine-code encoder/decoder, benchmarks, and ASCII architecture diagrams.

No dependencies beyond the Python standard library.

## Structure

```
src/core/
  conversion.py    Trit class + binary/ternary/decimal converters
  logic.py         TNOT, TAND, TOR gates + truth table printer
  adder.py         Half/full/ripple-carry adder (native base-3)
  arithmetic.py    ADD, SUB, MUL, DIV via decimal round-trip
  alu.py           ALU: ADD, SUB, AND, OR, NOT, CMP
  registers.py     Register file (R0–R3): LOAD, STORE, MOVE, CLEAR
  memory.py        256-address RAM with store/load/dump
  cpu.py           CPU: fetch-decode-execute, 17 opcodes, stack, flags, subroutines
  assembler.py     Two-pass assembler: labels → addresses, branch resolution
  machine.py       Machine-code encoder/decoder: assembly ↔ ternary opcodes
  demo_programs.py Countdown, Fibonacci, sum, calculator, subroutine, logic, stack demos
  benchmark.py     Instruction counts, digit density, carry propagation, memory benchmarks
  diagrams.py      ASCII art: CPU arch, memory layout, fetch-decode-execute, data flow
tests/             Standalone scripts with input() — no test framework
docs/              devlog.md, TODO.md
ARCHITECTURE.md    Full CPU spec: registers, opcodes, memory layout, encoding
```

## Quick Start

```sh
python src/core/cpu.py               # Fetch-decode-execute walkthrough
python src/core/demo_programs.py      # All demo programs
python src/core/benchmark.py          # Benchmark suite
python src/core/diagrams.py           # ASCII architecture diagrams
python -m src.core.logic              # Ternary logic truth tables
python src/core/conversion.py         # Interactive conversion CLI
```

## Architecture

- **CPU**: 4 general-purpose registers (R0–R3), PC, SP, flags. 17 opcodes including arithmetic, logic, branching, stack, and subroutines.
- **ALU**: ADD (native base-3 ripple-carry), SUB/AND/OR/NOT/CMP via delegated modules.
- **Memory**: 256-word RAM, stack grows downward 255→128.
- **Assembler**: Two-pass with symbolic labels and branch resolution.
- **Machine Code**: Variable-length ternary opcode encoding (3+ trits per instruction).
- **Dual addition**: `adder.py` (native base-3) and `arithmetic.py` (decimal round-trip).

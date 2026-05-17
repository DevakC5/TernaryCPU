# Trinary — Ternary Computer Simulation

A ternary (base-3) computer simulation in pure Python with a PyQt6 desktop UI. Covers conversion, logic gates, adders, ALU, register file, RAM, CPU (fetch-decode-execute), two-pass assembler, machine-code encoder/decoder, benchmarks, ASCII architecture diagrams, and an interactive visual simulator.

## Structure

```
src/trinary/           ← installable package
  __init__.py
  conversion.py        Trit class + binary/ternary/decimal converters
  logic.py             TNOT, TAND, TOR gates + truth table printer
  adder.py             Half/full/ripple-carry adder (native base-3)
  arithmetic.py        ADD, SUB, MUL, DIV via decimal round-trip
  alu.py               ALU: ADD, SUB, MUL, DIV, AND, OR, NOT, CMP
  registers.py         Register file (R0–R3): LOAD, STORE, MOVE, CLEAR
  memory.py            256-address RAM with store/load/dump
  cpu.py               CPU: fetch-decode-execute, 19 opcodes, stack, flags, subroutines
  assembler.py         Two-pass assembler: labels → addresses, branch resolution
  machine.py           Machine-code encoder/decoder: assembly ↔ ternary opcodes
  demo_programs.py     Countdown, Fibonacci, sum, calculator, subroutine, logic, stack demos
  benchmark.py         Instruction counts, digit density, carry propagation, memory benchmarks
  diagrams.py          ASCII art: CPU arch, memory layout, fetch-decode-execute, data flow
  ui/                  PyQt6 desktop visual simulator
    main_window.py      Main window with split-panel layout
    assembler_editor.py Syntax-highlighted assembly editor
    controls.py         Run / Step / Reset / Assemble / demo selector
    register_view.py    Register + flag display with change highlighting
    memory_view.py      256-row address/value table with write tracking
    stack_view.py       Stack visualization with SP indicator
    execution_trace.py  Step-by-step instruction history
    machine_code_view.py Assembly ↔ ternary machine code side-by-side
    demos.py            10 one-click demo programs
    styles.py           Dark cyberpunk theme
    app.py              Application entry point
tests/
  test_conversion.py   pytest tests for converters
  test_arithmetic.py   pytest tests for arithmetic
  test_alu.py          pytest tests for ALU
  test_assembler.py    pytest tests for assembler (incl. inline comments)
  test_cpu.py          pytest tests for CPU (all 19 opcodes)
  legacy/              Original input()-based scripts (archived)
docs/
  ARCHITECTURE.md      Full CPU spec: registers, opcodes, memory layout, encoding
pyproject.toml         Build config + pytest config
```

## Quick Start

```sh
pip install -e .                    # one-time setup
python -m pytest tests/ -v          # run all 62 tests
python -m trinary.cpu               # CPU fetch-decode-execute walkthrough
python -m trinary.demo_programs     # All demo programs
python -m trinary.benchmark         # Benchmark suite
python -m trinary.diagrams          # ASCII architecture diagrams
python -m trinary.logic             # Ternary logic truth tables
python -m trinary.conversion        # Interactive conversion CLI
```

### PyQt6 Desktop UI

```sh
pip install pyqt6                   # install dependency
python -m trinary.ui.app            # launch visual simulator
```

The UI provides:
- **Assembly editor** with syntax highlighting (opcodes, registers, labels, comments)
- **Machine code viewer** — ternary encoding alongside assembly
- **Register display** — R0–R3, PC, SP, flags with change highlighting
- **Memory viewer** — 256-address grid with write tracking
- **Stack viewer** — live stack with SP direction indicator
- **Execution trace** — step-by-step history with current instruction highlight
- **Demo selector** — 10 one-click demo programs
- **Run / Step / Reset / Assemble** controls
- **Instruction banner** — current instruction displayed top-center
- **Dark cyberpunk theme**

## Features

- **19 opcodes**: LOAD, MOV, CLR, ADD, SUB, MUL, DIV, AND, OR, NOT, CMP, JMP, JZ, JNZ, PUSH, POP, CALL, RET, HALT
- **Negative numbers**: signed-magnitude with leading `-` prefix (e.g., `"-10"` = −3 decimal)
- **Two addition paths**: `adder.py` (native base-3 ripple-carry) vs `arithmetic.py` (decimal round-trip, handles negatives)
- **MUL/DIV**: opcodes `122` / `200`, integrated across ALU, CPU, assembler, encoder
- **Assembler**: two-pass with symbolic labels, `#` and `;` inline comments
- **Machine code**: variable-length ternary opcode strings with encode/decode
- **Stack**: memory-based PUSH/POP (grows down 255→128) + Python-list CALL/RET
- **Tests**: 62 pytest tests covering conversion, arithmetic, ALU, CPU, assembler

## Architecture

- **CPU**: 4 general-purpose registers (R0–R3), PC, SP, flags (ZERO/EQUAL/GREATER/LESS)
- **ALU**: arithmetic, logical, and comparison operations
- **Memory**: 256-word RAM
- **UI**: fully decoupled from back-end — uses public APIs only

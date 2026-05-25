# Trinary — Ternary (Base-3) Computer Simulation

A complete ternary (base-3) computer system simulated in pure Python. From fundamental logic gates up through an interactive OS shell and a PyQt6 desktop UI.

## Features

- **26 instructions**: LOAD, MOV, CLR, ADD, SUB, MUL, DIV, AND, OR, NOT, CMP, JMP, JZ, JNZ, PUSH, POP, CALL, RET, HALT, STOREM, LOADM, INT, IRET, EI, DI, SETIVT, SETTIMER
- **Signed-magnitude negatives**: leading `-` prefix (e.g., `"-10"` = −3 decimal)
- **Memory-mapped display**: RAM addresses 200–255 drive a 7×8 character display; register-based `STOREM`/`LOADM` access
- **Keyboard input**: memory address 260 acts as keyboard buffer
- **Hardware timer**: programmable periodic interrupt (interrupt 0)
- **Interrupt system**: 8-entry interrupt vector table, software/hardware interrupts
- **Two addition paths**: `adder.py` (native base-3 ripple-carry) vs `arithmetic.py` (decimal round-trip, handles negatives)
- **Two-pass assembler**: symbolic labels, `#` and `;` inline comments
- **Machine code encoder/decoder**: variable-length ternary opcode strings
- **Dual stacks**: memory-based PUSH/POP (grows down 255→128) + Python-list CALL/RET
- **Minimal OS shell**: keyboard echo, line editing, HELP/MEMDUMP/REGS/RUN/CLS commands
- **ASCII diagrams**: CPU architecture, memory layout, fetch-decode-execute cycle, data flow
- **PyQt6 desktop UI**: syntax-highlighted editor, machine code viewer, register/memory/stack displays, execution trace, pixel framebuffer display

## Quick Start

```sh
pip install -e .                  # one-time install
python -m pytest tests/ -v        # run all 113 tests
python -m trinary.os              # boot interactive OS shell (TTY)
python -m trinary.cpu             # CPU fetch-decode-execute walkthrough
python -m trinary.demo_programs   # all demo programs
python -m trinary.benchmark       # full benchmark suite
python -m trinary.diagrams        # ASCII architecture diagrams
python -m trinary.logic           # ternary logic truth tables
python -m trinary.conversion      # interactive conversion CLI
```

### PyQt6 Visual Simulator

```sh
pip install pyqt6                 # install dependency
python -m trinary.ui.app          # launch desktop UI
```

## Project Structure

```
src/trinary/             ← installable package (pip install -e .)
├── __init__.py
├── conversion.py        Trit class + binary/ternary/decimal converters
├── logic.py             TNOT, TAND, TOR gates + truth tables
├── adder.py             Half/full/ripple-carry adder (native base-3)
├── arithmetic.py        ADD, SUB, MUL, DIV via decimal round-trip
├── alu.py               ALU: all 8 operations (ADD, SUB, MUL, DIV, AND, OR, NOT, CMP)
├── registers.py         Register file (R0–R3): load/store/move/clear
├── memory.py            512-address RAM with store/load/dump
├── cpu.py               CPU: fetch-decode-execute, 26 opcodes, 2 stacks, flags, interrupts
├── assembler.py         Two-pass assembler: labels → addresses, branch resolution
├── machine.py           Machine-code encoder/decoder: assembly ↔ ternary opcodes
├── display.py           Memory-mapped display (200–255) + PixelDisplay (27×27)
├── os.py                Minimal OS shell: keyboard, display, commands
├── demo_programs.py     Countdown, Fibonacci, sum, calculator, subroutines, stack, logic, interrupt demos
├── benchmark.py         Instruction throughput, digit density, carry propagation, memory benchmarks
├── diagrams.py          ASCII art: CPU arch, memory layout, F-D-E cycle, data flow
└── ui/                  PyQt6 desktop visual simulator
    ├── app.py              Application entry point
    ├── main_window.py      Main window assembles all panels
    ├── assembler_editor.py Syntax-highlighted editor + breakpoints
    ├── controls.py         Run/Step/Reset/Assemble toolbar + demo selector
    ├── register_view.py    R0–R3, PC, SP, flags with flash animation
    ├── memory_view.py      512-row address/value table with access tracking
    ├── stack_view.py       Stack contents with SP indicator
    ├── execution_trace.py  Step-by-step instruction history
    ├── machine_code_view.py Assembly ↔ ternary machine code side-by-side
    ├── screen_view.py     27×27 pixel framebuffer widget
    ├── demos.py            13 demo program source strings
    └── styles.py           Dark cyberpunk QSS stylesheet
tests/
├── test_conversion.py   Trit class, base conversion functions
├── test_arithmetic.py   Add/sub/multiply/divide ternary functions
├── test_alu.py          ALU operations (incl. MUL/DIV)
├── test_assembler.py    Label resolution, inline comments
├── test_cpu.py          All 26 opcodes, flags, stack, interrupts
├── test_cpu_stress.py   Nested calls, long loops, heavy instruction counts
├── test_display.py      DisplayMemoryMap, PixelDisplay, STOREM/LOADM, keyboard
└── legacy/              Original input()-based scripts (archived)
docs/
├── ARCHITECTURE.md      Full CPU specification
├── instruction-set.md   Complete opcode reference
├── display-system.md    Display, keyboard, OS shell internals
├── ui-guide.md          PyQt6 visual simulator guide
├── developer-guide.md   Setup, testing, extending
├── tutorial.md          Step-by-step walkthrough
└── benchmarks.md        Benchmark results
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  ASSEMBLY SOURCE                     │
│  start: LOAD R0 10; CALL func; HALT                 │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                  ASSEMBLER (two-pass)                │
│  Pass 1: scan labels → addresses                   │
│  Pass 2: resolve branches, produce instruction list │
└─────────────────────────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
┌─────────────────────┐ ┌──────────────────────────┐
│  CPU (direct exec)  │ │  MACHINE CODE ENCODER     │
│  Parses assembly    │ │  Converts to ternary       │
│  strings at runtime │ │  opcode strings             │
└─────────────────────┘ └──────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────┐
│              FETCH-DECODE-EXECUTE CYCLE              │
│                                                     │
│  ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐     │
│  │FETCH  │→  │DECODE │→  │EXECUTE│→  │UPDATE │     │
│  │read   │   │parse  │   │ALU /  │   │PC += 1│     │
│  │prog[PC]│  │opcode  │   │memory │   │or jump│     │
│  └───────┘   └───────┘   └───────┘   └───────┘     │
└─────────────────────────────────────────────────────┘
```

## CPU Specifications

### Registers

| Register | Encoding | Purpose |
|----------|----------|---------|
| R0       | 0        | Primary accumulator |
| R1       | 1        | Secondary register |
| R2       | 2        | General purpose |
| R3       | 3        | General purpose (OS convention: always 0) |
| PC       | —        | Program counter |
| SP       | —        | Stack pointer (starts at 255, grows down) |
| Flags    | —        | ZERO, EQUAL, GREATER, LESS |

### Memory Map

| Address Range | Purpose |
|---------------|---------|
| 0–127         | General data / program |
| 128–199       | Stack (grows down from 255) |
| 200–255       | Video RAM (56 chars, 7 rows × 8 cols) |
| 260           | Keyboard buffer |
| 0–511         | Total addressable (default size) |

### Instruction Set Summary

| Category | Instructions |
|----------|-------------|
| Data Movement | LOAD, MOV, CLR |
| Arithmetic | ADD, SUB, MUL, DIV |
| Logical | AND, OR, NOT |
| Comparison | CMP |
| Control Flow | JMP, JZ, JNZ |
| Subroutines | CALL, RET |
| Stack | PUSH, POP |
| Memory | STOREM, LOADM |
| Interrupts | INT, IRET, EI, DI, SETIVT |
| Timer | SETTIMER |
| System | HALT |

See [docs/instruction-set.md](docs/instruction-set.md) for the complete reference.

## PyQt6 Desktop UI

The visual simulator provides a complete debugging environment:

![UI Layout](docs/ui-guide.md#layout)

- **Assembly editor** with syntax highlighting (opcodes=cyan, registers=yellow, labels=purple, comments=green, numbers=white) and clickable breakpoints in the gutter
- **Machine code viewer** — ternary opcode strings alongside assembly
- **Register panel** — R0–R3 values with flash animation on change, PC, SP, four flag indicators (active/inactive style)
- **Memory viewer** — 512-row table with green/blue backgrounds for write/read access tracking, current PC highlight
- **Stack viewer** — live stack contents with SP position marker and item count
- **Execution trace** — step-by-step history with columns: step#, PC, instruction, registers, flags
- **Pixel display** — 27×27 pixel framebuffer (black/gray/white), keyboard capture
- **Toolbar** — demo selector (13 programs) + Assemble / Run / Step Into / Step Over / Reset / Pause / Continue
- **Dark cyberpunk theme**

## OS Shell

The built-in minimal OS (`python -m trinary.os`) boots into an interactive command shell:

```
Trishell!> HELP
HELP - CLS MEMDUMP REGS RUN
> █
```

### Commands

| Command | Description |
|---------|-------------|
| `HELP` | Lists available commands |
| `CLS` | Clears the display |
| `REGS` | Shows register values |
| `MEMDUMP` | Dumps first 8 memory addresses |
| `RUN` | Prints "RUN!" (placeholder) |

### OS Internals

Written entirely in assembly (342 instructions), the OS implements:
- Memory-mapped keyboard polling (address 260)
- Input line buffer with backspace support (addresses 1–32)
- Cursor management with display scrolling
- Multi-character command parsing

## Development

```sh
git clone <repo>
cd trinary
pip install -e .
python -m pytest tests/ -v
```

### Adding a new instruction

1. Add opcode to `OPCODE_MAP` in `machine.py`
2. Add to `OPCODES` set in `cpu.py` (top-level constant)
3. Implement execution in `cpu.execute_instruction()`
4. Add cycle cost to `CYCLES` dict in `cpu.py`
5. Add tests in `tests/test_cpu.py`
6. Update assembler if new operand formats are needed

## Testing

```sh
python -m pytest tests/ -v              # all 113 tests
python -m pytest tests/test_cpu.py -v   # CPU-specific tests
python -m pytest tests/ -k "cmp" -v     # comparison-related tests
```

## License

MIT

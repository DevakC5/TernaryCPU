# Ternary CPU Architecture Specification

## Overview

The Trinary CPU is a balanced ternary computer simulation with 26 instructions, 4 general-purpose registers, 512-byte addressable memory, full interrupt support, and memory-mapped I/O.

---

## 1. Registers

### General Purpose (4)

| Register | Encoding | Convention |
|----------|----------|------------|
| R0       | 0        | Primary accumulator |
| R1       | 1        | Secondary register |
| R2       | 2        | General purpose |
| R3       | 3        | Always 0 (OS convention) |

### Special Purpose

| Register | Size | Description |
|----------|------|-------------|
| PC       | int  | Program counter — address of next instruction |
| SP       | int  | Stack pointer — starts at 255, grows down to 128 |
| call_stack | list | Python list for CALL/RET return addresses |
| flags    | dict | ZERO, EQUAL, GREATER, LESS (set by CMP) |

### Flag Semantics

| Flag | Set When | Notes |
|------|----------|-------|
| ZERO | CMP result is `"EQ"` | Also set by operations that produce "0" |
| EQUAL | CMP result is `"EQ"` | Synonymous with ZERO |
| GREATER | CMP result is `"GT"` | dst > src in CMP |
| LESS | CMP result is `"LT"` | dst < src in CMP |

---

## 2. Memory Model

### Memory Map (default: 512 addresses)

| Range | Size | Purpose |
|-------|------|---------|
| 0–127 | 128  | General data / program storage |
| 128–199 | 72 | Stack (grows down from 255) |
| 200–255 | 56  | Video RAM (7 rows × 8 cols) |
| 256–259 | 4   | Reserved |
| 260    | 1    | Keyboard buffer |
| 261–511 | 251 | Available |

### Memory Cell

Each cell holds a ternary string (variable length, e.g., `"0"`, `"102"`, `"-10"`). Values are stored as-is — no fixed-width encoding.

### Stack

```
Initial SP = 255

PUSH R0:  memory[SP] = R0; SP -= 1
POP R0:   SP += 1; R0 = memory[SP]

Stack overflow: SP < 128 → StackOverflowError
Stack underflow: SP >= 255 → StackUnderflowError (on POP)
```

The CALL/RET system uses a separate Python-list call stack — not memory.

---

## 3. Instruction Set

### Opcode Map

| Ternary | Decimal | Mnemonic | Format | Cycles | Description |
|---------|---------|----------|--------|--------|-------------|
| 000     | 0       | LOAD     | C      | 1      | Load immediate into register |
| 001     | 1       | MOV      | A      | 1      | Copy register to register |
| 002     | 2       | CLR      | B      | 1      | Set register to "0" |
| 010     | 3       | ADD      | A      | 1      | Add registers |
| 011     | 4       | SUB      | A      | 1      | Subtract registers |
| 012     | 5       | AND      | A      | 1      | Ternary AND (element-wise min) |
| 020     | 6       | OR       | A      | 1      | Ternary OR (element-wise max) |
| 021     | 7       | NOT      | B      | 1      | Ternary NOT (0↔2, 1→1) |
| 022     | 8       | CMP      | A      | 1      | Compare, set flags |
| 100     | 9       | JMP      | D      | 1      | Unconditional jump |
| 101     | 10      | JZ       | D      | 1      | Jump if ZERO or EQUAL flag |
| 102     | 11      | JNZ      | D      | 1      | Jump if NOT ZERO and NOT EQUAL |
| 110     | 12      | PUSH     | B      | 2      | Push register to stack |
| 111     | 13      | POP      | B      | 2      | Pop register from stack |
| 112     | 14      | CALL     | D      | 3      | Call subroutine |
| 120     | 15      | RET      | E      | 3      | Return from subroutine |
| 121     | 16      | HALT     | E      | 1      | Halt execution |
| 122     | 17      | MUL      | A      | 3      | Multiply registers |
| 200     | 18      | DIV      | A      | 5      | Divide registers |
| 201     | 19      | STOREM   | M      | 2      | Store register to memory address |
| 202     | 20      | LOADM    | M      | 2      | Load memory address into register |
| —       | —       | INT      | D      | 2      | Software interrupt |
| —       | —       | IRET     | E      | 2      | Return from interrupt |
| —       | —       | EI       | E      | 1      | Enable interrupts |
| —       | —       | DI       | E      | 1      | Disable interrupts |
| —       | —       | SETIVT   | S      | 1      | Set interrupt vector |
| —       | —       | SETTIMER | T      | 1      | Set timer period |

### Instruction Formats

| Format | Pattern | Example | Encoding |
|--------|---------|---------|----------|
| A (two-reg) | `OP R_dst R_src` | `ADD R0 R1` | op(3) + dst(1) + src(1) |
| B (one-reg) | `OP R_op` | `CLR R0` | op(3) + reg(1) |
| C (imm) | `OP R_dst value` | `LOAD R0 10` | op(3) + dst(1) + value(ternary) |
| D (branch) | `OP addr` | `JMP loop` | op(3) + addr(ternary) |
| E (no-op) | `OP` | `HALT` | op(3) |
| M (mem) | `OP addr R_reg` | `STOREM 33 R0` | op(3) + reg(1) + addr(ternary) |
| S (ivt) | `SETIVT int addr` | — | op(3) + int(ternary) + addr(ternary) |
| T (timer) | `SETTIMER period` | — | op(3) + period(ternary) |

### Assembly Syntax

```
label:
    OPCODE operand operand  # inline comment
    OPCODE operand          ; also a comment
```

Labels are identifiers followed by `:`. They can be used as branch targets and CALL addresses. Comments use `#` or `;`.

---

## 4. Display System

### Memory-Mapped Display

| Property | Value |
|----------|-------|
| Address range | 200–255 (56 bytes) |
| Display size | 7 rows × 8 columns = 56 characters |
| Encoding | Ternary ASCII code (e.g., `"10010"` for `'T'` = ASCII 84) |
| Null character | Ternary `"0"` renders as space |

Each VRAM cell stores the ternary representation of an ASCII code. The `DisplayMemoryMap` reads these, converts to integers, and produces `chr(code)`. Non-printable characters render as `.`.

### Pixel Display

| Property | Value |
|----------|-------|
| Resolution | 27 × 27 pixels |
| Colors | 0 = black, 1 = gray, 2 = white |
| Drawing | Bresenham line algorithm |

The `PixelDisplay` is a separate framebuffer (not memory-mapped) used by the UI for graphics demos.

### Keyboard

| Property | Value |
|----------|-------|
| Buffer address | 260 |
| Polling | CPU reads `LOADM 260 R1` |
| Value | Ternary ASCII code of most recent key |
| Acknowledge | Write `"0"` to 260 after reading |

The OS shell polls address 260 each cycle. When non-zero, it processes the key and writes `"0"` to acknowledge.

---

## 5. Interrupt System

### Interrupt Vector Table (IVT)

- 8 entries (indices 0–7)
- Each entry holds an instruction address
- `INT n` triggers vector `n`

### Timer

- `SETTIMER period` sets timer interval (in CPU cycles)
- Timer decrements each step by the cycle cost
- When timer_counter ≤ 0, interrupt 0 is pended
- Pending interrupt fires when `iflag` is True

### Interrupt Flow

```
Main program:                  Handler:
  ...                            STOREM 0 R0   (save state)
  EI      (enable interrupts)    ...            (work)
  ...                            LOADM 0 R0   (restore state)
  ← timer fires →               IRET          (return, re-enable)
  ...
```

### Instructions

| Instruction | Description |
|-------------|-------------|
| `EI` | Set interrupt flag (enable) |
| `DI` | Clear interrupt flag (disable) |
| `INT n` | Software interrupt: push PC to stack, jump to IVT[n], disable interrupts |
| `IRET` | Pop PC from stack, enable interrupts |
| `SETIVT n addr` | Set IVT entry n to address addr |
| `SETTIMER period` | Set timer period in cycles |

---

## 6. Execution Cycle

### Step-by-Step

```
1. FETCH:   instruction = program[pc]
2. DECODE:  opcode, operands = parse(instruction)
3. EXECUTE: perform opcode operation
4. UPDATE:  pc += 1 (unless branch/halt/interrupt)
5. TIMER:   timer_counter -= cycle_cost
6. INTERRUPT: if pending and iflag, push PC, jump to handler
```

### Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     CPU EXECUTION CYCLE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                │
│   │ FETCH  │ →  │ DECODE  │ →  │ EXECUTE │                │
│   └─────────┘    └─────────┘    └─────────┘                │
│        │              │              │                      │
│        ▼              ▼              ▼                      │
│   PC points to   Parse opcode   ALU / memory /             │
│   instruction    + operands     reg / control flow         │
│                                                             │
│        ────────────── UPDATE ───────────────               │
│        PC += 1 / jump, timer, interrupt check              │
└─────────────────────────────────────────────────────────────┘
```

### Execution Example

```
Program:
  0: LOAD R0 10
  1: LOAD R1 12
  2: ADD R0 R1
  3: HALT

Step  PC  Instruction      R0   R1   R2   Action
───── ─── ──────────────── ──── ──── ──── ───────────────────
  0    0  LOAD R0 10       10   0    0    R0 ← ternary("10")
  1    1  LOAD R1 12       10   12   0    R1 ← ternary("12")
  2    2  ADD R0 R1        22   12   0    ADD: 3+5=8 → "22"
  3    3  HALT             22   12   0    halted = True
```

---

## 7. Number Representation

### Representation

- Positive numbers: standard ternary (e.g., `"10"` = 3, `"22"` = 8)
- Negative numbers: signed-magnitude with leading `-` (e.g., `"-10"` = −3)
- Zero: `"0"`

### Conversion

```python
ternary_to_decimal("102")    → 11
ternary_to_decimal("-10")    → -3
decimal_to_ternary(11)       → "102"
decimal_to_ternary(-3)       → "-10"
```

### Digit Efficiency

Ternary is more digit-efficient than binary:
- Value 1000: binary = `1111101000` (10 digits), ternary = `1101001` (7 digits)
- Average savings: ~37% fewer digits

---

## 8. Addition Paths

### Native Ternary (adder.py)

- Works only with non-negative strings of '0','1','2'
- Full-adder chain: each position adds a+b+carry
- Returns (sum_string, final_carry)

### Decimal Round-Trip (arithmetic.py)

- Used by the CPU ALU
- Converts both operands to decimal, performs Python operation, converts back
- Handles negative numbers naturally
- Slower but correct for signed arithmetic

### When Each Is Used

| Context | Path |
|---------|------|
| ALU ADD/SUB/MUL/DIV | arithmetic.py (decimal round-trip) |
| Benchmarks / education | adder.py (native base-3) |
| CPU PUSH/POP | Memory (no arithmetic) |

---

## 9. Complete System Stack

```
┌────────────────────────────────────────────────────────────┐
│  APPLICATION                                              │
│  (OS Shell, Demo Programs, User Code)                     │
├────────────────────────────────────────────────────────────┤
│  ASSEMBLER                                                │
│  (two-pass: labels → addresses, branch resolution)        │
├────────────────────────────────────────────────────────────┤
│  MACHINE CODE ENCODER / DECODER                           │
│  (assembly ↔ ternary opcode strings)                      │
├────────────────────────────────────────────────────────────┤
│  CPU                                                      │
│  (fetch-decode-execute, 26 opcodes, 4 regs, 512B RAM)    │
├────────────────────────────────────────────────────────────┤
│  ALU                    │  REGISTERS  │  MEMORY           │
│  (ADD/SUB/MUL/DIV/      │  (R0–R3)    │  (512 addresses) │
│   AND/OR/NOT/CMP)       │             │                   │
├────────────────────────────────────────────────────────────┤
│  arithmetic.py  │  logic.py  │  conversion.py            │
│  (decimal       │  (ternary   │  (base conversion)       │
│   round-trip)   │   gates)    │                           │
└────────────────────────────────────────────────────────────┘
```

---

## 10. Module Dependencies

```
conversion.py      (foundation — no trinary deps)
    ↑
logic.py           (foundation — no trinary deps)
    ↑
adder.py           → logic.py
arithmetic.py      → conversion.py
    ↑
alu.py             → arithmetic.py, logic.py, conversion.py
registers.py       → conversion.py
memory.py          (standalone)
    ↑
cpu.py             → registers.py, alu.py, memory.py
assembler.py       → cpu.py (demo only)
machine.py         → assembler.py, conversion.py
display.py         → conversion.py (lazy)
os.py              → cpu.py, assembler.py, conversion.py, display.py
demo_programs.py   → cpu.py, assembler.py, display.py
benchmark.py       → cpu.py, assembler.py, adder.py, conversion.py
diagrams.py        (standalone)
```

---

## Revision History

- v2.0 (2026-05-18): Full rewrite
  - 26 opcodes (added MUL, DIV, STOREM, LOADM, INT, IRET, EI, DI, SETIVT, SETTIMER)
  - 512-byte memory
  - Memory-mapped display (200–255)
  - Keyboard buffer (260)
  - Hardware timer and interrupt system
  - Minimal OS shell
  - PyQt6 desktop UI

- v1.0 (2026-05-17): Initial specification
  - 4 general-purpose registers
  - 17 opcodes
  - 256-word memory
  - Two-pass assembler with labels
  - Variable-length ternary machine code

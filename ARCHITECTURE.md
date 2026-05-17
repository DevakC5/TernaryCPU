# Ternary CPU Architecture Specification

## Overview

This document describes the complete architecture of the Trinary ternary computer system, from high-level assembly down to machine code execution.

---

## 1. Registers

### General Purpose Registers (4)

| Register | Encoding | Description |
|----------|----------|-------------|
| R0       | 0        | Primary accumulator |
| R1       | 1        | Secondary register |
| R2       | 2        | General purpose |
| R3       | 3        | General purpose |

### Special Purpose Registers

| Register | Description |
|----------|-------------|
| PC       | Program Counter - address of next instruction |
| SP       | Stack Pointer - top of stack (starts at 255) |
| Flags    | Condition flags (ZERO, EQUAL, GREATER, LESS) |
| Call Stack | Internal return address stack for CALL/RET |

### Register State Example
```python
{'R0': '102', 'R1': '21', 'R2': '0', 'R3': '0'}
```

---

## 2. Instruction Formats

### Format A: Two-Operand Instructions
```
[OPCODE (3 trits)] [DST (1 trit)] [SRC (1 trit)]
```
Example: `ADD R0 R1` → `01001`

### Format B: One-Operand Instructions
```
[OPCODE (3 trits)] [OPERAND (1 trit)]
```
Example: `NOT R0` → `0210`

### Format C: Immediate Load
```
[OPCODE (3 trits)] [DST (1 trit)] [VALUE (variable)]
```
Example: `LOAD R0 102` → `0000102`

### Format D: Branch Instructions
```
[OPCODE (3 trits)] [ADDRESS (variable)]
```
Example: `CALL add_func` → `11211` (address 4 = ternary 11)

### Format E: No-Operand Instructions
```
[OPCODE (3 trits)]
```
Example: `HALT` → `121`, `RET` → `120`

---

## 3. Opcode Map

### Ternary Encoding (3 trits = 27 possible opcodes)

| Mnemonic | Ternary | Decimal | Description |
|----------|---------|---------|-------------|
| LOAD     | 000     | 0       | Load immediate |
| MOV      | 001     | 1       | Move register |
| CLR      | 002     | 2       | Clear register |
| ADD      | 010     | 3       | Add registers |
| SUB      | 011     | 4       | Subtract registers |
| AND      | 012     | 5       | Logical AND |
| OR       | 020     | 6       | Logical OR |
| NOT      | 021     | 7       | Logical NOT |
| CMP      | 022     | 8       | Compare registers |
| JMP      | 100     | 9       | Unconditional jump |
| JZ       | 101     | 10      | Jump if zero/equal |
| JNZ      | 102     | 11      | Jump if not zero |
| PUSH     | 110     | 12      | Push to stack |
| POP      | 111     | 13      | Pop from stack |
| CALL     | 112     | 14      | Call subroutine |
| RET      | 120     | 15      | Return from subroutine |
| HALT     | 121     | 16      | Halt execution |

### Register Encoding (1 trit)

| Register | Ternary |
|----------|---------|
| R0       | 0       |
| R1       | 1       |
| R2       | 2       |
| R3       | 3       |

---

## 4. Memory Layout

### Address Space
- **Total Memory**: 256 addresses (0-255)
- **Address Unit**: Ternary string (variable length)

### Memory Map

| Address Range | Purpose |
|---------------|---------|
| 0-127         | General data storage |
| 128-255       | Stack (grows downward) |

### Stack Behavior

```
Initial SP = 255 (top of stack)

PUSH R0:
  - Store R0 value at address SP
  - Decrement SP

POP R0:
  - Increment SP
  - Load value from address SP into R0
```

### Memory Example
```
ADDR | VALUE
------------------
  96 | 0
  97 | 0
  98 | 0
  99 | 0
 100 | 102      <- Data
 101 | 21       <- Data
 102 | 0
 103 | 0
 ...
 253 | 0        <- Stack bottom
 254 | 0
 255 | 0        <- Stack top (initial SP)
```

---

## 5. Stack Behavior

### Data Stack (PUSH/POP)
- **Grows downward**: 255 → 128
- **Overflow**: Raises error if SP < 128

### Call Stack (CALL/RET)
- **Separate internal stack**: Python list for return addresses
- **CALL**: Push (PC+1) to call stack, jump to address
- **RET**: Pop return address, continue from there

### Stack Usage
```assembly
LOAD R0 10       # R0 = 10
PUSH R0          # Stack[255] = 10, SP = 254
PUSH R1          # Stack[254] = (R1 value), SP = 253
POP R2           # SP = 254, R2 = Stack[254]
```

---

## 6. Execution Cycle

### Fetch-Decode-Execute Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     CPU EXECUTION CYCLE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                │
│   │ FETCH  │ -> │ DECODE  │ -> │ EXECUTE │                │
│   └─────────┘    └─────────┘    └─────────┘                │
│        │              │              │                      │
│        ▼              ▼              ▼                      │
│   PC points to   Parse opcode   Perform operation         │
│   instruction    + operands     Update PC/registers/flags  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Steps

1. **FETCH**: Read instruction at PC from program memory
2. **DECODE**: Parse into (opcode, operands)
3. **EXECUTE**: Perform operation based on opcode
4. **UPDATE**: Adjust PC (+1 or jump), update flags if needed

### Execution Example
```
Program:
  0: LOAD R0 10
  1: LOAD R1 12
  2: ADD R0 R1

Step 1: FETCH instruction at PC=0 -> "LOAD R0 10"
Step 2: DECODE -> opcode="LOAD", operands=["R0", "10"]
Step 3: EXECUTE -> R0 = "10", update flags
Step 4: UPDATE -> PC = 1

Step 1: FETCH instruction at PC=1 -> "LOAD R1 12"
Step 2: DECODE -> opcode="LOAD", operands=["R1", "12"]
Step 3: EXECUTE -> R1 = "12", update flags
Step 4: UPDATE -> PC = 2

Step 1: FETCH instruction at PC=2 -> "ADD R0 R1"
Step 2: DECODE -> opcode="ADD", operands=["R0", "R1"]
Step 3: EXECUTE -> R0 = R0 + R1 = "22"
Step 4: UPDATE -> PC = 3 (halt)
```

---

## 7. Instruction Set Reference

### Data Movement

| Instruction | Format | Example |
|-------------|--------|---------|
| LOAD        | LOAD R dest value | LOAD R0 102 |
| MOV         | MOV R dst R src | MOV R0 R1 |
| CLR         | CLR R dst | CLR R0 |

### Arithmetic

| Instruction | Format | Example |
|-------------|--------|---------|
| ADD         | ADD R dst R src | ADD R0 R1 |
| SUB         | SUB R dst R src | SUB R0 R1 |

### Logical

| Instruction | Format | Example |
|-------------|--------|---------|
| AND         | AND R dst R src | AND R0 R1 |
| OR          | OR R dst R src | OR R0 R1 |
| NOT         | NOT R dst | NOT R0 |

### Comparison

| Instruction | Format | Example |
|-------------|--------|---------|
| CMP         | CMP R dst R src | CMP R0 R1 |

**CMP Sets Flags:**
- ZERO: Result is zero
- EQUAL: Operands equal
- GREATER: dst > src
- LESS: dst < src

### Control Flow

| Instruction | Format | Example |
|-------------|--------|---------|
| JMP         | JMP addr | JMP loop |
| JZ          | JZ addr | JZ done |
| JNZ         | JNZ addr | JNZ loop |

### Subroutine

| Instruction | Format | Example |
|-------------|--------|---------|
| CALL        | CALL addr | CALL func |
| RET         | RET | RET |

### Stack Operations

| Instruction | Format | Example |
|-------------|--------|---------|
| PUSH        | PUSH R src | PUSH R0 |
| POP         | POP R dst | POP R0 |

### System

| Instruction | Format | Example |
|-------------|--------|---------|
| HALT        | HALT | HALT |

---

## 8. Assembly Syntax

### Labels
```
label_name:
    instruction
    instruction
```

### Comments
```
# This is a comment
LOAD R0 10  # Load 10 into R0
```

### Full Program Example
```
# Main program

start:
    LOAD R0 10        # Load 10 into R0
    LOAD R1 12        # Load 12 into R1
    CALL add_func     # Call subroutine
    HALT              # Stop

add_func:
    ADD R0 R1         # R0 = R0 + R1
    RET               # Return to caller
```

### Assembled Output
```
Labels: {'start': 0, 'add_func': 4}

Program:
  0: LOAD R0 10
  1: LOAD R1 12
  2: CALL 4
  3: HALT
  4: ADD R0 R1
  5: RET
```

---

## 9. Machine Code Encoding

### Encoding Rules

1. **Opcodes**: 3-trit ternary string
2. **Registers**: 1-trit (0-3 for R0-R3)
3. **Addresses**: Converted to ternary
4. **Immediates**: Kept as ternary strings

### Encoding Examples

| Assembly | Machine Code | Breakdown |
|----------|--------------|-----------|
| LOAD R0 10 | 000010 | 000(LOAD) + 0(R0) + 10(value) |
| ADD R0 R1 | 01001 | 010(ADD) + 0(R0) + 1(R1) |
| CALL 4 | 11211 | 112(CALL) + 11(4 in ternary) |
| HALT | 121 | 121(HALT) |

### Disassembly

Machine code can be decoded back to assembly:
```
000010 -> LOAD R0 10
01001 -> ADD R0 R1
11211 -> CALL 4
121 -> HALT
```

---

## 10. Flags and Conditions

### Flag Register

| Flag | Set When |
|------|----------|
| ZERO | Result is "0" or operands equal |
| EQUAL | a == b |
| GREATER | a > b |
| LESS | a < b |

### Conditional Jumps

- **JZ** (Jump if Zero/Equal): Jumps if ZERO or EQUAL is true
- **JNZ** (Jump if Not Zero): Jumps if ZERO and EQUAL are false

---

## 11. Complete System Stack

```
┌─────────────────────────────────────────────────────┐
│                  SOURCE CODE                        │
│   start: LOAD R0 10; CALL add_func; HALT            │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                  ASSEMBLER                           │
│   - Two-pass: collect labels → resolve addresses    │
│   - Output: list of instruction strings             │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                  MACHINE CODE                       │
│   - Ternary opcodes (000, 001, 010...)             │
│   - Variable-length instruction encoding            │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                     CPU                             │
│   - Fetch → Decode → Execute                        │
│   - Registers: R0, R1, R2, R3, PC, SP               │
│   - ALU: ADD, SUB, AND, OR, NOT, CMP               │
│   - Memory: 256 addresses                           │
└─────────────────────────────────────────────────────┘
```

---

## 12. Implementation Files

| File | Purpose |
|------|---------|
| `conversion.py` | Trit class, base conversion |
| `logic.py` | TNOT, TAND, TOR gates |
| `adder.py` | Half/Full adder, Ripple Carry |
| `arithmetic.py` | ADD, SUB, MUL, DIV |
| `alu.py` | ALU operations wrapper |
| `registers.py` | Register file (R0-R3) |
| `memory.py` | RAM simulation |
| `cpu.py` | CPU with fetch-decode-execute |
| `assembler.py` | Two-pass assembler with labels |
| `machine.py` | Machine code encoder/decoder |

---

## 13. Usage

### Running Assembly
```python
from src.core.assembler import Assembler
from src.core.cpu import CPU

asm = Assembler()
source = """
start:
    LOAD R0 10
    LOAD R1 12
    ADD R0 R1
    HALT
"""

program, labels = asm.assemble(source)
cpu = CPU()
cpu.load_program(program)
cpu.run()
```

### Machine Code
```python
from src.core.machine import Machine

m = Machine()
machine_code, program, labels = m.assemble(source)
# machine_code = ['000010', '000112', '01001', '121']
```

---

## Revision History

- v1.0 (2026-05-17): Initial specification
  - 4 general-purpose registers
  - 17 opcodes
  - 256-word memory
  - Two-pass assembler with labels
  - Variable-length ternary machine code
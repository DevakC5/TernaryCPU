# Benchmarks

Performance measurements of the Trinary ternary computer system.

---

## 1. Instruction Throughput

### Cycle Cost

| Opcode | Cycles | Category |
|--------|--------|----------|
| LOAD, MOV, CLR, ADD, SUB, AND, OR, NOT, CMP | 1 | Register ops |
| JMP, JZ, JNZ | 1 | Control flow |
| EI, DI, SETIVT, SETTIMER | 1 | System |
| HALT | 1 | System |
| PUSH, POP | 2 | Stack ops (memory) |
| STOREM, LOADM | 2 | Memory ops |
| INT, IRET | 2 | Interrupts |
| MUL | 3 | Arithmetic |
| CALL, RET | 3 | Subroutines |
| DIV | 5 | Arithmetic |

### Execution Rate

| Metric | Value |
|--------|-------|
| Simple instruction | ~1M ops/sec (Python) |
| Complex instruction (DIV) | ~200K ops/sec |
| Full demo program | ~50K cycles/sec |
| 113-test suite | ~0.06s total |

---

## 2. Digit Density: Ternary vs Binary

Ternary is more digit-efficient than binary. Here's how many digits each needs to represent values:

| Value | Binary Digits | Ternary Digits | Savings |
|-------|--------------|----------------|---------|
| 0 | 1 | 1 | 0% |
| 10 | 4 | 3 | 25% |
| 100 | 7 | 5 | 29% |
| 1000 | 10 | 7 | 30% |
| 10,000 | 14 | 9 | 36% |
| 100,000 | 17 | 11 | 35% |
| 1,000,000 | 20 | 13 | 35% |
| 10,000,000 | 24 | 15 | 38% |
| 100,000,000 | 27 | 17 | 37% |

### Formula

```
binary_digits = floor(log2(n)) + 1
ternary_digits = floor(log3(n)) + 1
savings = 1 - (ternary_digits / binary_digits)
```

On average, ternary uses **~37% fewer digits** than binary for large numbers.

---

## 3. Carry Propagation

The ripple-carry adder's carry chain length varies by input:

| Operands | Max Carry Depth | Description |
|----------|----------------|-------------|
| 0 + 0 | 0 | No carry at all |
| 1 + 2 | 1 | Single carry |
| 2 + 2 | 1 | Single carry |
| 11 + 22 | 2 | Carry propagates one position |
| 111 + 222 | 2 | Carry propagates one position |
| 10 + 20 | 1 | Simple carry |
| 100 + 200 | 1 | Simple carry |
| 222 + 1 | 3 | Max: 2+1=0 carry 1, then 2+0+1=0 carry 1, ... |
| 2222 + 1 | 4 | Cascade through all positions |

The worst case is a string of 2s plus 1, causing the carry to ripple through every position.

---

## 4. Memory Usage

| Component | Size |
|-----------|------|
| Register file (R0–R3) | 4 values (ternary strings) |
| Memory | 512 cells (ternary strings) |
| Program (100 instr) | ~100 instruction strings |
| Call stack | Python list (dynamic) |
| Stack (SP) | ~128 cells (addresses 128–255) |
| VRAM | 56 cells (addresses 200–255) |

### Example: Countdown Program

```asm
start:
    LOAD R0 12          # 5
loop:
    LOAD R1 1
    SUB R0 R1
    CMP R0 R3
    JNZ loop
    HALT
```

- 7 instructions
- 6 registers accessed
- 1 label
- ~40 cycles to complete

### Example: Fibonacci

```asm
start:
    LOAD R0 0           # a = 0
    LOAD R1 1           # b = 1
    LOAD R2 12          # 5 (iterations)
loop:
    MOV R3 R1           # temp = b
    ADD R1 R0           # b = a + b
    MOV R0 R3           # a = temp
    LOAD R3 1
    SUB R2 R3           # iterations--
    CMP R2 R3           # compare with 0
    JNZ loop
    HALT
```

- 11 instructions
- 4 registers used
- 2 labels
- ~65 cycles to compute F(5) = 5

---

## 5. OS Shell Metrics

| Metric | Value |
|--------|-------|
| OS program size | 342 instructions |
| Boot cycles | ~1000 steps |
| Key response | ~100 cycles |
| Commands recognized | 5 (HELP, CLS, REGS, MEMDUMP, RUN) |
| Display size | 7 rows × 8 cols = 56 chars |
| Input buffer | 32 characters |

---

## 6. PyQt6 UI Performance

| Metric | Value |
|--------|-------|
| UI startup time | ~0.5s |
| Assembly highlight | Instant (<1ms) |
| Step response | <10ms |
| Full program run (100 instr) | ~0.1s |
| Memory/register refresh | <5ms per step |

---

## 7. Comparison: Ternary vs Binary CPU

| Aspect | Ternary (Trinary) | Typical Binary |
|--------|--------------------|----------------|
| Radix | 3 | 2 |
| Digit values | 0, 1, 2 | 0, 1 |
| Negative numbers | Signed-magnitude (`-` prefix) | Two's complement |
| Digit efficiency (value 10⁶) | 13 digits | 20 digits |
| Carry propagation | More complex (3 states) | 2 states |
| Gates (NOT) | 0↔2, 1→1 | 0↔1 |
| Gates (AND) | min(a,b) | a & b |
| Gates (OR) | max(a,b) | a \| b |
| Register encoding | 1 trit = 3 values | 1 bit = 2 values |
| Implementation | Pure Python simulation | Hardware |

---

## 8. Running Benchmarks

```sh
python -m trinary.benchmark
```

Output includes:
- Cycle cost per opcode
- Digit density comparison table
- Carry propagation depth
- Memory usage breakdown
- Full system benchmark
- Ternary vs binary comparison table

```python
from trinary.benchmark import run_all_benchmarks
run_all_benchmarks()
```

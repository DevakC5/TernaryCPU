# Instruction Set Reference

Complete technical reference for all 31 Trinary CPU instructions.

---

## Instruction Formats

| Format | Name | Pattern | Encoding | Example |
|--------|------|---------|----------|---------|
| A | Two-Register | `OP R_dst R_src` | opcode(3) + dst(1) + src(1) | `ADD R0 R1` → `01001` |
| B | One-Register | `OP R_op` | opcode(3) + reg(1) | `CLR R0` → `0020` |
| C | Immediate | `OP R_dst value` | opcode(3) + dst(1) + value(variable) | `LOAD R0 10` → `000010` |
| D | Branch | `OP address` | opcode(3) + addr(variable) | `CALL 4` → `11211` |
| E | No-Operand | `OP` | opcode(3) | `HALT` → `121` |
| M | Memory | `OP address R_reg` | opcode(3) + reg(1) + addr(variable) | `STOREM 33 R0` → `20101020` |
| T | Tensor | `OP operands...` | opcode(3) + raw operands | `TLOADW 100 2 2` → `22110022` |

### Register Encoding

| Register | Trit |
|----------|------|
| R0 | 0 |
| R1 | 1 |
| R2 | 2 |
| R3 | 3 |

---

## Data Movement Instructions

### LOAD — Load Immediate

```
LOAD R_dst value
```

Loads a ternary immediate value into a register.

| Field | Description |
|-------|-------------|
| Format | C |
| Cycles | 1 |
| Flags affected | None |

**Examples:**
```asm
LOAD R0 10       # R0 = "10" (decimal 3)
LOAD R1 1012     # R1 = "1012" (decimal 32)
LOAD R2 -11      # R2 = "-11" (decimal -4)
LOAD R3 0        # R3 = "0"
```

**Implementation:**
```python
self.registers.load(dst, value)  # value kept as-is (ternary string)
```

---

### MOV — Move Register

```
MOV R_dst R_src
```

Copies the value of one register to another.

| Field | Description |
|-------|-------------|
| Format | A |
| Cycles | 1 |
| Flags affected | None |

**Examples:**
```asm
MOV R0 R1   # R0 = R1
MOV R2 R3   # R2 = R3
```

**Implementation:**
```python
value = self.registers.store(src)
self.registers.load(dst, value)
```

---

### CLR — Clear Register

```
CLR R_dst
```

Sets a register to `"0"`.

| Field | Description |
|-------|-------------|
| Format | B |
| Cycles | 1 |
| Flags affected | None |

**Examples:**
```asm
CLR R0    # R0 = "0"
CLR R1    # R1 = "0"
```

**Implementation:**
```python
self.registers.load(dst, "0")
```

---

## Arithmetic Instructions

### ADD — Add Registers

```
ADD R_dst R_src
```

Adds two registers using decimal round-trip arithmetic.

| Field | Description |
|-------|-------------|
| Format | A |
| Cycles | 1 |
| Flags affected | ZERO, EQUAL, GREATER, LESS |

**Examples:**
```asm
LOAD R0 10       # R0 = "10" (3)
LOAD R1 12       # R1 = "12" (5)
ADD R0 R1        # R0 = "22" (8)
```

**Arithmetic:**
```
decimal(reg[dst]) + decimal(reg[src]) → result
reg[dst] = decimal_to_ternary(result)
```

Supports negative numbers:
```asm
LOAD R0 10       # R0 = "10" (3)
LOAD R1 -1       # R1 = "-1" (-1)
ADD R0 R1        # R0 = "2" (2)
```

**Implementation:**
```python
a = self.registers.store(dst)
b = self.registers.store(src)
result, _ = alu("ADD", a, b)
self.registers.load(dst, result)
```

---

### SUB — Subtract Registers

```
SUB R_dst R_src
```

Subtracts src from dst using decimal round-trip arithmetic.

| Field | Description |
|-------|-------------|
| Format | A |
| Cycles | 1 |
| Flags affected | ZERO, EQUAL, GREATER, LESS |

**Examples:**
```asm
LOAD R0 12       # R0 = "12" (5)
LOAD R1 10       # R1 = "10" (3)
SUB R0 R1        # R0 = "2" (2)

SUB R1 R0        # R1 = "-1" (-1, after R0=2)
```

---

### MUL — Multiply Registers

```
MUL R_dst R_src
```

Multiplies two registers.

| Field | Description |
|-------|-------------|
| Format | A |
| Cycles | 3 |
| Flags affected | ZERO, EQUAL, GREATER, LESS |

**Examples:**
```asm
LOAD R0 12       # R0 = "12" (5)
LOAD R1 10       # R1 = "10" (3)
MUL R0 R1        # R0 = "120" (15)
```

---

### DIV — Divide Registers

```
DIV R_dst R_src
```

Divides dst by src. Uses floor division.

| Field | Description |
|-------|-------------|
| Format | A |
| Cycles | 5 |
| Flags affected | ZERO, EQUAL, GREATER, LESS |

**Examples:**
```asm
LOAD R0 120       # R0 = "120" (15)
LOAD R1 10        # R1 = "10" (3)
DIV R0 R1         # R0 = "12" (5)
```

**Error:** Division by zero raises `ZeroDivisionError`.

---

## Logical Instructions

### AND — Logical AND

```
AND R_dst R_src
```

Element-wise ternary AND between two registers. Operands are padded to equal length with leading zeros.

| Field | Description |
|-------|-------------|
| Format | A |
| Cycles | 1 |
| Flags affected | None |

**Truth table:** `tand(a, b) = min(a, b)` where 0=false, 1=neutral, 2=true.

| A | B | Result |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 0 | 2 | 0 |
| 1 | 1 | 1 |
| 1 | 2 | 1 |
| 2 | 2 | 2 |

**Examples:**
```asm
LOAD R0 22        # R0 = "22"
LOAD R1 12        # R1 = "12"
AND R0 R1         # R0 = "12" (element-wise min: min(2,1)=1, min(2,2)=2)
```

---

### OR — Logical OR

```
OR R_dst R_src
```

Element-wise ternary OR between two registers. Operands are padded to equal length.

| Field | Description |
|-------|-------------|
| Format | A |
| Cycles | 1 |
| Flags affected | None |

**Truth table:** `tor(a, b) = max(a, b)`.

| A | B | Result |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 0 | 2 | 2 |
| 1 | 1 | 1 |
| 1 | 2 | 2 |
| 2 | 2 | 2 |

**Examples:**
```asm
LOAD R0 20        # R0 = "20"
LOAD R1 2         # R1 = "2"
OR R0 R1          # R0 = "22" (pad: "020" OR "002" → "022" → "22")
```

---

### NOT — Logical NOT

```
NOT R_dst
```

Element-wise ternary NOT. Single-operand instruction.

| Field | Description |
|-------|-------------|
| Format | B |
| Cycles | 1 |
| Flags affected | None |

**Truth table:** 0→2, 1→1, 2→0.

| Input | Output |
|-------|--------|
| 0 | 2 |
| 1 | 1 |
| 2 | 0 |

**Examples:**
```asm
LOAD R0 20        # R0 = "20"
NOT R0            # R0 = "02" → "2" (2→0, 0→2)
```

---

## Comparison Instruction

### CMP — Compare Registers

```
CMP R_dst R_src
```

Compares two registers and sets condition flags. Does not modify register values.

| Field | Description |
|-------|-------------|
| Format | A |
| Cycles | 1 |
| Flags affected | ZERO, EQUAL, GREATER, LESS |

**Flag effects:**

| Result | ZERO | EQUAL | GREATER | LESS |
|--------|------|-------|---------|------|
| dst == src | True | True | False | False |
| dst > src | False | False | True | False |
| dst < src | False | False | False | True |

**Examples:**
```asm
LOAD R0 10        # R0 = "10" (3)
LOAD R1 12        # R1 = "12" (5)
CMP R0 R1         # LESS = True  (3 < 5)
JZ  done          # NOT taken (ZERO/EQUAL is False)
JMP try_gt        # Jump elsewhere

CMP R1 R0         # GREATER = True (5 > 3)

LOAD R0 10        # R0 = "10" (3)
LOAD R1 10        # R1 = "10" (3)
CMP R0 R1         # ZERO = True, EQUAL = True
JZ  equal_label   # Taken!
```

**JZ / JNZ behavior:**
- `JZ addr`: jumps if ZERO or EQUAL is True
- `JNZ addr`: jumps if BOTH ZERO and EQUAL are False

---

## Control Flow Instructions

### JMP — Unconditional Jump

```
JMP address
```

Sets PC to the given address unconditionally.

| Field | Description |
|-------|-------------|
| Format | D |
| Cycles | 1 |
| Flags affected | None |

**Examples:**
```asm
JMP loop         # Jump to loop label
JMP 4            # Jump to instruction address 4
```

---

### JZ — Jump if Zero/Equal

```
JZ address
```

Jumps to address if ZERO or EQUAL flag is True.

| Field | Description |
|-------|-------------|
| Format | D |
| Cycles | 1 |
| Flags affected | None |

**Examples:**
```asm
CMP R0 R1
JZ done          # Jump if R0 == R1
```

---

### JNZ — Jump if Not Zero

```
JNZ address
```

Jumps to address if BOTH ZERO and EQUAL flags are False.

| Field | Description |
|-------|-------------|
| Format | D |
| Cycles | 1 |
| Flags affected | None |

**Examples:**
```asm
CMP R0 R1
JNZ loop         # Jump if R0 != R1
```

---

### JMPR — Jump Indirect via Register

```
JMPR R_src
```

Unconditionally jumps to the address stored in register `R_src`.

| Field | Description |
|-------|-------------|
| Format | B |
| Cycles | 1 |
| Flags affected | None |

**Examples:**
```asm
LOAD R0 11       # R0 = address 4 (decimal)
JMPR R0          # Jump to address 4
```

---

### JZR — Jump if Zero via Register

```
JZR R_src
```

Jumps to the address stored in `R_src` if ZERO or EQUAL flag is True.

| Field | Description |
|-------|-------------|
| Format | B |
| Cycles | 1 |
| Flags affected | None |

---

### JNZR — Jump if Not Zero via Register

```
JNZR R_src
```

Jumps to the address stored in `R_src` if BOTH ZERO and EQUAL flags are False.

| Field | Description |
|-------|-------------|
| Format | B |
| Cycles | 1 |
| Flags affected | None |

---

## Subroutine Instructions

### CALL — Call Subroutine

```
CALL address
```

Pushes (PC + 1) to the call stack and jumps to address.

| Field | Description |
|-------|-------------|
| Format | D |
| Cycles | 3 |
| Flags affected | None |

**Examples:**
```asm
start:
    LOAD R0 10
    CALL my_func   # Call subroutine
    HALT

my_func:
    ADD R0 R1
    RET
```

**Note:** CALL/RET use the same hardware memory stack (SP) as PUSH/POP. Return addresses and data share the 128-cell stack region (128–255).

---

### RET — Return from Subroutine

```
RET
```

Pops a return address from the call stack and continues execution there.

| Field | Description |
|-------|-------------|
| Format | E |
| Cycles | 3 |
| Flags affected | None |

**Error:** `StackUnderflowError` if call stack is empty.

---

### CALLR — Call Subroutine Indirect via Register

```
CALLR R_src
```

Pushes (PC + 1) to the hardware stack and jumps to the address stored in `R_src`.

| Field | Description |
|-------|-------------|
| Format | B |
| Cycles | 3 |
| Flags affected | None |

**Examples:**
```asm
LOAD R0 11       # Load function address into R0
CALLR R0         # Call function via register
```

---

## Stack Instructions

### PUSH — Push to Stack

```
PUSH R_src
```

Stores a register's value on the memory stack and decrements SP.

| Field | Description |
|-------|-------------|
| Format | B |
| Cycles | 2 |
| Flags affected | None |

**Behavior:**
```python
self.memory.store(self.sp, self.registers.store(src))
self.sp -= 1
```

**Overflow:** If SP < 128, raises `StackOverflowError`.

**Examples:**
```asm
LOAD R0 10       # R0 = 3
PUSH R0          # memory[255] = "10", SP = 254
PUSH R1          # memory[254] = (R1 value), SP = 253
```

---

### POP — Pop from Stack

```
POP R_dst
```

Increments SP and loads a value from the memory stack into a register.

| Field | Description |
|-------|-------------|
| Format | B |
| Cycles | 2 |
| Flags affected | None |

**Behavior:**
```python
self.sp += 1
value = self.memory.load(self.sp)
self.registers.load(dst, value)
```

**Underflow:** If SP >= 255, raises `StackUnderflowError`.

**Examples:**
```asm
POP R0           # SP = 254, R0 = memory[254]
POP R1           # SP = 255, R1 = memory[255]
```

---

## Memory Instructions

### STOREM — Store Register to Memory

```
STOREM address R_src
```

Stores a register's value at a memory address.

| Field | Description |
|-------|-------------|
| Format | M |
| Cycles | 2 |
| Flags affected | None |

**Address modes:**
- Literal address: `STOREM 33 R0` → store at memory address 33
- Register-based address: `STOREM R2 R0` → store at address = value(R2)

**Examples:**
```asm
STOREM 33 R0     # memory[33] = R0
STOREM R2 R1     # memory[value(R2)] = R1

# Address from register:
LOAD R2 12       # R2 = "12" (5)
STOREM R2 R0     # memory[5] = R0
```

---

### LOADM — Load Memory into Register

```
LOADM address R_dst
```

Loads a value from memory address into a register.

| Field | Description |
|-------|-------------|
| Format | M |
| Cycles | 2 |
| Flags affected | None |

**Address modes:**
- Literal address: `LOADM 260 R1` → R1 = memory[260]
- Register-based address: `LOADM R2 R0` → R0 = memory[value(R2)]

**Examples:**
```asm
LOADM 260 R1     # R1 = memory[260] (keyboard buffer)
LOADM 0 R0       # R0 = memory[0] (OS cursor)

# Address from register:
LOAD R2 100      # R2 = "100" (9)
LOADM R2 R1      # R1 = memory[9]
```

---

## Interrupt Instructions

### EI — Enable Interrupts

```
EI
```

Sets the interrupt flag. When enabled, pending interrupts are handled before the next instruction.

| Field | Description |
|-------|-------------|
| Format | E |
| Cycles | 1 |
| Flags affected | None |

---

### DI — Disable Interrupts

```
DI
```

Clears the interrupt flag. Pending interrupts are deferred.

| Field | Description |
|-------|-------------|
| Format | E |
| Cycles | 1 |
| Flags affected | None |

---

### INT — Software Interrupt

```
INT n
```

Triggers interrupt n (0–7).

| Field | Description |
|-------|-------------|
| Format | D |
| Cycles | 2 |
| Flags affected | None |

**Behavior:**
```python
self.pc += 1
self.memory.store(self.sp, d2t(self.pc))  # push PC
self.sp -= 1
self.iflag = False  # disable interrupts
self.pc = self.ivt[n]  # jump to handler
```

The handler must end with `IRET` to return. Interrupts are automatically disabled on entry to prevent re-entrancy.

---

### IRET — Return from Interrupt

```
IRET
```

Returns from an interrupt handler.

| Field | Description |
|-------|-------------|
| Format | E |
| Cycles | 2 |
| Flags affected | None |

**Behavior:**
```python
self.sp += 1
self.pc = t2d(self.memory.load(self.sp))  # restore PC
self.iflag = True  # re-enable interrupts
```

---

### SETIVT — Set Interrupt Vector

```
SETIVT n address
```

Sets interrupt vector table entry n to a handler address.

| Field | Description |
|-------|-------------|
| Format | D (extended, two operands) |
| Cycles | 1 |
| Flags affected | None |

**Examples:**
```asm
SETIVT 0 timer_handler    # IVT[0] = address of timer_handler
SETIVT 1 key_handler      # IVT[1] = address of key_handler
```

---

## Timer Instruction

### SETTIMER — Set Timer Period

```
SETTIMER period
```

Sets the hardware timer period in CPU cycles. The timer fires interrupt 0 each time the counter reaches zero.

| Field | Description |
|-------|-------------|
| Format | D |
| Cycles | 1 |
| Flags affected | None |

**Behavior:**
```python
self.timer_period = period
self.timer_counter = period
```

Each `step()` decrements `timer_counter` by the executed instruction's cycle cost. When `timer_counter ≤ 0`, a pending interrupt 0 is set.

**Timer fires interrupt 0** — set up the handler with `SETIVT 0` before enabling.

**Examples:**
```asm
SETIVT 0 handler     # Set up timer handler
SETTIMER 50          # Fire interrupt every 50 cycles
EI                   # Enable interrupts

# Main loop:
loop:
    LOAD R0 1
    ADD R0 R0
    JMP loop

handler:
    # Increment counter on each timer tick
    LOADM 100 R0     # Load tick counter
    LOAD R1 1
    ADD R0 R1
    STOREM 100 R0    # Save tick counter
    IRET
```

---

## System Instruction

### HALT — Halt Execution

```
HALT
```

Stops CPU execution.

| Field | Description |
|-------|-------------|
| Format | E |
| Cycles | 1 |
| Flags affected | None |

**Behavior:**
```python
self.halted = True
```

After HALT, `CPU.step()` returns without fetching/executing further. `CPU.run()` stops. To resume, call `CPU.reset()` or set `halted = False` and `pc` manually.

---

## Accelerator Coprocessor Instructions

The Tensor Accelerator Coprocessor is a hardware unit integrated with the CPU that provides vector, matrix, and tensor operations using ternary arithmetic. The accelerator maintains its own tensor memory with allocation and shape tracking.

Operands for all tensor instructions can be immediate numbers or registers (R0–R3). When a register name is given, its decimal value is used as the operand. Results are stored in the accelerator's internal tensor memory; the resulting tensor ID (TID) is written into CPU register `R0` (converted via `decimal_to_ternary`).

### TLOADW — Load Tensor from CPU Memory

```
TLOADW addr rows cols
```

Loads a tile of CPU memory into the accelerator. Reads `rows × cols` consecutive values starting at `addr` from CPU memory, allocates a new tensor in accelerator memory, and stores the resulting TID in `R0`.

| Field | Description |
|-------|-------------|
| Format | T |
| Cycles | 10 |
| Flags affected | None |

**Operands:**
- `addr` — Starting CPU memory address (immediate or register)
- `rows` — Number of rows (immediate or register)
- `cols` — Number of columns (immediate or register)

**Behavior:**
```python
data = [memory.load(addr + i) for i in range(rows * cols)]
tid = accel.memory.allocate(data, shape=(rows, cols))
R0 = decimal_to_ternary(tid)
```

**Examples:**
```asm
# Load a 2x2 block from memory address 100
TLOADW 100 2 2       # Tensor loaded, TID → R0

# Using registers for operands
LOAD R0 100
LOAD R1 2
LOAD R2 2
TLOADW R0 R1 R2      # Equivalent: load 2x2 from addr 100
```

---

### TSTOREW — Store Tensor to CPU Memory

```
TSTOREW tid addr
```

Stores an accelerator tensor back into CPU memory. Reads tensor data from accelerator memory by TID and writes consecutive values starting at `addr`.

| Field | Description |
|-------|-------------|
| Format | T |
| Cycles | 10 |
| Flags affected | None |

**Operands:**
- `tid` — Tensor ID in accelerator memory (immediate or register)
- `addr` — Starting CPU memory address (immediate or register)

**Behavior:**
```python
data = accel.memory.load_list(tid)
for i, v in enumerate(data):
    memory.store(addr + i, str(v))
```

**Examples:**
```asm
# Store tensor with TID 0 to memory address 200
TSTOREW 0 200

# Using registers
LOAD R0 0
LOAD R1 200
TSTOREW R0 R1
```

---

### TVECADD — Vector Add

```
TVECADD dst src_a src_b
```

Performs element-wise ternary vector addition on the accelerator. Loads two source tensors by TID, adds corresponding elements using `TritSIMD.add_vectors`, allocates the result as a new tensor, and writes its TID to `R0`.

| Field | Description |
|-------|-------------|
| Format | T |
| Cycles | 4 |
| Flags affected | None |

**Operands:**
- `dst` — Result tensor ID (immediate or register; currently unused as new TID is allocated and stored in R0)
- `src_a` — First source tensor TID (immediate or register)
- `src_b` — Second source tensor TID (immediate or register)

**Behavior:**
```python
a = accel.memory.load_list(src_a)
b = accel.memory.load_list(src_b)
result = TritSIMD.add_vectors(a, b)
tid = accel.memory.allocate(result)
R0 = decimal_to_ternary(tid)
```

**Examples:**
```asm
TLOADW 100 2 2       # Load tensor A (TID in R0)
MOV R1 R0            # Save TID to R1
TLOADW 108 2 2       # Load tensor B (TID in R0)
MOV R2 R0            # Save TID to R2
TVECADD 0 R1 R2      # Element-wise add, result TID → R0
```

---

### TMATMUL — Matrix Multiply

```
TMATMUL dst src_a src_b
```

Performs matrix multiplication on the accelerator. Loads two source tensors by TID (as 2D matrices via `load_2d`), multiplies them using `TensorCore.matmul`, allocates the flattened result as a new tensor with the computed shape, and writes its TID to `R0`.

| Field | Description |
|-------|-------------|
| Format | T |
| Cycles | 20 |
| Flags affected | None |

**Operands:**
- `dst` — Result tensor ID (immediate or register; allocated new)
- `src_a` — First source tensor TID (immediate or register)
- `src_b` — Second source tensor TID (immediate or register)

**Behavior:**
```python
mat_a = accel.memory.load_2d(src_a)
mat_b = accel.memory.load_2d(src_b)
result = accel.core.matmul(mat_a, mat_b)
flat = [v for row in result for v in row]
tid = accel.memory.allocate(flat, shape=(len(result), len(result[0])))
R0 = decimal_to_ternary(tid)
```

**Examples:**
```asm
TLOADW 100 2 2       # Load 2x2 matrix A (TID in R0)
MOV R1 R0
TLOADW 104 2 2       # Load 2x2 matrix B (TID in R0)
MOV R2 R0
TMATMUL 0 R1 R2      # Matrix multiply, result TID → R0
TSTOREW R0 200       # Store result to CPU memory at addr 200
```

---

### TDOT — Dot Product

```
TDOT src_a src_b
```

Computes the dot product of two vectors on the accelerator. Loads two source tensors by TID, computes their dot product via `TritSIMD.dot_product`, and writes the scalar result (ternary-encoded) into CPU register `R0`.

| Field | Description |
|-------|-------------|
| Format | T |
| Cycles | 6 |
| Flags affected | None |

**Operands:**
- `src_a` — First source tensor TID (immediate or register)
- `src_b` — Second source tensor TID (immediate or register)

**Behavior:**
```python
a = accel.memory.load_list(src_a)
b = accel.memory.load_list(src_b)
result = TritSIMD.dot_product(a, b)
R0 = decimal_to_ternary(result)
```

**Examples:**
```asm
TLOADW 100 4 1       # Load 4-element vector A (TID in R0)
MOV R1 R0
TLOADW 104 4 1       # Load 4-element vector B (TID in R0)
MOV R2 R0
TDOT R1 R2           # Dot product, scalar result → R0
```

---

### TACT — Activation

```
TACT tid type
```

Applies an activation function in-place on a tensor in accelerator memory. Loads the tensor by TID, applies the selected activation element-wise, and stores the result back into the same tensor slot.

| Field | Description |
|-------|-------------|
| Format | T |
| Cycles | 3 |
| Flags affected | None |

**Operands:**
- `tid` — Tensor ID (immediate or register)
- `type` — Activation type: `0` = step function (immediate or register)

**Activation types:**

| Value | Function | Description |
|-------|----------|-------------|
| 0 | Step | `1 if x >= 0 else 0` (ternary threshold) |

**Behavior:**
```python
data = accel.memory.load_list(tid)
if type == 0:
    result = TritSIMD.ternary_threshold(data)
accel.memory.store(tid, result)
```

**Examples:**
```asm
TLOADW 100 4 1       # Load vector (TID in R0)
MOV R1 R0
TACT R1 0            # Apply step activation in-place

# Using register for type
LOAD R2 0
TACT R1 R2           # Equivalent: step activation
```

---

## Instruction Cycle Costs

| Opcode | Cycles | Notes |
|--------|--------|-------|
| LOAD | 1 | |
| MOV | 1 | |
| CLR | 1 | |
| ADD | 1 | |
| SUB | 1 | |
| AND | 1 | |
| OR | 1 | |
| NOT | 1 | |
| CMP | 1 | |
| JMP | 1 | |
| JZ | 1 | |
| JNZ | 1 | |
| PUSH | 2 | Memory write + SP decrement |
| POP | 2 | SP increment + memory read |
| CALL | 3 | Call stack push + jump |
| RET | 3 | Call stack pop + jump |
| HALT | 1 | |
| MUL | 3 | |
| DIV | 5 | Most expensive standard instruction |
| STOREM | 2 | Memory write |
| LOADM | 2 | Memory read |
| INT | 2 | Stack push + IVT lookup |
| IRET | 2 | Stack pop + restore |
| EI | 1 | |
| DI | 1 | |
| SETIVT | 1 | |
| SETTIMER | 1 | |
| TACT | 3 | Activation in-place |
| TVECADD | 4 | Element-wise vector add |
| TDOT | 6 | Dot product |
| TLOADW | 10 | Load CPU memory → accelerator tensor |
| TSTOREW | 10 | Store accelerator tensor → CPU memory |
| TMATMUL | 20 | Matrix multiply (most expensive overall) |

Cycle costs affect timer interrupts: the timer counter decrements by `CYCLES[opcode]` each step.

---

## Quick Reference Card

```
DATA MOVEMENT                    STACK
  LOAD R_dst value      [1]       PUSH R_src            [2]
  MOV R_dst R_src       [1]       POP R_dst             [2]
  CLR R_dst             [1]

                                  SUBROUTINES
ARITHMETIC                        CALL address          [3]
  ADD R_dst R_src        [1]      RET                   [3]
  SUB R_dst R_src        [1]
  MUL R_dst R_src        [3]     MEMORY
  DIV R_dst R_src        [5]      STOREM addr R_src     [2]
                                  LOADM addr R_dst      [2]
LOGICAL
  AND R_dst R_src        [1]     INTERRUPTS
  OR R_dst R_src         [1]      EI                    [1]
  NOT R_dst              [1]      DI                    [1]
                                  INT n                 [2]
COMPARISON                        IRET                  [2]
  CMP R_dst R_src        [1]      SETIVT n addr         [1]

CONTROL FLOW                      TIMER
  JMP address            [1]      SETTIMER period       [1]
  JZ address             [1]
  JNZ address            [1]     SYSTEM
                                  HALT                  [1]
                                  TENSOR ACCELERATOR
                                    TACT tid type       [3]
                                    TVECADD d a b       [4]
                                    TDOT a b            [6]
                                    TLOADW a r c       [10]
                                    TSTOREW t a        [10]
                                    TMATMUL d a b      [20]
```

## Flag Reference

| Flag | Set By | Cleared By | Checked By |
|------|--------|------------|------------|
| ZERO | CMP result == "EQ" | CMP result != "EQ" | JZ (jumps if True) |
| EQUAL | CMP result == "EQ" | CMP result != "EQ" | JZ (jumps if True) |
| GREATER | CMP result == "GT" | CMP result != "GT" | (not directly) |
| LESS | CMP result == "LT" | CMP result != "LT" | (not directly) |

Note: JZ jumps if ZERO OR EQUAL is True. JNZ jumps if BOTH are False.

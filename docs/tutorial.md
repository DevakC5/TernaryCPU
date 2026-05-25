# Tutorial — Getting Started with Ternary Programming

This tutorial walks through the Trinary system from scratch — number representation to a working program.

---

## Step 1: Ternary Numbers

### What Is Ternary?

Ternary is base-3: each digit position is a power of 3.

```
3^2  3^1  3^0
 9    3    1

  1    0    2   = 1×9 + 0×3 + 2×1 = 11 decimal
  2    2    2   = 2×9 + 2×3 + 2×1 = 26 decimal
```

### Using the Converter

```sh
python -m trinary.conversion
```

```
Enter a binary string: 1010
Decimal: 10
Ternary: 101
```

### Python API

```python
from trinary.conversion import decimal_to_ternary as d2t
from trinary.conversion import ternary_to_decimal as t2d

d2t(11)    # "102"
t2d("22")  # 8
d2t(-4)    # "-11"
t2d("-10") # -3
```

---

## Step 2: First Assembly Program

### Hello, CPU

Let's write a program that loads values into registers and adds them:

```asm
# my_first_program.asm
start:
    LOAD R0 10        # R0 = ternary "10" = decimal 3
    LOAD R1 12        # R1 = ternary "12" = decimal 5
    ADD R0 R1         # R0 = 3 + 5 = 8 = ternary "22"
    HALT
```

### Run It

```python
from trinary.cpu import CPU
from trinary.assembler import Assembler

source = """
start:
    LOAD R0 10
    LOAD R1 12
    ADD R0 R1
    HALT
"""

asm = Assembler()
program, labels = asm.assemble(source)

cpu = CPU()
cpu.load_program(program)
cpu.run(verbose=True)
```

Output:
```
   0: LOAD R0 10       R0→10 R1→0  R2→0  R3→0           Z:0 E:0 G:1 L:0
   1: LOAD R1 12       R0→10 R1→12 R2→0  R3→0           Z:0 E:0 G:1 L:0
   2: ADD R0 R1        R0→22 R1→12 R2→0  R3→0           Z:0 E:0 G:1 L:0
   3: HALT
```

Verify:
```python
t2d(cpu.registers.store("R0"))  # → 8
```

### What Happened

1. **LOAD R0 10**: The CPU parsed `"LOAD"`, identified R0 as destination, `"10"` as the value. R0 was set to the ternary string `"10"` (decimal 3).

2. **LOAD R1 12**: Same process. R1 = `"12"` (decimal 5).

3. **ADD R0 R1**: The CPU read R0 (`"10"`) and R1 (`"12"`), converted both to decimal (3, 5), added them (8), converted back to ternary (`"22"`), and stored in R0.

4. **HALT**: Set the halted flag, stopping execution.

---

## Step 3: Using Labels and Subroutines

Labels make programs readable. Subroutines allow code reuse.

```asm
# subroutine_demo.asm
start:
    LOAD R0 10          # R0 = 3
    LOAD R1 12          # R1 = 5
    CALL add_func       # Call subroutine
    HALT

add_func:
    ADD R0 R1           # R0 = R0 + R1
    RET                 # Return to caller
```

```python
program, labels = asm.assemble(source)
print(labels)  # {'start': 0, 'add_func': 4}
```

The assembler resolves `CALL add_func` to `CALL 4` (the address of `add_func`).

---

## Step 4: Control Flow

### Comparison and Branching

```asm
# compare.asm
start:
    LOAD R0 10          # R0 = 3
    LOAD R1 10          # R1 = 3
    CMP R0 R1           # Compare: are they equal?
    JZ equal_branch     # Yes → jump
    LOAD R0 0           # Not reached
    HALT

equal_branch:
    LOAD R2 20          # R2 = 6
    HALT
```

After execution, R2 = `"20"` (6).

### Looping

```asm
# countdown.asm
start:
    LOAD R0 12          # R0 = 5 (counter)
    LOAD R1 1           # R1 = 1 (decrement)

loop:
    SUB R0 R1           # R0 = R0 - 1
    CMP R0 R3           # Compare with 0 (R3 is always 0)
    JNZ loop            # If not zero, continue loop
    HALT                # Reached zero → stop
```

This counts R0 down from 5 to 0.

---

## Step 5: Stack Operations

The stack stores temporary data and grows downward from address 255.

```asm
# stack_demo.asm
start:
    LOAD R0 10          # R0 = 3
    LOAD R1 12          # R1 = 5
    PUSH R0             # Save R0 on stack
    PUSH R1             # Save R1 on stack
    CLR R0              # R0 = 0
    CLR R1              # R1 = 0
    POP R0              # Restore: R0 = old R1 (last pushed)
    POP R1              # Restore: R1 = old R0
    HALT
```

After execution: R0 = `"12"` (5), R1 = `"10"` (3). The stack is LIFO.

---

## Step 6: Memory Operations

### STOREM and LOADM

```asm
# memory_demo.asm
start:
    LOAD R0 11          # R0 = 4
    STOREM 100 R0       # memory[100] = R0
    LOAD R1 0           # R1 = 0
    LOADM 100 R1        # R1 = memory[100] = 4

    # Register-based addressing
    LOAD R2 42          # R2 = ternary address 42 → decimal 14
    STOREM R2 R0        # memory[14] = R0
    LOADM R2 R1         # R1 = memory[14] = "11"
    HALT
```

```python
t2d(cpu.memory.load(100))  # → 4
t2d(cpu.memory.load(14))   # → 4
```

---

## Step 7: Display Output

### Writing to VRAM

VRAM is at addresses 200–255. Each cell stores a ternary ASCII code.

```python
from trinary.conversion import decimal_to_ternary as d2t
from trinary.display import DisplayMemoryMap

# "Hello" in ASCII codes: 72, 101, 108, 108, 111
text = "Hello"
codes = [d2t(ord(c)) for c in text]
print(codes)  # ['2200', '11020', '11000', '11000', '11010']
```

### Assembly Program

```asm
# display_hello.asm
start:
    LOAD R1 2200        # R1 = 'H' (ternary 72)
    STOREM 200 R1       # VRAM[0] = 'H'
    LOAD R1 11020       # R1 = 'e' (ternary 101)
    STOREM 201 R1       # VRAM[1] = 'e'
    LOAD R1 11000       # R1 = 'l'
    STOREM 202 R1       # VRAM[2] = 'l'
    LOAD R1 11000       # R1 = 'l'
    STOREM 203 R1       # VRAM[3] = 'l'
    LOAD R1 11010       # R1 = 'o'
    STOREM 204 R1       # VRAM[4] = 'o'
    HALT
```

```python
display = DisplayMemoryMap()
chars = display.read_display(cpu.memory)
print("".join(chars[:5]))  # "Hello"
```

---

## Step 8: Keyboard Input

The keyboard buffer at address 260 receives ASCII codes.

```asm
# keyboard_poll.asm
start:
    LOADM 260 R1        # Poll keyboard
    CMP R1 R3           # Compare with 0
    JZ start            # No key → keep polling
    STOREM 260 R3       # Acknowledge: clear buffer
    STOREM 200 R1       # Echo to VRAM[0]
    HALT
```

```python
cpu.memory.store(260, d2t(ord('X')))
cpu.step()
cpu.step()  # First step: reads 'X', acknowledges
cpu.step()  # Second: stores X to VRAM

display = DisplayMemoryMap()
print(display.read_display(cpu.memory)[0])  # 'X'
```

---

## Step 9: Interrupts and Timer

### Timer Interrupt Demo

```asm
# timer_demo.asm
start:
    SETIVT 0 handler    # IVT[0] → handler address
    EI                   # Enable interrupts
    SETTIMER 10          # Timer fires every 10 cycles
    LOAD R0 0            # R0 = 0
    CLR R1               # R1 = 0 (tick counter)

loop:
    ADD R0 R0            # Main work
    JMP loop

handler:
    LOAD R1 1            # Increment tick counter
    ADD R0 R1            # (simplified)
    IRET                 # Return, re-enable interrupts
```

### Programmatic Interrupt

```asm
# software_int.asm
start:
    SETIVT 1 my_handler  # Set up handler
    INT 1                # Trigger software interrupt
    HALT

my_handler:
    LOAD R0 10           # Handler work
    IRET                 # Return
```

---

## Step 10: OS Shell

### Boot the OS

```sh
python -m trinary.os
```

The shell boots and displays:
```
Trishell!>
```

### Commands

```
Trishell!> HELP
HELP - CLS MEMDUMP REGS RUN
>
```

### Programmatic OS

```python
from trinary.os import OS

os = OS()
os.boot()

# Type "HELP" and press Enter
for ch in "HELP":
    os.feed_key(ch)
    for _ in range(500):
        if os.cpu.halted: break
        os.cpu.step()

os.feed_key(chr(10))   # Enter
for _ in range(5000):
    if os.cpu.halted: break
    os.cpu.step()

print(os.display_text())
```

---

## Step 11: Machine Code

### Encode to Ternary

```python
from trinary.machine import Machine

source = """
start:
    LOAD R0 10
    LOAD R1 12
    ADD R0 R1
    HALT
"""

m = Machine()
machine_code, program, labels = m.assemble(source)

for i, (mc, asm) in enumerate(zip(machine_code, program)):
    print(f"{i:>4} | {asm:<20} | {mc}")
```

Output:
```
   0 | LOAD R0 10          | 000010
   1 | LOAD R1 12          | 000112
   2 | ADD R0 R1           | 01001
   3 | HALT                | 121
```

### Decode Back

```python
disassembled = m.disassemble(machine_code)
for d in disassembled:
    print(d)
# LOAD R0 10
# LOAD R1 12
# ADD R0 R1
# HALT
```

---

## Step 12: PyQt6 Visual Simulator

Launch the desktop UI:

```sh
pip install pyqt6
python -m trinary.ui.app
```

### Workflow

1. Select a demo from the dropdown (e.g., "Countdown")
2. Click **Assemble** — the editor content is assembled and loaded
3. Click **Step Into** repeatedly — watch registers change
4. Click **Run** — executes to completion
5. View the **Execution Trace** table for the full history
6. Open the **Memory Viewer** to see stack changes
7. Check **Register Panel** for R0–R3, PC, SP, flags

---

## Step 13: Fantasy Console SDK

The Fantasy Console SDK provides a high-level game development API with a 64×64 pixel framebuffer, sprites, tilemaps, audio, and input handling.

### Engine and Runtime

Create a game by defining an `Engine` subclass with `init()`, `update()`, and `render()` methods, then run it with `Runtime`.

### Bouncing Ball Example

```python
from trinary.sdk import Engine, Runtime, Sprite, cls, spr, set_engine
from trinary.display.framebuffer import Framebuffer

class BouncingBall:
    def __init__(self):
        self.fb = Framebuffer()
        self.eng = Engine(self.fb)
        self.ball = Sprite.from_strings([
            "..@..",
            ".@@@.",
            "@@@@@",
            ".@@@.",
            "..@..",
        ])
        self.x, self.y = 32, 32
        self.dx, self.dy = 1, 1

    def loop(self):
        self.eng.init()
        for _ in range(300):
            self.update()
            self.render()
            self.fb.present()

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= 59:
            self.dx = -self.dx
        if self.y <= 0 or self.y >= 59:
            self.dy = -self.dy

    def render(self):
        cls(0)
        spr(self.ball, self.x, self.y, color_override=2)

set_engine(BouncingBall().eng)
BouncingBall().loop()
```

### API Reference

| Function | Description |
|----------|-------------|
| `cls(color)` | Clear screen with color |
| `spr(sprite, x, y)` | Draw sprite at position |
| `btn(name)` | Check if button is held |
| `btnp(name)` | Check if button was just pressed |
| `pixel(x, y, color)` | Set individual pixel |
| `rect(x, y, w, h, color)` | Draw filled rectangle |
| `print_text(text, x, y)` | Draw text |
| `sfx(freq, dur)` | Play audio beep |

### Built-in Demos

```sh
python -m trinary.demo_games pong
python -m trinary.demo_games snake
python -m trinary.demo_games breakout
python -m trinary.demo_games particles
python -m trinary.demo_games paint
python -m trinary.demo_games bouncing_logo
python -m trinary.demo_games tilemap
python -m trinary.demo_games rpg
```

---

## Step 14: TAL Compiler

TAL (Ternary Assembly Language) is a structured high-level language that compiles down to ternary CPU assembly. It provides variables, constants, control flow, and drawing primitives.

### Writing a Simple TAL Program

```tal
var counter @100
var result @101

const MAX = 10

label start:
    store counter, 0

label loop_start:
    if_eq counter, MAX, done
    inc counter
    jmp loop_start

label done:
    store result, counter
    halt
```

### Compile and Run

```python
from trinary.tal import compile_and_assemble
from trinary.cpu import CPU

source = """
var counter @100
const MAX = 10
label start:
    store counter, 0
label loop:
    if_eq counter, MAX, done
    inc counter
    jmp loop
label done:
    halt
"""

program, labels = compile_and_assemble(source, entry_point="start")
cpu = CPU()
cpu.load_program(program)
cpu.run(verbose=False)
```

### TAL Instruction Reference

| Instruction | Description |
|-------------|-------------|
| `var name @addr` | Declare variable at memory address |
| `const name = value` | Declare named constant |
| `store var, value` | Store value into variable |
| `load var, addr` | Load from address into variable |
| `inc var` | Increment variable |
| `dec var` | Decrement variable |
| `add dst, a, b` | Add two values |
| `sub dst, a, b` | Subtract two values |
| `if_eq a, b, label` | Branch if equal |
| `if_ne a, b, label` | Branch if not equal |
| `draw x, y, color` | Set pixel on framebuffer |
| `clear x, y` | Clear pixel on framebuffer |
| `write addr, value` | Write value to memory address |
| `jmp label` | Unconditional jump |

### Snake Game in TAL

The snake game (`test_snake_tal.py`) is a complete game written in TAL with 524 compiled instructions. It features a circular buffer for the snake body (memory addresses 20–147), keyboard input (WASD), collision detection, food spawning, and a 64×64 pixel framebuffer display.

```sh
python test_snake_tal.py
```

---

## Step 15: Hardware Simulation

The CPU supports a cycle-accurate microarchitecture simulation mode that models a 5-stage pipeline, L1 caches, branch predictor, DMA, bus, interrupt controller, and profiler.

### Enable Realistic Timing

```python
from trinary.cpu import CPU

cpu = CPU(realistic_timing=True)
cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])
cpu.run(verbose=False)

print(f"Cycles: {cpu.clock.cycle}")
print(cpu.profiler.report())
```

### Pipeline Visualizer

```python
from trinary.cpu import CPU

cpu = CPU(realistic_timing=True)
cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])

# Step through cycle by cycle
for i in range(12):
    cpu.step()
    print(cpu.pipeline.visualize(cycle=i))
```

Example output:
```
Cycle    0 | IF       | ID       | EX       | MEM      | WB
       | LOAD R0  | ---     | ---     | ---     | ---
Cycle    1 | IF       | ID       | EX       | MEM      | WB
       | LOAD R1  | LOAD R0  | ---     | ---     | ---
Cycle    2 | IF       | ID       | EX       | MEM      | WB
       | ADD     | LOAD R1  | LOAD R0  | ---     | ---
```

### Hardware Components

| Component | Attribute | Description |
|-----------|-----------|-------------|
| Clock | `cpu.clock` | Cycle counter with frequency |
| Pipeline | `cpu.pipeline` | 5-stage IF → ID → EX → MEM → WB |
| Hazard Unit | `cpu.hazard` | RAW detection, forwarding, stalls |
| L1 I-Cache | `cpu.icache` | Direct-mapped instruction cache |
| L1 D-Cache | `cpu.dcache` | Direct-mapped data cache |
| Branch Predictor | `cpu.bp` | 2-bit saturating counter predictor |
| Bus | `cpu.bus` | Shared system bus with arbitration |
| DMA | `cpu.dma` | Async memory-to-memory transfers |
| Interrupt Controller | `cpu.intc` | 8-line priority controller |
| VRAM Controller | `cpu.vram` | Bandwidth and scanline timing |
| Profiler | `cpu.profiler` | CPI, IPC, cache rates, branch accuracy |

### Cache and Branch Statistics

```python
cpu = CPU(realistic_timing=True)
cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])
cpu.run(verbose=False)

print(f"Cache hits: {cpu.dcache.hits}, misses: {cpu.dcache.misses}")
print(f"Branch accuracy: {cpu.bp.accuracy:.1%}")
print(f"CPI: {cpu.profiler.cpi:.2f}")
```

---

## Step 16: Tensor Accelerator

The Tensor Accelerator Coprocessor provides hardware-accelerated tensor operations integrated with the CPU ISA. It supports vector addition, matrix multiplication, dot products, and activation functions.

### Assembly-Level Tensor Operations

```asm
# tensor_demo.asm
start:
    # Load a 2x2 matrix from memory address 100
    TLOADW 100 2 2         # Load tensor, TID → R0

    # Load another 2x2 matrix from address 110
    TLOADW 110 2 2         # Load tensor, TID → R0

    # Add two vectors
    MOV R1 R0              # Save first TID
    TVECADD R2 R1 R0       # R2 = R1 + R0, result TID → R0

    # Matrix multiply
    TMATMUL R3 R1 R0       # R3 = R1 × R0, result TID → R0

    # Dot product
    TDOT R1 R0             # Scalar result → R0 (ternary encoded)

    HALT
```

### Python API

```python
from trinary.accelerator import TernaryTensorAccelerator, Opcode, Instruction

acc = TernaryTensorAccelerator()

# Load tensors
tid_a = acc.execute(Instruction(Opcode.TLOAD))
acc.memory.store(tid_a, [1, 0, 2, 1])  # 2x2 flat

tid_b = acc.execute(Instruction(Opcode.TLOAD))
acc.memory.store(tid_b, [2, 1, 0, 1])  # 2x2 flat

# Vector add
result = acc.execute(Instruction(Opcode.TVECADD, dest=0, src_a=tid_a, src_b=tid_b))
print(result)

# Dot product
result = acc.execute(Instruction(Opcode.TDOT, src_a=tid_a, src_b=tid_b))
print(result)
```

### Visualization

```python
from trinary.accelerator import render_simd_lanes, render_tensor_matrix, render_matmul

print(render_simd_lanes([2, 0, 1, 2]))
print(render_tensor_matrix([[2, 0], [0, 2]]))
print(render_matmul([[2, 0], [0, 2]], [[2, 0], [0, 2]], result=[[2, 0], [0, 2]]))
```

### Tensor ISA Opcodes

| Opcode | Format | Description |
|--------|--------|-------------|
| `TLOADW` | `TLOADW addr rows cols` | Load from CPU memory into accelerator tensor |
| `TSTOREW` | `TSTOREW tid addr` | Store accelerator tensor to CPU memory |
| `TVECADD` | `TVECADD dst src_a src_b` | Element-wise vector add |
| `TMATMUL` | `TMATMUL dst src_a src_b` | Matrix multiply |
| `TDOT` | `TDOT src_a src_b` | Dot product (scalar → R0) |
| `TACT` | `TACT tid type` | Activation (0 = step) |

---

## Step 17: Native C Backend

The native C backend accelerates ALU operations using a shared library (`libternary.so`). It auto-detects the library at import time and falls back to pure Python if unavailable.

### Building the Library

```sh
make -C src/trinary/native
```

This produces `src/trinary/libternary.so` containing C implementations of ternary arithmetic.

### Auto-Fallback Mechanism

```python
from trinary.native_backend import NATIVE_AVAILABLE, native_add, native_sub

if NATIVE_AVAILABLE:
    result = native_add(1, 2)  # 10 in ternary
    print(f"Native C add: {result}")
else:
    print("Native backend not available — using pure Python fallback")
```

The flag `NATIVE_AVAILABLE` is set at import time. The library is searched in multiple paths:

1. `src/trinary/libternary.so`
2. `src/trinary/native/libternary.so`
3. System library path

### Benchmark

Run a performance comparison between Python and native C:

```sh
python -m trinary.native_benchmark
```

Example output:
```
==================================================
TERNARY CPU — Native Backend Benchmark
Operations per test: 1,000,000
==================================================

Python add: 0.123s
Native add: 0.015s
Speedup: 8.2x

Python full_adder: 0.245s
Native full_adder: 0.019s
Speedup: 12.9x
```

### Exposed C Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `ternary_add` | `int ternary_add(int a, int b)` | Ternary digit addition |
| `ternary_sub` | `int ternary_sub(int a, int b)` | Ternary digit subtraction |
| `ternary_mul` | `int ternary_mul(int a, int b)` | Ternary digit multiplication |
| `ternary_div` | `int ternary_div(int a, int b)` | Ternary digit division |
| `ternary_full_adder` | `int ternary_full_adder(int a, int b, int carry_in, int* carry_out)` | Full adder with carry |

---

## Next Steps

- Read [instruction-set.md](instruction-set.md) for complete opcode reference
- Read [display-system.md](display-system.md) for display and OS internals
- Read [ARCHITECTURE.md](../ARCHITECTURE.md) for system architecture
- Read [ui-guide.md](ui-guide.md) for UI documentation
- Study the demo programs in `demo_programs.py`
- Write your own assembly programs and run them with the CPU
- Extend the OS shell with new commands
- Build your own games using the Fantasy Console SDK (`src/trinary/sdk/`)
- Explore the TAL compiler in `src/trinary/tal.py` and `test_snake_tal.py`
- Experiment with realistic timing: `CPU(realistic_timing=True)` and study pipeline, cache, branch predictor behavior
- Accelerate matrix workloads with tensor opcodes: `TLOADW`, `TVECADD`, `TMATMUL`, `TDOT`
- Build the native C backend and benchmark: `make -C src/trinary/native && python -m trinary.native_benchmark`
- Dive into the hardware simulation modules in `src/trinary/hardware/`
- Run the full test suite: `python -m pytest tests/ -v`

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

## Next Steps

- Read [instruction-set.md](instruction-set.md) for complete opcode reference
- Read [display-system.md](display-system.md) for display and OS internals
- Read [ARCHITECTURE.md](../ARCHITECTURE.md) for system architecture
- Read [ui-guide.md](ui-guide.md) for UI documentation
- Study the demo programs in `demo_programs.py`
- Write your own assembly programs and run them with the CPU
- Extend the OS shell with new commands

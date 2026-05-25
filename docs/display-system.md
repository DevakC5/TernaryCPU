# Display System, Keyboard & OS Shell

---

## 1. Memory-Mapped Display

### Overview

The Trinary CPU uses a memory-mapped text display. RAM addresses 200–255 form the Video RAM (VRAM), where each cell stores the ternary encoding of an ASCII character code.

### Specifications

| Property | Value |
|----------|-------|
| VRAM range | 200–255 (56 bytes) |
| Display resolution | 7 rows × 8 columns = 56 characters |
| Value format | Ternary ASCII code (e.g., `"10010"` = ASCII 84 = `'T'`) |
| Zero value | `"0"` → renders as space |
| Non-printable | chr(0)..chr(31) render as `.` |

### How Characters Are Stored

Characters are stored as ternary representations of their ASCII codes:

```python
# Write character 'T' (ASCII 84) to VRAM position 0:
memory.store(200, decimal_to_ternary(84))  # stores "10010"

# Read it back:
ternary_to_decimal(memory.load(200))  # → 84
chr(84)                               # → 'T'
```

### DisplayMemoryMap API

```python
from trinary.display import DisplayMemoryMap

display = DisplayMemoryMap()

# Read current display contents
chars = display.read_display(memory)
# Returns list of 56 characters (spaces for 0, dots for non-printable)

# Write text starting at offset
display.write_text(memory, "Hello", offset=0)

# Clear the display
display.clear(memory)
```

### Assembly Example

```asm
# Display character 'H' at VRAM position 0
LOAD R0 0              # Cursor position
LOAD R2 200            # VRAM base address
ADD R0 R2              # R0 = 200 (absolute VRAM address)
LOAD R1 2200           # R1 = d2t(ord('H')) = "2200" (ASCII 72)
STOREM R0 R1           # memory[200] = "2200"

# Or using STOREM with literal address:
LOAD R1 2200           # R1 = 'H'
STOREM 200 R1          # memory[200] = "2200"

# Load from VRAM:
LOADM 200 R0           # R0 = memory[200] = "2200"
```

### Assembly Character Constants

For convenience, character values can be generated in Python:

```python
def _t(ch):
    return d2t(ord(ch))

# Examples:
_t("T")   # → "10010"  (ternary for 84)
_t("r")   # → "11020"  (ternary for 114)
_t("!")   # → "1020"   (ternary for 33)
_t(" ")   # → "1012"   (ternary for 32)
```


## 2. OS Shell Display Driver

The OS shell (`os.py`) uses a cursor-based display driver written in assembly. The driver manages a cursor offset, character output, and scrolling.

### Cursor Memory

| Address | Purpose |
|---------|---------|
| 0 | Cursor offset (0–55), ternary encoded |

### Display Driver Entry Points

| Label | Input | Description |
|-------|-------|-------------|
| `vput` | R1 = character | Write char at cursor, advance cursor |
| `vinc` | — | Increment cursor by 1 |
| `vdec` | — | Decrement cursor by 1 |
| `cls` | — | Clear entire VRAM, reset cursor to 0 |

### vput Implementation

```
vput:
    LOADM 0 R0          # R0 = cursor
    cmp R0 with 55      # full?
    JZ  full_scroll     # if full, scroll first
    LOAD R2 VRB         # R2 = 200 (VRAM base)
    ADD R0 R2           # R0 = 200 + cursor
    STOREM R0 R1        # memory[cursor_pos] = char
    CALL vinc           # cursor += 1
    RET

full_scroll:
    CALL doscroll       # scroll up, cursor = 48
    LOADM 0 R0          # R0 = 48
    LOAD R2 VRB         # R2 = 200
    ADD R0 R2           # R0 = 248
    STOREM R0 R1        # write char at position 48 (start of last row)
    LOAD R0 49          # cursor = 49
    STOREM 0 R0
    RET
```

### Scrolling

When the cursor reaches position 55 (last VRAM cell), the display scrolls:

1. Copy addresses 201→200, 202→201, ..., 247→246 (shifts content up one row)
2. Clear addresses 248–255 (the last row, 8 characters)
3. Set cursor to 48 (first position of the now-empty last row)

```
Before scroll:              After scroll:
┌────────────────────┐      ┌────────────────────┐
│ 0: Trishell!>      │      │ 0: rishell!> HE    │  ← shifted up
│ 8:  HELP           │      │ 8: LP - CLS ME     │
│ 16:                │      │ 16: ... shifted    │
│ 24:                │      │ 24: ...             │
│ 32:                │      │ 32: ...             │
│ 40:                │      │ 40: ...here goes    │ ← last char scrolled off
│ 48: user input...  │      │ 48: _               │ ← cleared for new input
└────────────────────┘      └────────────────────┘
```


## 3. Keyboard Input

### Keyboard Buffer

| Address | Purpose |
|---------|---------|
| 260 | Keyboard buffer (ternary ASCII code) |

### Polling Protocol

The keyboard uses a simple polling protocol:

1. CPU reads memory address 260
2. If value is non-zero, a key is waiting
3. Process the key
4. Write `"0"` to address 260 to acknowledge

### OS Keyboard Driver

The OS main loop polls address 260 each cycle:

```asm
main:
    LOADM 260 R1       # Poll keyboard
    CMP R1 R3          # Compare with 0 (R3 is always 0)
    JZ main            # No key, keep polling
    STOREM 260 R3      # Acknowledge: clear buffer
    CALL kbd           # Process key
    JMP main           # Back to polling
```

### Key Processing (kbd)

The `kbd` routine handles character classification:

```
kbd:
    Compare R1 with backspace (127)
        → JZ kbsp (backspace handler)
    Compare R1 with newline (10) or CR (13)
        → JZ kent (enter handler)
    Otherwise:
        CALL bufadd      # Add char to input buffer
        Compare R1 with space
            → JZ main (don't echo spaces)
        CALL vput        # Echo char to display
        RET
```

### Key Injection (Python)

```python
os = OS()
os.boot()

# Inject a keypress
os.feed_key('H')              # Writes d2t(ord('H')) to memory[260]
os.feed_key(chr(10))           # Newline (Enter)
os.feed_key(chr(127))          # Backspace
```


## 4. OS Shell Architecture

### Overview

The OS shell (`os.py`) is a 342-instruction assembly program that boots into an interactive command prompt. It provides keyboard input, display output, line editing, and command execution.

### Memory Map

| Address | Purpose |
|---------|---------|
| 0 | Cursor offset (0–55) |
| 1–32 | Input buffer (characters) |
| 33 | Input buffer length |
| 34+ | OS working data |
| 200–255 | Video RAM |
| 260 | Keyboard buffer |

### Boot Sequence

```
start:
    LOAD R3 0          # R3 = 0 (convention: always zero)
    CALL cls           # Clear display
    CALL banner         # Print "Trishell!"
    CALL prompt        # Print "> "
```

### Main Loop

```
main:
    LOADM 260 R1       # Poll keyboard
    CMP R1 R3          # Any key?
    JZ main            # No → keep polling
    STOREM 260 R3      # Acknowledge
    CALL kbd           # Process key
    JMP main           # Loop
```

### Input Buffer

```
bufadd:  Append R1 to buffer[1..32], increment length
bufpop:  Remove last character, decrement length
bufclr:  Reset length to 0
```

### Command Parsing (exec)

The `exec` routine reads buffer[1] and dispatches:

```
exec:
    LOADM 1 R1           # First character
    'H' → check HELP...
    'M' → check MEMDUMP...
    'R' → check REGS/RUN...
    'C' → check CLS...
    else → print "?"
```

### Commands

| Command | Handler | Output |
|---------|---------|--------|
| `HELP` | `help` | Lists commands: "HELP - CLS MEMDUMP REGS RUN" |
| `MEMDUMP` | `mem` | Dumps memory addresses 0–7 |
| `REGS` | `regs` | Shows R0–R3 values |
| `RUN` | `run_` | Prints "RUN!" |
| `CLS` | `cls` | Clears screen, resets cursor |
| *(other)* | `unk` | Prints "?" |

### Key Handlers

```
kent (Enter):
    CALL vput           # Echo newline
    CALL exec           # Execute command
    CALL prompt         # Print "> "
    CALL bufclr         # Clear buffer
    RET

kbsp (Backspace, ASCII 127):
    CALL bufpop         # Remove from buffer
    CALL vdec           # Decrement cursor
    CALL vput           # Write space (erase char on screen)
    CALL vdec           # Decrement cursor again
    RET
```


## 5. Pixel Display

The `PixelDisplay` class provides a separate 27×27 pixel framebuffer for graphics.

### Specifications

| Property | Value |
|----------|-------|
| Width | 27 pixels |
| Height | 27 pixels |
| Colors | 0 = black, 1 = gray, 2 = white |
| Drawing | Bresenham line algorithm |

### API

```python
from trinary.display import PixelDisplay

display = PixelDisplay()

display.set_pixel(x, y, color)     # Set individual pixel
color = display.get_pixel(x, y)    # Read pixel (0 for OOB)
display.clear()                    # All black
display.draw_line(x0, y0, x1, y1, color)  # Bresenham line
buffer = display.get_buffer()      # 27×27 int matrix
```

### Demo Programs

```python
# Diagonal line
display2 = display(0, 0, 26, 26, 2)

# Checkerboard (3×3 blocks)
for i in range(9):
    for j in range(9):
        cx, cy = (i % 3) * 3, (j % 3) * 3
        color = ((i // 3) + (j // 3)) % 3
        for dx in range(3):
            for dy in range(3):
                display.set_pixel(cx + dx, cy + dy, color)

# Smiley face
for x in range(27):
    for y in range(27):
        dist = ((x-13)**2 + (y-13)**2) ** 0.5
        if dist < 12:
            display.set_pixel(x, y, 1)  # face
# Eyes, mouth...
```


## 6. Assembler Character Helpers

When writing OS-level assembly, these Python helpers generate character constants:

```python
from trinary.conversion import decimal_to_ternary as d2t

def _t(ch):
    return d2t(ord(ch))

# Common characters and their ternary values:
_t(" ")   # "1012"  (32)
_t("!")   # "1020"  (33)
_t(">")   # "2022"  (62)
_t("?")   # "2100"  (63)
_t("C")   # "2111"  (67)
_t("D")   # "2112"  (68)
_t("E")   # "2120"  (69)
_t("G")   # "2122"  (71)
_t("H")   # "2200"  (72)
_t("L")   # "2211"  (76)
_t("M")   # "2212"  (77)
_t("N")   # "2220"  (78)
_t("P")   # "2222"  (80)
_t("R")   # "10001" (82)
_t("S")   # "10002" (83)
_t("U")   # "10011" (85)

# Line drawing characters:
d2t(200)  # "21102" — VRAM base address
d2t(248)  # "100012" — last row start
d2t(256)  # "100111" — one past VRAM end
```

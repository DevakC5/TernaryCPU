# Display System, Keyboard & OS Shell

The Trinary CPU has two display subsystems that coexist:

| Layer | VRAM Range | Display | Keyboard | Used by |
|-------|-----------|---------|----------|---------|
| **Legacy** (text) | 200–255 | 7×8 chars via `DisplayMemoryMap` | 260 | `os.py`, `demo_programs.py`, `cpu.py` default |
| **SDK** (framebuffer) | 1000–5095 | 64×64 pixel `Framebuffer` | 9000–9001 | `os/` package, `sdk/`, `demo_games.py`, PyQt6 |

---

## 1. Legacy Text Display (200–255)

### Overview

Memory-mapped text display. RAM addresses 200–255 form the Video RAM (VRAM), where each cell stores the ternary encoding of an ASCII character code.

### Specifications

| Property | Value |
|----------|-------|
| VRAM range | 200–255 (56 bytes) |
| Display resolution | 7 rows × 8 columns = 56 characters |
| Value format | Ternary ASCII code (e.g., `"10010"` = ASCII 84 = `'T'`) |
| Zero value | `"0"` → renders as space |
| Non-printable | chr(0)..chr(31) render as `.` |

### DisplayMemoryMap API

```python
from trinary.display import DisplayMemoryMap

display = DisplayMemoryMap()

chars = display.read_display(memory)
display.write_text(memory, "Hello", offset=0)
display.clear(memory)
```

### Assembly Example

```asm
LOAD R1 2200           # R1 = 'H' (ternary for ASCII 72)
STOREM 200 R1          # memory[200] = "2200"
LOADM 200 R0           # R0 = memory[200] = "2200"
```

### Character Constants

```python
from trinary.conversion import decimal_to_ternary as d2t
d2t(ord('H'))   # "2200"  (72)
d2t(ord('e'))   # "11020" (101)
```

---

## 2. SDK Framebuffer Display (1000–5095)

The SDK provides a 64×64 pixel framebuffer with a 9-color palette, designed for game graphics.

### Specifications

| Property | Value |
|----------|-------|
| VRAM range | 1000–5095 (4096 cells) |
| Resolution | 64 × 64 pixels |
| Colors | 9 (black, dark gray, white, red, green, blue, yellow, cyan, magenta) |
| Pixel addressing | `address = 1000 + y * 64 + x` |

### Color Palette

| Index | Name | RGB |
|-------|------|-----|
| 0 | Black | (0, 0, 0) |
| 1 | Dark gray | (64, 64, 64) |
| 2 | White | (200, 200, 200) |
| 3 | Red | (200, 40, 40) |
| 4 | Green | (40, 180, 40) |
| 5 | Blue | (40, 80, 220) |
| 6 | Yellow | (200, 200, 40) |
| 7 | Cyan | (40, 200, 200) |
| 8 | Magenta | (200, 40, 200) |

### Assembly Example

```asm
# Set pixel at (10, 5) to red (color 3)
# address = 1000 + 5*64 + 10 = 1330
LOAD R0 3
STOREM 1330 R0

# Read pixel
LOADM 1330 R1
```

### Python API

```python
from trinary.display.framebuffer import Framebuffer

fb = Framebuffer()
fb.set_pixel(x, y, color)
fb.get_buffer()       # 64×64 int matrix
fb.clear()
```

### Memory Hooks

```python
memory.register_write_hook(1000, 5095, callback)
```

---

## 3. Keyboard Input

### Legacy Keyboard (address 260)

| Address | Purpose |
|---------|---------|
| 260 | Keyboard buffer (ternary ASCII code) |

Polling protocol:
1. CPU reads address 260
2. If non-zero, key is waiting
3. Process key
4. Write `"0"` to 260 to acknowledge

```asm
main:
    LOADM 260 R1       # Poll keyboard
    CMP R1 R3          # Compare with 0
    JZ main            # No key
    STOREM 260 R3      # Acknowledge
    CALL kbd           # Process key
    JMP main
```

### SDK Keyboard (addresses 9000–9001)

| Address | Purpose |
|---------|---------|
| 9000 | Key data register (ASCII code as ternary) |
| 9001 | Key status register (1 = key waiting, 0 = none) |

Used by the Fantasy Console SDK and modern OS. Supports 8-button mapping:
LEFT/RIGHT/UP/DOWN/A/B/START/SELECT.

```python
from trinary.sdk.api import btn, btnp

if btn("LEFT"):    x -= 1
if btnp("A"):      jump()
```

---

## 4. Legacy OS Shell Display Driver

The legacy OS shell (`os.py`) uses a cursor-based display driver written in assembly.

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

### Scrolling

When the cursor reaches position 55 (last VRAM cell), the display scrolls:
1. Copy addresses 201→200, 202→201, ..., 247→246
2. Clear addresses 248–255 (last row)
3. Set cursor to 48

---

## 5. Legacy OS Shell Architecture

### Boot Sequence

```
start:
    LOAD R3 0          # R3 = 0 (convention)
    CALL cls           # Clear display
    CALL banner        # Print "Trishell!"
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
    JMP main
```

### Commands

| Command | Handler | Output |
|---------|---------|--------|
| `HELP` | `help` | Lists commands |
| `MEMDUMP` | `mem` | Dumps memory addresses 0–7 |
| `REGS` | `regs` | Shows R0–R3 values |
| `RUN` | `run_` | Prints "RUN!" |
| `CLS` | `cls` | Clears screen, resets cursor |

### Key Injection (Python)

```python
os = OS()
os.boot()
os.feed_key('H')
os.feed_key(chr(10))    # Enter
os.feed_key(chr(127))   # Backspace
```

---

## 6. Framebuffer Display Architecture

### Files

| File | Purpose |
|------|---------|
| `display/constants.py` | VRAM addresses, display dimensions |
| `display/palette.py` | 9-color palette (RGB tuples) |
| `display/framebuffer.py` | 64×64 framebuffer with dirty tracking |
| `display/display_controller.py` | Bridges CPU memory ↔ framebuffer |
| `display/display_widget.py` | PyQt6 rendering widget (retro aesthetic) |
| `display/keyboard.py` | Memory-mapped keyboard I/O |

### Retro Aesthetic

The display widget renders at 8× pixel scale with optional scanlines and pixel-grid lines. Uses nearest-neighbour filtering (no blur). Auto-refresh at ~30 FPS.

### Pixel Display (Legacy Graphics)

The `PixelDisplay` class provides a separate 27×27 pixel framebuffer for legacy graphics demos.

```python
from trinary.display import PixelDisplay

display = PixelDisplay()
display.set_pixel(x, y, color)
display.draw_line(x0, y0, x1, y1, color)
buffer = display.get_buffer()      # 27×27 int matrix
```

---

## 7. Assembler Character Helpers

```python
from trinary.conversion import decimal_to_ternary as d2t

def _t(ch):
    return d2t(ord(ch))

_t("H")   # "2200"  (72)
_t("e")   # "11020" (101)
_t(" ")   # "1012"  (32)
_t("!")   # "1020"  (33)
```

Common VRAM addresses:
```python
d2t(200)  # "21102" — VRAM base
d2t(248)  # "100012" — last row start
d2t(256)  # "100111" — one past VRAM end
```

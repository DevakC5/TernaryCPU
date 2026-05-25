# Graphics System — TernaryVM

The display system turns the ternary CPU into a visual retro computer with
a memory-mapped framebuffer, keyboard input, and a PyQt6 rendering widget.

## Architecture

```
CPU (assembly program)
    │
    ▼  STOREM / LOADM instructions
Memory (RAM)
    │
    ├── 1000–5095  64×64 VRAM (pixel color values 0–8)
    ├── 9000       Keyboard data register
    └── 9001       Keyboard status register
    │
    ▼  DisplayController sync
Framebuffer (Python)
    │
    ▼  DisplayWidget (PyQt6)
Screen
```

## VRAM Layout

| Region | Addresses | Size | Purpose |
|---|---|---|---|
| Text display | 200–255 | 56 chars | Legacy ASCII text (backward compatible) |
| Pixel display | 200–255 | 56 bytes | Legacy 7×8 character display (backward compatible) |
| **Framebuffer VRAM** | **1000–5095** | **4096 cells** | **64×64 pixel framebuffer** |
| Keyboard data | 9000 | 1 cell | Last key pressed (ASCII code as ternary) |
| Keyboard status | 9001 | 1 cell | 1 = key waiting, 0 = no key |

### Pixel addressing

```
address = VRAM_BASE + y * WIDTH + x
        = 1000      + y * 64      + x
```

Pixel (0, 0) → address 1000
Pixel (1, 0) → address 1001
Pixel (0, 1) → address 1064
Pixel (63, 63) → address 5095

Each address stores a ternary string of the color index (0–8).

## Color palette (ternary-inspired)

| Index | Name    | RGB             |
|-------|---------|-----------------|
| 0     | Black   | (0, 0, 0)       |
| 1     | Dark gray | (64, 64, 64)  |
| 2     | White   | (200, 200, 200) |
| 3     | Red     | (200, 40, 40)   |
| 4     | Green   | (40, 180, 40)   |
| 5     | Blue    | (40, 80, 220)   |
| 6     | Yellow  | (200, 200, 40)  |
| 7     | Cyan    | (40, 200, 200)  |
| 8     | Magenta | (200, 40, 200)  |

## Programming the display

### Setting a pixel (assembly)

```asm
# Set pixel at (10, 5) to red (color 3)
# address = 1000 + 5*64 + 10 = 1330
LOAD R0 3             # color value
STOREM 1330 R0        # write to VRAM
```

### Reading a pixel (assembly)

```asm
LOADM 1330 R1         # read color value from VRAM
```

### Clearing the screen

```asm
# Fill VRAM with zeros
LOAD R0 0             # color 0 = black
LOAD R1 1000          # start address
LOAD R2 3             # increment (1 in ternary)
LOAD R3 5095          # end address
loop:
  STOREM R1 R0
  ADD R1 R2
  CMP R1 R3
  JNZ loop
  HALT
```

### Keyboard input (assembly)

```asm
# Poll keyboard
LOADM 9000 R0         # read key code
LOAD R1 0
CMP R0 R1
JZ no_key             # no key pressed (zero)
# process key in R0 ...
no_key:
# ...
```

## Memory hooks

Python code can register write hooks on memory ranges. When the CPU
stores to a VRAM address, the hook fires automatically, keeping the
framebuffer in sync.

```python
memory.register_write_hook(VRAM_BASE, VRAM_END, my_callback)
```

## Files

| File | Purpose |
|---|---|
| `display/constants.py` | VRAM addresses, display dimensions |
| `display/palette.py` | 9-color palette (RGB tuples) |
| `display/framebuffer.py` | 64×64 framebuffer with dirty tracking |
| `display/display_controller.py` | Bridges CPU memory ↔ framebuffer |
| `display/display_widget.py` | PyQt6 rendering widget (retro aesthetic) |
| `display/keyboard.py` | Memory-mapped keyboard IO |
| `demo_graphics.py` | Graphics demo programs |

## Retro aesthetic

The display widget renders at 8× pixel scale with optional scanlines
and subtle pixel-grid lines for a retro emulator look. It uses
nearest-neighbour filtering (no blur). Auto-refresh runs at ~30 FPS.

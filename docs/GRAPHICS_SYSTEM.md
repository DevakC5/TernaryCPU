# Graphics System — Trinary

The display system turns the ternary CPU into a visual retro computer with a memory-mapped framebuffer, keyboard input, and PyQt6 rendering widgets. Two display subsystems coexist — legacy text mode and SDK framebuffer mode.

## Architecture

```
CPU (assembly program / SDK game)
    │
    ▼  STOREM / LOADM / SDK API
Memory (RAM)
    │
    ├── 200–255    Legacy VRAM (7×8 text, 56 bytes)
    ├── 260        Legacy keyboard buffer
    ├── 1000–5095  SDK VRAM (64×64 pixels, 4096 cells)
    ├── 9000       SDK keyboard data register
    └── 9001       SDK keyboard status register
    │
    ▼  DisplayController / Memory Hooks
Framebuffer (Python)
    │
    ▼  PyQt6 DisplayWidget / Console
Screen
```

## VRAM Layout

| Region | Addresses | Size | Purpose |
|--------|-----------|------|---------|
| Text display | 200–255 | 56 chars | Legacy ASCII text (backward compatible) |
| **Framebuffer VRAM** | **1000–5095** | **4096 cells** | **64×64 pixel framebuffer** |
| Keyboard (legacy) | 260 | 1 cell | ASCII code (ternary) |
| Keyboard (SDK) | 9000–9001 | 2 cells | Data + status registers |

### Pixel Addressing (Framebuffer)

```
address = VRAM_BASE + y * WIDTH + x
        = 1000      + y * 64      + x
```

Pixel (0, 0) → address 1000
Pixel (1, 0) → address 1001
Pixel (0, 1) → address 1064
Pixel (63, 63) → address 5095

## Color Palette

| Index | Name    | RGB |
|-------|---------|-----|
| 0     | Black   | (0, 0, 0) |
| 1     | Dark gray | (64, 64, 64) |
| 2     | White   | (200, 200, 200) |
| 3     | Red     | (200, 40, 40) |
| 4     | Green   | (40, 180, 40) |
| 5     | Blue    | (40, 80, 220) |
| 6     | Yellow  | (200, 200, 40) |
| 7     | Cyan    | (40, 200, 200) |
| 8     | Magenta | (200, 40, 200) |

## Programming the Display

### Setting a Pixel (Assembly)

```asm
# Set pixel at (10, 5) to red (color 3)
# address = 1000 + 5*64 + 10 = 1330
LOAD R0 3
STOREM 1330 R0
```

### Reading a Pixel (Assembly)

```asm
LOADM 1330 R1
```

### Clearing the Screen (Assembly)

```asm
LOAD R0 0             # color 0 = black
LOAD R1 1000          # start address
LOAD R2 3             # increment (1 in ternary: "1")
LOAD R3 5095          # end address
loop:
  STOREM R1 R0
  ADD R1 R2
  CMP R1 R3
  JNZ loop
  HALT
```

### Keyboard Input (Assembly, SDK Mode)

```asm
LOADM 9000 R0         # read key code
LOAD R1 0
CMP R0 R1
JZ no_key             # no key pressed
# process key in R0 ...
no_key:
```

### Python API (SDK)

```python
from trinary.display.framebuffer import Framebuffer

fb = Framebuffer()
fb.set_pixel(x, y, color)
pixel = fb.get_pixel(x, y)
fb.clear()
buffer = fb.get_buffer()     # 64×64 int matrix
```

### Memory Hooks

Python code can register write hooks on memory ranges. When the CPU stores to a VRAM address, the hook fires automatically, keeping the framebuffer in sync.

```python
memory.register_write_hook(1000, 5095, my_callback)
```

## Display Package Structure

```
display/
├── __init__.py            # Exports: DisplayMemoryMap, PixelDisplay, Framebuffer
├── constants.py           # VRAM addresses, display dimensions
├── palette.py             # 9-color palette (RGB tuples)
├── text.py                # DisplayMemoryMap (7×8 char grid, legacy)
├── framebuffer.py         # 64×64 framebuffer with dirty tracking
├── display_controller.py  # Bridges CPU memory ↔ framebuffer
├── display_widget.py      # PyQt6 rendering widget (retro aesthetic)
└── keyboard.py            # Memory-mapped keyboard I/O
```

## Legacy Pixel Display (27×27)

The `PixelDisplay` class provides a separate 27×27 pixel framebuffer for legacy graphics demos (not memory-mapped).

| Property | Value |
|----------|-------|
| Width | 27 pixels |
| Height | 27 pixels |
| Colors | 0 = black, 1 = gray, 2 = white |
| Drawing | Bresenham line algorithm |

```python
from trinary.display import PixelDisplay

display = PixelDisplay()
display.set_pixel(x, y, color)
display.draw_line(x0, y0, x1, y1, color)
buffer = display.get_buffer()
```

## Retro Aesthetic (PyQt6)

The display widget renders at 8× pixel scale with optional scanlines and subtle pixel-grid lines for a retro emulator look. Uses nearest-neighbour filtering (no blur). Auto-refresh runs at ~30 FPS.

### Display Widget Files

| File | Purpose |
|------|---------|
| `display_widget.py` | PyQt6 rendering widget |
| `screen_view.py` | Legacy 27×27 pixel widget |
| `game_window.py` | SDK game display window |

## Demo Graphics Programs

```bash
python -m trinary.demo_graphics     # pixel test, color bars, bouncing box
python -m trinary.demo_games pong   # SDK game demos
```

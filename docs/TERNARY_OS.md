# TernaryOS — Tiny Operating Environment

TernaryOS is a minimal operating environment that runs inside the ternary
computer simulator. It provides a retro-style terminal shell with a
pixel-based text renderer, a command system, graphics demos, and a
program loader.

## Architecture

```
┌─────────────────────────────────────┐
│           Kernel (kernel.py)        │  ← main loop, boot
├─────────────────────────────────────┤
│   Shell (shell.py)                  │  ← command dispatch
│   ├── commands.py                   │  ← HELP, CLS, MEM, etc.
│   └── program_loader.py             │  ← load assembly programs
├─────────────────────────────────────┤
│   Terminal (terminal.py)            │  ← input buffer, history
│   └── TextRenderer (text_renderer)  │  ← 8×8 bitmap font → framebuffer
├─────────────────────────────────────┤
│   Syscalls (syscalls.py)            │  ← print, clear, draw, read key
├─────────────────────────────────────┤
│   Framebuffer (64×64)               │  ← VRAM at 1000–5095
│   CPU + Memory                      │  ← existing simulator
└─────────────────────────────────────┘
```

## Boot flow

1. `Kernel.boot()` → calls `boot_sequence()`
2. Clear framebuffer (all black)
3. Draw boot banner: "TERNARY OS v0.1" in red
4. Show system info: "64x64 DISP READY", "256W RAM", "TCPU-4"
5. Separator line
6. Cursor ready for input

## Terminal layout

The 64×64 pixel framebuffer is divided into an 8×8 character grid:

- **8 columns** × **8 rows** = 64 character cells
- Each character is 8×8 pixels using a bitmap font
- Font has all uppercase letters, digits 0–9, and common punctuation
- Scrolling shifts rows up when cursor reaches bottom

## Commands

| Command | Description |
|---|---|
| `HELP` | List all available commands |
| `CLS` | Clear the terminal screen |
| `MEM [addr]` | Dump 16 words of memory from optional address |
| `REGS` | Show CPU register values (R0–R3) |
| `CLEAR` | Reset all memory to zero |
| `ABOUT` | Display system information |
| `DEMO <name>` | Run a graphics demo (PIXEL, COLORS, BOUNCE, NOISE) |
| `RUN <name>` | Load and execute an assembly demo program |
| `HALT` | Stop the CPU |
| `CPU` | Show CPU status (PC, cycles, etc.) |

## Keyboard input

Memory-mapped keyboard at address 9000 / 9001:

- `mem[9000]` = last key pressed as ternary ASCII code
- `mem[9001]` = 1 if key is waiting, 0 if no key

The kernel's `tick()` method polls this address, processes the key
through the terminal (handles backspace, enter, arrow keys), and
dispatches completed command lines to the shell.

## Syscall API (Python)

```python
syscalls.print_text(text, color=None)     # write text at cursor
syscalls.println(text, color=None)         # write text + newline
syscalls.clear_screen()                     # clear framebuffer
syscalls.draw_pixel(x, y, color)            # set single pixel
syscalls.read_key()                          # read keyboard buffer
syscalls.sleep(seconds)                      # sleep stub
```

## Font

The 8×8 bitmap font is stored in `text_renderer.py` as hex bitmasks:

```
"A": [0x18, 0x24, 0x42, 0x7E, 0x42, 0x42, 0x42, 0x00]
```

Each byte is one row; bits 0–6 represent columns (MSB = leftmost).

## Adding a command

```python
from trinary.os.commands import register

def cmd_hello(args, syscalls, kernel):
    syscalls.println("Hello from TernaryOS!")

register("HELLO", "Say hello", cmd_hello)
```

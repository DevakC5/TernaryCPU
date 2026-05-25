# TernaryOS — Dual Operating Environment

TernaryOS provides two operating system paths that coexist in the codebase:

| Path | File | Display | Keyboard | Type |
|------|------|---------|----------|------|
| **Legacy** | `os.py` | Text (7×8, VRAM 200–255) | addr 260 | Single-file TTY shell |
| **SDK** | `os/` package | Framebuffer (64×64, VRAM 1000–5095) | addr 9000–9001 | Modular Kernel/Shell/Terminal |

---

## Legacy OS (`os.py`)

A 342-instruction assembly program that boots into an interactive command shell with keyboard echo, line editing, display scrolling, and 5 commands.

```sh
python -m trinary.os
```

### Memory Map

| Address | Purpose |
|---------|---------|
| 0 | Cursor offset (0–55) |
| 1–32 | Input buffer (characters) |
| 33 | Input buffer length |
| 200–255 | Video RAM |
| 260 | Keyboard buffer |

### Commands

| Command | Description |
|---------|-------------|
| `HELP` | Lists available commands |
| `CLS` | Clears the display |
| `REGS` | Shows register values |
| `MEMDUMP` | Dumps first 8 memory addresses |
| `RUN` | Prints "RUN!" (placeholder) |

### Architecture

```
start → cls → banner → prompt → main loop
                                   ↓
                             poll keyboard (addr 260)
                                   ↓
                             kbd (classify key)
                              ↙    ↓    ↘
                          kbsp   kent   bufadd + vput
                          (bsp)  (enter) (echo)
                                   ↓
                                 exec
                              ↙   ↓   ↘
                          HELP  REGS  CLS ...
```

---

## SDK OS (`os/` package)

A modular operating environment with a retro-style terminal, command system, graphics demos, and program loader — all using the 64×64 pixel framebuffer.

```sh
python -m trinary.ui.app          # PyQt6 launcher includes SDK OS
```

### Architecture

```
┌─────────────────────────────────────┐
│           Kernel (kernel.py)        │  ← main loop, boot
├─────────────────────────────────────┤
│   Shell (shell.py)                  │  ← command dispatch
│   ├── commands.py                   │  ← HELP, CLS, MEM, etc.
│   └── program_loader.py             │  ← load assembly programs
├─────────────────────────────────────┤
│   Terminal (terminal.py)            │  ← input buffer, history
│   └── TextRenderer (text_renderer)  │  ← 8×8 bitmap font
├─────────────────────────────────────┤
│   Syscalls (syscalls.py)            │  ← print, clear, draw, read key
├─────────────────────────────────────┤
│   Framebuffer (64×64)               │  ← VRAM at 1000–5095
│   CPU + Memory                      │  ← existing simulator
└─────────────────────────────────────┘
```

### Boot Flow

1. `Kernel.boot()` → `boot_sequence()`
2. Clear framebuffer (all black)
3. Draw boot banner: "TERNARY OS v0.1" in red
4. Show system info: "64x64 DISP READY", "256W RAM", "TCPU-4"
5. Cursor ready for input

### Commands

| Command | Description |
|---------|-------------|
| `HELP` | List all available commands |
| `CLS` | Clear the terminal screen |
| `MEM [addr]` | Dump 16 words of memory |
| `REGS` | Show CPU register values |
| `CLEAR` | Reset all memory to zero |
| `ABOUT` | Display system information |
| `DEMO <name>` | Run a graphics demo |
| `RUN <name>` | Load and execute assembly |
| `HALT` | Stop the CPU |
| `CPU` | Show CPU status (PC, cycles) |

### Terminal Layout

64×64 pixel framebuffer divided into 8×8 character grid:
- **8 columns** × **8 rows** = 64 character cells
- Each character is 8×8 pixels using a bitmap font
- Font has all uppercase letters, digits 0–9, and common punctuation
- Scrolling shifts rows up when cursor reaches bottom

### Font

The 8×8 bitmap font is stored in `text_renderer.py` as hex bitmasks:
```
"A": [0x18, 0x24, 0x42, 0x7E, 0x42, 0x42, 0x42, 0x00]
```
Each byte is one row; bits 0–6 represent columns (MSB = leftmost).

### Syscall API

```python
syscalls.print_text(text, color=None)
syscalls.println(text, color=None)
syscalls.clear_screen()
syscalls.draw_pixel(x, y, color)
syscalls.read_key()
syscalls.sleep(seconds)
```

### Adding a Command

```python
from trinary.os.commands import register

def cmd_hello(args, syscalls, kernel):
    syscalls.println("Hello from TernaryOS!")

register("HELLO", "Say hello", cmd_hello)
```

---

## Keyboard Input

### Legacy (address 260)

Polled by the legacy OS. Value is ternary ASCII code. Write `"0"` to acknowledge.

### SDK (addresses 9000–9001)

| Address | Purpose |
|---------|---------|
| 9000 | Last key pressed (ternary ASCII code) |
| 9001 | 1 = key waiting, 0 = no key |

The SDK kernel's `tick()` method polls address 9001, processes keys through the terminal (handles backspace, enter), and dispatches completed command lines to the shell.

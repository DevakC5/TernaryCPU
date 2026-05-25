# PyQt6 Desktop UI — Visual Simulator Guide

The Trinary Visual Simulator is a full-featured desktop debugger for the ternary CPU, built with PyQt6. It provides real-time visibility into every aspect of CPU state.

---

## Quick Start

```sh
pip install pyqt6
python -m trinary.ui.app
```

---

## Layout

```
┌────────────────────────────────────────────────────────────────┐
│  [Demo: ▼] [Assemble] [▶ Run] [⤵ Step Into] [⤴ Step Over]   │
│  [↺ Reset] [⏸ Pause] [▶ Continue]      Cycles: 0            │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┬────────────────────────────────┐     │
│  │                      │  Registers:                    │     │
│  │  Assembly Editor     │  R0: 0  R1: 0  R2: 0  R3: 0  │     │
│  │  (syntax highlight)  │  PC: 0   SP: 255              │     │
│  │  (breakpoints)       │  Flags: Z[ ] E[ ] G[ ] L[ ]  │     │
│  │                      ├────────────────────────────────┤     │
│  │  Machine Code View   │  Memory (0..511):             │     │
│  │  (ternary opcodes)   │  │Addr│Value│                  │     │
│  │                      │  │  0 │  0  │                  │     │
│  │                      │  │  1 │  0  │                  │     │
│  │                      ├────────────────────────────────┤     │
│  │                      │  Stack (SP→):                 │     │
│  │                      │  [255] 0                       │     │
│  │                      │  [254] 0                       │     │
│  │                      ├────────────────────────────────┤     │
│  │                      │  Display:                      │     │
│  │                      │  ┌──────────────────────┐      │     │
│  │                      │  │  27×27 pixel grid    │      │     │
│  │                      │  └──────────────────────┘      │     │
│  └──────────────────────┴────────────────────────────────┘     │
├────────────────────────────────────────────────────────────────┤
│  Execution Trace:                                              │
│  │Step│ PC│ Instruction     │ R0│R1│R2│R3│Flags  │            │
│  │  0 │ 0 │ LOAD R0 10     │ 0 │ 0│ 0│ 0│Z:0...│            │
│  │  1 │ 1 │ LOAD R1 12     │10 │ 0│ 0│ 0│Z:0...│            │
│  │  2 │ 2 │ ADD R0 R1      │10 │12│ 0│ 0│Z:0...│            │
│  │  3 │ 3 │ HALT           │22 │12│ 0│ 0│Z:1...│            │
└────────────────────────────────────────────────────────────────┘
```

---

## Panels

### 1. Assembly Editor (`assembler_editor.py`)

A full-featured source code editor with:

**Syntax Highlighting:**
| Token | Color |
|-------|-------|
| Opcodes (ADD, SUB, LOAD, ...) | Cyan |
| Registers (R0–R3) | Yellow |
| Labels | Purple |
| Comments (# / ;) | Dim green |
| Numbers | White |

**Breakpoints:** Click in the gutter (line number area) to toggle a red dot breakpoint. Breakpoints pause execution before the instruction executes.

**Current Line:** A yellow arrow in the gutter marks the current PC.

**Features:**
- `get_source()` — returns current editor text
- `highlight_line(line)` — scrolls to and highlights a line
- `toggle_breakpoint(line)` — programmatic breakpoint toggle
- `get_breakpoints()` — returns set of line numbers with breakpoints

### 2. Machine Code Viewer (`machine_code_view.py`)

Displays the assembled machine code in a table:

| Column | Content |
|--------|---------|
| # | Instruction address |
| Assembly | Original assembly instruction |
| Machine Code | Ternary opcode string |

Highlights the current line as the CPU executes.

### 3. Register Panel (`register_view.py`)

Shows all CPU state registers:

- **R0–R3**: Current register values. Flashes green briefly when the value changes.
- **PC**: Program counter
- **SP**: Stack pointer
- **Flags**: Four indicators (ZERO, EQUAL, GREATER, LESS) — active style when True, dim when False.

### 4. Memory Viewer (`memory_view.py`)

A 512-row table showing memory contents:

| Column | Content |
|--------|---------|
| Address | Memory address (0–511) |
| Value | Ternary string stored at that address |

**Access Tracking:**
- Green background: recently written address
- Blue background: recently read address
- Colors fade after a configurable timeout

**Current PC Highlight:** The row corresponding to the current PC address is highlighted.

### 5. Stack Viewer (`stack_view.py`)

Displays the memory stack (addresses SP+1 to 255):

- Shows each stack slot with its address and value
- Labels the SP position with a pointer indicator
- Shows item count

### 6. Execution Trace (`execution_trace.py`)

A running log of all executed instructions:

| Column | Content |
|--------|---------|
| Step | Sequential step number |
| PC | Address of the instruction |
| Instruction | Decompiled assembly |
| R0–R3 | Register state after execution |
| Flags | Flag state after execution |

Auto-scrolls to the most recent entry.

### 7. Pixel Display (`screen_view.py`)

A 27×27 pixel framebuffer rendered as a 324×324 pixel widget:

- Each "pixel" is 12×12 screen pixels
- Colors: black (0), gray (1), white (2)
- Draws using QPainter

**Keyboard Capture:** When the pixel display has focus, key presses are captured and written to memory address 260 (the keyboard buffer), allowing the OS shell to receive input.

### 8. Controls Toolbar (`controls.py`)

| Control | Function |
|---------|----------|
| Demo selector (combo box) | Load 13 pre-written demo programs |
| Assemble | Run the assembler on the editor content |
| Run (▶) | Execute to completion (or until breakpoint/halt) |
| Step Into (⤵) | Execute one instruction |
| Step Over (⤴) | Step, or if CALL, run until return |
| Reset (↺) | Reset CPU to initial state |
| Pause (⏸) | Pause running program |
| Continue (▶) | Resume after pause |
| Cycle counter | Shows total cycles executed |

---

## Signal Flow

```
User types in editor
    → Assemble button
        → Assembler.assemble(source)
            → (program, labels)
        → Machine.encode_instruction() for each instruction
            → (machine_code list)
        → Update MachineCodeView
        → CPU.load_program(program)

User clicks Run
    → CPU.run()
        → loop: CPU.step()
            → Update RegisterView
            → Update MemoryView
            → Update StackView
            → Update ExecutionTrace
            → Check breakpoints → pause
            → Update MachineCodeView highlight
            → Process UI events (keep responsive)

User clicks Step Into
    → CPU.step()
    → Update all views

User types in ScreenView
    → Write d2t(ord(char)) to memory[260]
    → OS main loop in CPU polls 260
```

---

## Theme

The UI uses a dark cyberpunk theme defined in `styles.py`. Key colors:

```css
/* Background */
background-color: #0a0a0f;

/* Text */
color: #00ff88;

/* Opcodes in editor */
color: #00ffff;  /* cyan */

/* Registers */
color: #ffff00;  /* yellow */

/* Labels */
color: #aa66ff;  /* purple */

/* Comments */
color: #004400;  /* dim green */

/* Buttons */
background-color: #1a1a2e;
color: #00ff88;
```

---

## 13 Demo Programs

The demo selector includes these programs:

| Demo | Description |
|------|-------------|
| Countdown | Counts 5→0 with loop |
| Fibonacci | Computes F(3)=2 |
| Factorial | Computes 3! = 6 |
| Sum 1 to N | Sums 1+2+3+4+5 |
| Calculator | ((10+5)-3)+2 = 14 |
| Subroutine Average | CALL/RET with add_routines |
| Logical Operations | AND, OR, NOT demos |
| Comparison | CMP + conditional jumps |
| Stack Operations | PUSH/POP visualization |
| Timer Interrupt | Periodic timer firing |
| Pixel Diagonal | Diagonal lines on framebuffer |
| Pixel Checkerboard | 3×3 checkerboard |
| Pixel Smiley | Ternary smiley face |
| Keyboard Echo | Type and see characters |
| CPU Display Demo | End-to-end display demo |

---

## Extending the UI

### Adding a New Panel

```python
# In main_window.py:
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class MyPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("My Panel"))
    
    def update_state(self, cpu):
        """Called after each CPU step."""
        pass

# In MainWindow.__init__:
self.my_panel = MyPanel()
# Add to an existing splitter or layout
```

### Adding a New Demo

```python
# In ui/demos.py:
DEMOS["My New Demo"] = """
    LOAD R0 10
    LOAD R1 12
    ADD R0 R1
    HALT
"""
```

### Customizing the Theme

Edit `styles.py` to change colors, fonts, and widget styling.

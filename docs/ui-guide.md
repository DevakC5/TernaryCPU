# PyQt6 Desktop UI — Visual Simulator Guide

The Trinary Visual Simulator is a full-featured desktop debugger for the ternary CPU, built with PyQt6. It provides real-time visibility into every aspect of CPU state — from registers and memory to pipeline stages and bus transactions.

---

## Quick Start

```sh
pip install pyqt6
python -m trinary.ui.app
```

---

## Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ [Demo: ▼] [Assemble] [▶ Run] [⤵ Step] [↺ Reset] [⏸ Pause]    │
├─────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────┬──────────────────────────────┐       │
│ │                        │  Inspector: R0–R3, PC, SP   │       │
│ │  Assembly Editor       │  Flags: Z[ ] E[ ] G[ ] L[ ]│       │
│ │  (syntax highlight)    ├──────────────────────────────┤       │
│ │  (breakpoints)         │  Memory (0..511):            │       │
│ │                        ├──────────────────────────────┤       │
│ │  Machine Code View     │  Stack Viewer                │       │
│ │  (ternary opcodes)     ├──────────────────────────────┤       │
│ │                        │  Pipeline Widget             │       │
│ │                        │  Cache Widget                │       │
│ │                        │  Branch Widget               │       │
│ │                        │  Bus Widget                  │       │
│ │                        ├──────────────────────────────┤       │
│ │                        │  Performance Dashboard       │       │
│ │                        │  Timeline / Waveform Viewer  │       │
│ │                        ├──────────────────────────────┤       │
│ │                        │  Game Window (SDK)           │       │
│ └────────────────────────┴──────────────────────────────┘       │
├──────────────────────────────────────────────────────────────────┤
│  Execution Trace: Step│PC│Instruction│R0│R1│R2│R3│Flags         │
└──────────────────────────────────────────────────────────────────┘
```

---

## Panels

### 1. Assembly Editor (`assembler_editor.py`)

**Syntax Highlighting:**
| Token | Color |
|-------|-------|
| Opcodes (ADD, SUB, LOAD, ...) | Cyan |
| Registers (R0–R3) | Yellow |
| Labels | Purple |
| Comments (# / ;) | Dim green |
| Numbers | White |

**Breakpoints:** Click in the gutter to toggle. Breakpoints pause execution before the instruction executes. A yellow arrow marks the current PC.

### 2. Machine Code Viewer

Displays a table with columns: `#` (address), `Assembly` (original instruction), `Machine Code` (ternary opcode string). Highlights the current line.

### 3. Inspector Widget (`inspector_widget.py`)

Shows all CPU state:
- **R0–R3**: Flash green on change
- **PC, SP**: Current values
- **Flags**: Four indicators (ZERO, EQUAL, GREATER, LESS)

### 4. Memory Viewer (`memory_view.py`)

512-row table with:
- **Access Tracking**: Green = written, Blue = read (fades over time)
- **PC Highlight**: Current PC row highlighted

### 5. Stack Viewer

Memory stack (addresses SP+1 to 255) with SP position marker and item count.

### 6. Execution Trace

Running log: Step#, PC, Instruction, R0–R3, Flags. Auto-scrolls.

### 7. Pipeline Widget (`pipeline_widget.py`)

Visualizes the 5-stage pipeline (IF→ID→EX→MEM→WB):
- Shows which instruction occupies each stage
- Displays bubbles (stalls) and flushes (mispredicts)
- Cycle-by-cycle stage occupancy

### 8. Cache Widget (`cache_widget.py`)

Direct-mapped L1 cache viewer:
- Cache lines with tag, valid bit, dirty bit, data
- Hit/miss counters
- Address-to-line mapping

### 9. Branch Widget (`branch_widget.py`)

Branch predictor state:
- 2-bit saturating counter values
- Prediction history (taken/not taken)
- Accuracy percentage (correct / total)

### 10. Bus Widget (`bus_widget.py`)

System bus transaction viewer:
- Transaction log (requestor, address, type, cycle)
- Arbitration events
- Contention tracking

### 11. Performance Widget (`performance_widget.py`)

Real-time performance dashboard:
- CPI (cycles per instruction)
- IPC (instructions per cycle)
- Cache hit rate
- Branch prediction accuracy
- Total cycles and instructions retired

### 12. Timeline Widget (`timeline_widget.py`)

Cycle-by-cycle trace visualization:
- Horizontal timeline of executed instructions
- Pipeline stage markers per cycle
- Event annotations (cache miss, branch mispredict, interrupt)

### 13. Waveform Widget (`waveform_widget.py`)

Signal waveform viewer:
- Visualizes signal transitions over cycles
- Multiple signal traces
- Zoom and scroll controls

### 14. Game Window (`game_window.py`)

Fantasy Console game display:
- 64×64 pixel framebuffer at 8× scale
- Keyboard input binding
- Game loop integration with SDK Runtime

### 15. Debugger (`debugger_widget.py`)

Full debugger panel:
- Run/Step/Continue controls
- Breakpoint management
- Watch expressions
- CPU state overview

### 16. Pixel Display (`screen_view.py`)

27×27 pixel framebuffer for legacy graphics (black/gray/white). Keyboard capture for OS shell input.

### 17. Controls Toolbar (`controls.py`)

| Control | Function |
|---------|----------|
| Demo selector | Load pre-written demo programs |
| Assemble | Run assembler on editor content |
| Run (▶) | Execute to completion / breakpoint |
| Step Into (⤵) | Execute one instruction |
| Reset (↺) | Reset CPU to initial state |
| Pause (⏸) | Pause running program |
| Continue (▶) | Resume after pause |

---

## Signal Flow

```
User types in editor
    → Assemble button
        → Assembler.assemble(source)
        → Machine.encode_instruction()
        → CPU.load_program(program)

User clicks Run
    → CPU.run() / CPU.step()
        → Update all views
        → Check breakpoints
        → Process UI events

User types in ScreenView
    → Write d2t(ord(char)) to memory[260]
    → OS main loop in CPU polls 260
```

---

## Theme

Dark cyberpunk theme in `styles.py`:
- Background: `#0a0a0f`
- Text: `#00ff88` (green)
- Opcodes: `#00ffff` (cyan)
- Registers: `#ffff00` (yellow)
- Labels: `#aa66ff` (purple)
- Comments: `#004400` (dim green)
- Buttons: `#1a1a2e` with `#00ff88` text

---

## Demo Programs

| Demo | Description |
|------|-------------|
| Countdown | Counts 5→0 with loop |
| Fibonacci | Computes F(3)=2 |
| Factorial | 3! = 6 |
| Sum 1 to N | 1+2+3+4+5 |
| Calculator | ((10+5)-3)+2 = 14 |
| Timer Interrupt | Periodic timer firing |
| Pixel Diagonal | Framebuffer lines |
| Keyboard Echo | Type and see characters |
| (+ more) | 15+ programs total |

---

## Extending the UI

### Adding a New Panel

```python
# In main_window.py:
class MyPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("My Panel"))

    def update_state(self, cpu):
        """Called after each CPU step."""
        pass
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

# Trinary — Ternary (Base-3) Computer Simulation

A complete ternary (base-3) computer system simulated in Python — from logic gates up through an interactive OS, Fantasy Console SDK, PyQt6 desktop UI, and cycle-accurate hardware microarchitecture simulation.

## Features

- **27 instructions**: LOAD, MOV, CLR, ADD, SUB, MUL, DIV, AND, OR, NOT, CMP, JMP, JZ, JNZ, PUSH, POP, CALL, RET, HALT, STOREM, LOADM + **6 tensor coprocessor ops** (TVECADD, TMATMUL, TDOT, TACT, TLOADW, TSTOREW)
- **Signed-magnitude negatives**: leading `-` prefix (e.g., `"-10"` = −3 decimal)
- **Memory-mapped display**: text mode (7×8 chars, addresses 200–255) + SDK framebuffer (64×64 pixels, addresses 1000–5095)
- **Keyboard input**: address 260 (text mode) / 9000–9001 (framebuffer)
- **Two addition paths**: `adder.py` (native base-3 ripple-carry) vs `arithmetic.py` (decimal round-trip)
- **Two-pass assembler**: symbolic labels, `#` and `;` inline comments
- **Machine code encoder/decoder**: 27 variable-length ternary opcode strings
- **Dual stacks**: memory-based PUSH/POP (grows down 255→128) + Python-list CALL/RET
- **Interrupt system**: 8-entry vector table, programmable timer (interrupt 0), software INT
- **PyQt6 desktop UI**: syntax-highlighted editor, debugger, pipeline/cache/bus/branch inspector widgets
- **Fantasy Console SDK**: engine/runtime, sprites, tilemaps, audio, cartridge format
- **TAL compiler**: structured language → ternary assembly (snake game demo)
- **Tensor Accelerator Coprocessor**: 6 ISA opcodes for vector/matrix/tensor operations
- **Hardware simulation**: 5-stage pipeline, cache, branch predictor, bus, DMA, VRAM controller, interrupt controller, profiler (cycle-accurate, optional)
- **GPU mode**: parallel processing elements, workgroups, tensor pipeline dispatch
- **SIMD processor**: packed trit storage, vector ops, lanes
- **Native C backend**: `libternary.so` via ctypes, auto-fallback to Python
- **Dual OS paths**: legacy TTY shell (`os.py`) + modern SDK Kernel/Shell/Terminal (`os/`)
- **ASCII diagrams**: CPU architecture, memory layout, fetch-decode-execute cycle, pipeline visualization
- **594 tests** across all subsystems

## Quick Start

```sh
pip install -e .                  # one-time install
python -m pytest tests/ -v        # run all 594 tests
python -m trinary.os              # boot legacy OS shell (TTY)
python -m trinary.ui.app          # PyQt6 desktop UI (needs PyQt6)
python -m trinary.demo_games pong # Fantasy Console SDK demo
```

### Demos

```sh
python -m trinary.demo_games pong          # Pong (SDK)
python -m trinary.demo_games snake         # Snake (SDK)
python -m trinary.demo_games breakout      # Breakout (SDK)
python -m trinary.demo_games particles     # Particle system
python -m trinary.demo_games bouncing_logo # DVD-style logo
python -m trinary.demo_games tilemap       # Tilemap scroller
python -m trinary.demo_games rpg           # RPG overworld
python test_snake_tal.py                   # TAL-compiled snake (13 frames, CPU test)
python -m trinary.demo_programs            # Legacy demo programs
```

### Native C Benchmark

```sh
make -C src/trinary/native           # build libternary.so
python -m trinary.native_benchmark   # Python vs C speed comparison
```

## Project Structure

```
src/trinary/             ← installable package
├── conversion.py        Trit class + base converters
├── logic.py             TNOT, TAND, TOR gates
├── adder.py             Native base-3 ripple-carry adder
├── arithmetic.py        ADD/SUB/MUL/DIV via decimal round-trip
├── alu.py               ALU: 8 operations + flag computation
├── registers.py         R0–R3 register file
├── memory.py            RAM with hooks, write/read tracking
├── cpu.py               CPU: 27 opcodes, 2 stacks, interrupts, realistic timing
├── assembler.py         Two-pass assembler with labels
├── machine.py           Machine-code encoder/decoder (27 opcodes)
├── os.py                Legacy TTY OS shell
├── os/                  Modern SDK OS (Kernel/Shell/Terminal)
├── display/             Display package (text + framebuffer)
│   ├── text.py          DisplayMemoryMap (7×8 char grid)
│   └── framebuffer.py   PixelDisplay → Framebuffer (64×64)
├── sdk/                 Fantasy Console SDK
│   ├── engine.py        Game engine / runtime
│   ├── cartridge.py     Cartridge format (sprites, tilemaps, code)
│   └── ...
├── accelerator/         Tensor Accelerator Coprocessor
│   ├── accelerator.py   Core tensor ops (add/mul/dot/act)
│   ├── gpu.py           GPU mode (PEs, workgroups, dispatch)
│   ├── simd.py          SIMD processor
│   ├── packed_trits.py  Packed trit storage
│   ├── vector_ops.py    Vector operations
│   └── viz.py           ASCII visualization tools
├── hardware/            Cycle-accurate hardware simulation
│   ├── clock.py         Clock / cycle counter
│   ├── pipeline.py      5-stage pipeline + visualizer
│   ├── hazards.py       RAW hazard detection + forwarding
│   ├── cache.py         Direct-mapped L1 cache
│   ├── branch_predictor.py   2-bit saturating counters
│   ├── bus.py           Shared system bus with arbitration
│   ├── dma.py           Async DMA transfers
│   ├── vram_controller.py    Bandwidth/scanline timing
│   ├── interrupts.py    Priority interrupt controller
│   └── profiler.py      CPI, IPC, cache miss rates, CSV export
├── tal.py               TAL compiler (structured → ternary assembly)
├── native/              C backend (libternary.so)
├── native_backend.py    Python ↔ C bridge (auto-detect)
├── native_benchmark.py  Benchmark Python vs C
├── demo_games.py        Fantasy Console SDK demos
├── demo_graphics.py     Graphics demos
├── demo_programs.py     Legacy assembly demos
├── snake_game.py        Snake (TAL-compiled or direct assembly)
├── diagrams.py          ASCII architecture diagrams
├── benchmark.py         Instruction / memory benchmarks
└── ui/                  PyQt6 desktop visual simulator
    ├── app.py               Application entry point
    ├── main_window.py       Main window assembling all panels
    ├── assembler_editor.py  Syntax-highlighted editor + breakpoints
    ├── controls.py          Run/Step/Reset/Assemble toolbar
    ├── screen_view.py       Pixel framebuffer widget
    ├── memory_view.py       Memory table with access tracking
    ├── debugger_widget.py   Full debugger panel
    ├── pipeline_widget.py   Pipeline stage visualizer
    ├── cache_widget.py      Cache contents viewer
    ├── bus_widget.py        Bus transaction viewer
    ├── branch_widget.py     Branch predictor state
    ├── inspector_widget.py  Register/flag inspector
    ├── performance_widget.py CPI/IPC/cache-hit-rate dashboard
    ├── timeline_widget.py   Cycle timeline viewer
    ├── waveform_widget.py   Signal waveform viewer
    ├── game_window.py       Fantasy Console game window
    └── viz_engine.py        Visualization engine
tests/                  ← 594 pytest tests
├── test_cpu.py              All 27 opcodes + flags + stack + interrupts
├── test_cpu_accelerator.py  CPU + accelerator integration
├── test_accelerator.py      Tensor coprocessor unit tests
├── test_gpu.py              GPU mode
├── test_pipeline.py         Clock, pipeline, hazards, realistic timing
├── test_cache.py            Cache hit/miss
├── test_branch_predictor.py Prediction accuracy
├── test_bus.py              Bus arbitration
├── test_dma.py              DMA transfers
├── test_interrupts.py       Interrupt controller
├── test_vram.py             VRAM timing
├── test_profiler.py         Profiler stats
├── test_realistic_cpu.py    Full CPU in realistic timing mode
├── test_sdk.py              Fantasy Console SDK
├── test_os.py               OS shell
├── test_tal.py              TAL compiler
├── test_tensor_core.py      Tensor core ops
├── test_simd.py             SIMD processor
├── test_packed_trits.py     Packed trit storage
├── test_vector_ops.py       Vector operations
├── test_native_backend.py   Native C bridge
├── test_display.py          Text display + keyboard
├── test_display_framebuffer.py  Framebuffer display
├── test_viz_engine.py       Visualization engine
├── test_arithmetic.py       ADD/SUB/MUL/DIV
├── test_alu.py              ALU operations
├── test_assembler.py        Assembler labels, comments
├── test_conversion.py       Trit + base conversion
├── test_cpu_stress.py       Stress tests (nested calls, loops)
└── test_ternary_nn.py       Neural network (perceptron, trainer, etc.)
docs/
├── ARCHITECTURE.md          Full CPU specification
├── instruction-set.md       27-opcode reference + tensor ISA
├── display-system.md        Dual display internals
├── GRAPHICS_SYSTEM.md       SDK graphics pipeline
├── FANTASY_CONSOLE.md       Fantasy Console SDK docs
├── TERNARY_OS.md            OS internals
├── ui-guide.md              PyQt6 UI guide
├── developer-guide.md       Extending the system
├── tutorial.md              Step-by-step walkthrough
└── benchmarks.md            Performance benchmarks
```

## Architecture Overview

```
┌───────────────────────────────────────────────────────┐
│                   ASSEMBLY SOURCE                      │
│  start: LOAD R0 10; CALL func; HALT                   │
└───────────────────────────────────────────────────────┘
                        │               ┌───────────────────────┐
                        ▼               │  TAL COMPILER         │
┌──────────────────────────────────┐    │  if_eq → CMP/JZ       │
│     TWO-PASS ASSEMBLER           │    │  inc/dec → ADD/SUB    │
│  Pass 1: scan labels → addresses │    │  draw/clear → pixel   │
│  Pass 2: resolve branches        │    └───────────────────────┘
└──────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│        CPU (27 opcodes, 2 stacks, interrupts)          │
│                                                        │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐      │
│  │ FETCH  │→ │ DECODE │→ │EXECUTE │→ │ UPDATE │      │
│  └────────┘  └────────┘  └────────┘  └────────┘      │
│                                                        │
│  Optional: 5-stage pipeline, cache, branch predictor   │
│  Optional: DMA, VRAM controller, interrupt controller  │
│  Optional: Tensor Accelerator Coprocessor (6 ops)      │
│  Optional: GPU mode (parallel PEs)                     │
└───────────────────────────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
┌────────────────────┐  ┌──────────────────────────┐
│  DISPLAY SUBSYSTEM │  │  FANTASY CONSOLE SDK     │
│  Text (7×8 chars)  │  │  Sprites, tilemaps,      │
│  Framebuffer (64²) │  │  audio, cartridge format │
└────────────────────┘  └──────────────────────────┘
```

## CPU Specifications

### Registers

| Register | Encoding | Purpose |
|----------|----------|---------|
| R0       | 0        | Primary accumulator |
| R1       | 1        | Secondary register |
| R2       | 2        | General purpose |
| R3       | 3        | General purpose (OS convention: always 0) |
| PC       | —        | Program counter |
| SP       | —        | Stack pointer (starts at 255, grows down) |
| Flags    | —        | ZERO, EQUAL, GREATER, LESS |

### Memory Map

| Address Range | Purpose |
|---------------|---------|
| 0–127         | General data / program |
| 128–199       | Stack (grows down from 255) |
| 200–255       | Video RAM (text mode: 7×8 chars) |
| 260           | Keyboard buffer (text mode) |
| 1000–5095     | SDK framebuffer (64×64 pixels) |
| 9000–9001     | SDK keyboard input |

### Instruction Set (27 opcodes)

| Category | Instructions |
|----------|-------------|
| Data Movement | LOAD, MOV, CLR |
| Arithmetic | ADD, SUB, MUL, DIV |
| Logical | AND, OR, NOT |
| Comparison | CMP |
| Control Flow | JMP, JZ, JNZ |
| Subroutines | CALL, RET |
| Stack | PUSH, POP |
| Memory | STOREM, LOADM |
| Interrupts | INT, IRET, EI, DI, SETIVT |
| Timer | SETTIMER |
| System | HALT |
| **Tensor** | **TVECADD, TMATMUL, TDOT, TACT, TLOADW, TSTOREW** |

See [docs/instruction-set.md](docs/instruction-set.md) for the complete reference.

## PyQt6 Desktop UI

The visual simulator provides a complete debugging and hardware inspection environment:

- **Assembly editor** with syntax highlighting and breakpoints
- **Machine code viewer** — ternary opcode strings alongside assembly
- **Register/flag inspector** with flash animation on change
- **Memory viewer** with read/write access tracking
- **Stack viewer** with SP position marker
- **Debugger widget** — full step/run/breakpoint controls
- **Pipeline widget** — 5-stage pipeline occupancy visualization
- **Cache widget** — direct-mapped L1 contents and hit/miss tracking
- **Bus widget** — transaction history with arbitration
- **Branch widget** — 2-bit predictor state and accuracy
- **Performance dashboard** — CPI, IPC, cache hit rate
- **Timeline viewer** — cycle-by-cycle trace
- **Waveform viewer** — signal transitions
- **Game window** — Fantasy Console game display
- **Dark cyberpunk theme**

```sh
pip install pyqt6
python -m trinary.ui.app
```

## Fantasy Console SDK

The SDK (`src/trinary/sdk/`) provides a full fantasy console environment:

- **Engine/Runtime** — game loop, input polling, frame timing
- **64×64 pixel framebuffer** with sprite and tilemap support
- **Audio** — waveform-based sound effects
- **Cartridge format** — packs sprites, tilemaps, code into a loadable unit
- **Public API**: `cls`, `spr`, `btn`, `btnp`, `print_text`, `pixel`, `rect`, `sfx`, `poll_input`

```python
from trinary.sdk import Engine, Cartridge
engine = Engine()
engine.load_cartridge(Cartridge.load("my_game.cart"))
engine.run()
```

Run demos:
```sh
python -m trinary.demo_games pong
python -m trinary.demo_games snake
python -m trinary.demo_games breakout
```

## TAL Compiler

The TAL compiler (`tal.py`) compiles a structured higher-level language into ternary CPU assembly:

```
x = 10
y = 20
if_eq x y
    draw x y 1
else
    draw x y 2
```

Supports `if_eq`/`if_ne`, `inc`/`dec`/`add`/`sub`, `draw`/`clear` pixel, array access, I/O port load/write. The snake game (`snake_game.py`) uses 524 TAL-compiled instructions.

```sh
python test_snake_tal.py   # runs TAL-compiled snake through CPU
```

## Hardware Simulation (Cycle-Accurate)

All hardware modules are optional — enabled via `CPU(realistic_timing=True)`.

| Module | Description |
|--------|-------------|
| **Pipeline** | 5-stage IF→ID→EX→MEM→WB with bubbles, flushes, ASCII viz |
| **Hazard Unit** | RAW detection, forwarding paths, stall insertion |
| **Cache** | Direct-mapped L1, hit/miss tracking, write-back |
| **Branch Predictor** | Static + 2-bit saturating counters |
| **Bus** | Shared system bus, priority arbitration, contention |
| **DMA** | Async memory-to-memory transfers, concurrent with CPU |
| **VRAM Controller** | Bandwidth limits, scanline timing, frame sync |
| **Interrupt Controller** | 8-line priority controller, masking, nesting |
| **Profiler** | CPI, IPC, cache rates, branch accuracy, CSV export |

```python
from trinary.cpu import CPU
cpu = CPU(realistic_timing=True)
cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])
cpu.run(verbose=False)
print(f"Cycles: {cpu.clock.cycle}")
print(cpu.profiler.report())
print(cpu.pipeline.visualize(cycle=5))
```

## Tensor Accelerator Coprocessor

Hardware-accelerated tensor operations integrated with the CPU ISA:

| Opcode | Operation |
|--------|-----------|
| `TLOADW` | Load CPU memory into accelerator tensor |
| `TSTOREW` | Store accelerator tensor to CPU memory |
| `TVECADD` | Element-wise vector addition |
| `TMATMUL` | Matrix multiplication |
| `TDOT` | Dot product (scalar result → R0) |
| `TACT` | In-place activation (step function) |

## Dual Display / OS Subsystems

| Layer | VRAM Range | Display | Used by |
|-------|-----------|---------|---------|
| **Legacy** (text) | 200–255 | 7×8 chars | `os.py`, `demo_programs.py` |
| **SDK** (framebuffer) | 1000–5095 | 64×64 pixels | `os/`, `sdk/`, `demo_games.py`, PyQt6 |

## Development

```sh
git clone <repo>
cd trinary
pip install -e .
python -m pytest tests/ -v
```

### Adding a new instruction

1. Add opcode to `OPCODE_MAP` in `machine.py`
2. Add to `OPCODES` set in `cpu.py`
3. Implement execution in `cpu.execute_instruction()`
4. Add cycle cost to `CYCLES` dict in `cpu.py`
5. Add tests in `tests/test_cpu.py`
6. Update assembler if new operand formats are needed

## Testing

```sh
python -m pytest tests/ -v                        # all 594 tests
python -m pytest tests/test_cpu.py -v             # CPU-specific
python -m pytest tests/test_hardware -v           # hardware sim
python -m pytest tests/test_accelerator.py -v     # tensor coprocessor
python -m pytest tests/test_sdk.py -v             # Fantasy Console SDK
python -m pytest tests/test_os.py -v              # OS tests
python -m pytest tests/ -k "realistic" -v         # cycle-accurate tests
```

## License

MIT

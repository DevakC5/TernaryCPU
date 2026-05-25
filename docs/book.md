# Trinary: A Ternary (Base-3) Computer Simulation — Book Outline

---

## Chapter 1 — Introduction to Ternary Computing

- Historical context: binary vs ternary number systems
- Information-theoretic advantages of base-3 (Knuth, Hurst)
- The Soviet Setun computer (1958)
- Why simulate a ternary computer in software?
- Scope of this book: from logic gates to a working OS
- This chapter's code: verifying your Python environment

---

## Chapter 2 — System Architecture Overview

- Five-layer abstraction stack: logic → ALU → CPU → Assembler → OS
- Module dependency graph
- 512-address memory map (data, stack, VRAM, keyboard)
- Signed-magnitude ternary number representation
- Dual-stack design: memory stack (PUSH/POP) vs call stack (CALL/RET)
- 26-opcode instruction set summary
- `src/trinary/` directory structure
- This chapter's code: importing the package and exploring its public API

---

## Chapter 3 — Environment Setup and Quick Start

- Installing Python 3.10+
- Package installation: `pip install -e .`
- Running all 113 tests: `python -m pytest tests/ -v`
- Booting the interactive OS shell: `python -m trinary.os`
- Launching the PyQt6 desktop UI: `python -m trinary.ui.app`
- Running demo programs: `python -m trinary.demo_programs`
- Viewing ASCII architecture diagrams: `python -m trinary.diagrams`
- This chapter's code: writing, assembling, and running a first "Hello, Ternary" program

---

## Chapter 4 — Trit: The Fundamental Unit

- What is a trit? The ternary analogue of a bit
- The three states: 0, 1, 2
- The `Trit` class: construction, validation, string representation
- Allowed values and error handling
- Relation to higher-level representation
- This chapter's code: creating, inspecting, and manipulating Trit objects

---

## Chapter 5 — Base Conversion Systems

- Ternary ↔ Decimal conversion: `decimal_to_ternary`, `ternary_to_decimal`
- Signed-magnitude convention: leading `-` for negatives
- Ternary ↔ Binary conversion: `ternary_to_binary`, `binary_to_ternary`
- Binary ↔ Decimal conversion: `binary_to_decimal`, `decimal_to_binary`
- Validation functions: `validate_ternary`, `validate_binary`
- Edge cases: zero, negative numbers, invalid strings
- This chapter's code: interactive CLI converter, round-trip verification (0–99, −99 – −1)

---

## Chapter 6 — Ternary Logic Gates

- Extending Boolean logic to three values
- TNOT: `tnot(x) = 2 - x`
- TAND: `tand(x, y) = min(x, y)`
- TOR: `tor(x, y) = max(x, y)`
- Truth tables for all three gates
- The `validate_trit` helper
- Why these definitions? Mathematical motivation
- This chapter's code: generating and printing formatted truth tables

---

## Chapter 7 — Adder Circuits

- Half adder: adding two trits, sum and carry
- Full adder: adding three trits (two operands + carry-in)
- Ripple-carry adder: chaining full adders for multi-trit strings
- The `ripple_carry_adder_detailed` function and per-position traces
- Limitations: non-negative numbers only, educational focus
- Comparison with the decimal round-trip approach used by the CPU
- This chapter's code: printing step-by-step adder traces for various inputs

---

## Chapter 8 — Arithmetic via Decimal Round-Trip

- Rationale: why the CPU doesn't use the native ternary adder
- ADD: `add_ternary(a, b)` — convert, add, convert back
- SUB: `subtract_ternary(a, b)` — handles negative results
- MUL: `multiply_ternary(a, b)` — handles negative operands
- DIV: `divide_ternary(a, b)` — floor division, zero-division error
- The `validate_ternary` lambda
- This chapter's code: exercising all four operations with positive and negative values

---

## Chapter 9 — The Arithmetic Logic Unit

- The `alu` function: unified entry point for 8 operations
- Operation dispatch: ADD, SUB, MUL, DIV, AND, OR, NOT, CMP
- `pad_equal_length` for bitwise logical operations
- CMP: comparison returning "EQ", "GT", or "LT"
- The `VALID_OPERATIONS` constant
- Integration: called by the CPU for all data-processing instructions
- This chapter's code: running all 8 ALU operations and inspecting results

---

## Chapter 10 — The Register File

- Four general-purpose registers: R0 (accumulator), R1, R2, R3
- The `RegisterFile` class: `load`, `store`, `move`, `clear`
- Validation: register names, ternary values
- The `dump` method and `__repr__`
- R3 convention in the OS (always zero)
- This chapter's code: loading values, moving between registers, clearing

---

## Chapter 11 — Memory Architecture

- The `Memory` class: size-configurable, ternary-string values
- Address validation (0–size-1)
- Core operations: `store`, `load`, `clear`, `clear_all`
- Debugging: `dump`, `dump_hex`
- Memory regions: data (0–127), stack (128–199), VRAM (200–255), keyboard (260)
- CPU creates `Memory(512)` — 512-address RAM
- This chapter's code: storing and loading values, inspecting memory contents

---

## Chapter 12 — CPU Design: Fetch-Decode-Execute

- The `CPU` class: state machine overview
- Program counter (PC), stack pointer (SP), flag register
- `load_program`: loading a list of instruction strings
- `parse_instruction`: splitting opcode and operands
- `execute_instruction`: the 26-branch dispatch
- `step`: fetch → execute → cycle accounting → timer → interrupt check
- `run`: the main execution loop (verbose mode with trace)
- The `CYCLES` dictionary: per-instruction cycle costs
- This chapter's code: single-stepping through a simple program

---

## Chapter 13 — Data Movement Instructions

- `LOAD R0 value`: load immediate into register
- `MOV R0 R1`: copy value between registers
- `CLR R0`: zero a register
- Implementation details in `execute_instruction`
- Cycle costs and flag effects (none for data movement)
- This chapter's code: programs exercising LOAD, MOV, and CLR

---

## Chapter 14 — Arithmetic and Logical Instructions

- ADD, SUB, MUL, DIV: register-to-register, write-back to destination
- AND, OR, NOT: per-trit logical operations via the ALU
- Read both operands → call `alu(op, a, b)` → write result
- Cycle costs: ADD/SUB/AND/OR/NOT = 1, MUL = 3, DIV = 5
- This chapter's code: arithmetic chains, mixed logical operations

---

## Chapter 15 — Comparison and Control Flow

- `CMP`: compares two register values
- Four flags: ZERO, EQUAL, GREATER, LESS
- `JMP addr`: unconditional jump
- `JZ addr`: jump if ZERO or EQUAL
- `JNZ addr`: jump if NOT ZERO and NOT EQUAL
- Flag semantics and edge cases (ZERO vs EQUAL distinction)
- This chapter's code: countdown loops, conditional branching

---

## Chapter 16 — Subroutines: CALL and RET

- The call stack: a Python list managed separately from memory
- `CALL addr`: push PC+1 onto call_stack, jump to addr
- `RET`: pop address from call_stack, set PC
- Nesting subroutines: how the call stack grows and shrinks
- StackUnderflowError on RET with empty call_stack
- Contrast with the memory-based PUSH/POP stack
- This chapter's code: a 5-deep nested subroutine chain

---

## Chapter 17 — Stack Operations: PUSH and POP

- The memory stack: SP (initialized to 255, grows down to 128)
- `PUSH R0`: store register at SP, decrement SP
- `POP R0`: increment SP, load from memory into register
- StackOverflowError (SP < 128) and StackUnderflowError (SP >= 255)
- Stack region: addresses 128–199 (32 cells)
- This chapter's code: pushing 10 values, popping them back in reverse

---

## Chapter 18 — Memory Access Instructions

- `STOREM R0 addr`: store register value into memory
- Two address modes: literal integer or register-based (`ternary_to_decimal`)
- `LOADM R0 addr`: load memory value into register
- Same dual address mode
- Connection to the memory-mapped display (addresses 200–255)
- This chapter's code: writing to and reading from arbitrary memory addresses

---

## Chapter 19 — The Interrupt System

- Interrupt Vector Table (IVT): 8 entries, set via SETIVT
- `INT n`: trigger software interrupt n
- Hardware interrupts: timer-driven
- Interrupt flow: push PC+1 → disable interrupts → jump to handler
- `IRET`: pop PC → enable interrupts
- `EI` / `DI`: global interrupt flag
- Nesting interrupts and stack overflow protection
- This chapter's code: writing an interrupt handler, triggering it

---

## Chapter 20 — Timer and Interrupt-Driven Execution

- The hardware timer: SETTIMER sets period and counter
- Timer decrements each CPU step; fires interrupt 0 when it reaches zero
- Periodic interrupt generation for preemptive multitasking
- Timer counter reloads automatically
- Interaction with EI/DI and the pending interrupt mechanism
- This chapter's code: a timer-driven counter that increments on each interrupt

---

## Chapter 21 — The Two-Pass Assembler

- Why a two-pass design? Forward references and labels
- Pass 1: scanning for labels, building the symbol table
- Pass 2: resolving label references in jump/call operands
- The `Assembler` class: `parse_line`, `first_pass`, `second_pass`, `assemble`
- Comment handling: `#` and `;` delimiters
- BRANCH_OPCODES: JMP, JZ, JNZ, CALL
- This chapter's code: assembling a program with labels and forward jumps

---

## Chapter 22 — Machine Code Encoding and Decoding

- The OPCODE_MAP: 21 of 26 instructions mapped to 3-trit opcodes
- Register encoding: R0→"0", R1→"1", R2→"2", R3→"3"
- Immediate and address encoding (ternary)
- `encode_instruction`: assembly string → ternary machine code
- `decode_instruction`: ternary machine code → assembly string
- The `Machine` class: full pipeline (assemble → encode)
- Unmapped instructions: INT, IRET, EI, DI, SETIVT, SETTIMER
- This chapter's code: round-trip encoding and decoding, inspecting opcode tables

---

## Chapter 23 — Memory-Mapped Display and Keyboard

- VRAM: addresses 200–255, 56 characters in a 7×8 grid
- The `DisplayMemoryMap` class: `read_display`, `write_text`, `clear`
- Character encoding: ASCII values stored as ternary numbers
- Keyboard buffer: address 260, polled by the OS
- The `PixelDisplay` class: 27×27 pixel framebuffer
- Drawing primitives: `set_pixel`, `draw_line` (Bresenham)
- This chapter's code: writing text to the display, drawing pixel patterns

---

## Chapter 24 — The Operating System Shell

- OS source: ~342 lines of assembly (the `_gen()` function)
- Boot sequence: clear screen, print banner, show prompt
- Main loop: poll keyboard (mem[260]), dispatch to handler
- Input buffer: addresses 1–32, backspace support
- The display driver: cursor management (vput, vinc, vdec), scrolling
- Command parsing: HELP, CLS, REGS, MEMDUMP, RUN
- The `OS` class: `boot`, `step_os`, `feed_key`, `render_console`
- Interactive terminal mode: `boot_interactive()` with raw TTY
- This chapter's code: booting the OS, sending commands programmatically

---

## Chapter 25 — The PyQt6 Visual Simulator

- Architecture: Qt model-view separation, decoupled from backend
- The `MainWindow`: assembling all panels in a splitter layout
- Assembler editor with syntax highlighting (cyan opcodes, yellow registers, purple labels, green comments)
- Machine code viewer: side-by-side assembly ↔ ternary strings
- Register panel with flash animation on value change
- Memory viewer: 512-row table, colour-coded read (blue) / write (green) tracking
- Stack viewer: SP indicator, live item list
- Execution trace: step-by-step history (step#, PC, instruction, registers, flags)
- Pixel display: 27×27 buffered widget, keyboard capture
- Toolbar controls: Assemble, Run, Step Into, Step Over, Reset, Pause, Continue
- 13 demo programs in the dropdown selector
- Dark cyberpunk stylesheet (`styles.py`)
- This chapter's code: launching the UI, running a demo, single-stepping

---

## Chapter 26 — Games and Demos

- Two distinct game systems coexist in the codebase
- Legacy CPU demos (`demo_programs.py`): 13 assembly programs running on the ternary CPU with the 7×8 text display (VRAM 200–255). Run via `python -m trinary.demo_programs`
- SDK games (`demo_games.py`): 8 graphical games using the Fantasy Console SDK with the 64×64 pixel framebuffer (VRAM 1000–5095, keyboard at 9000). Run via `python -m trinary.demo_games <name>`
- All SDK games share a common architecture: an `Engine` wrapping a `Framebuffer`, a `Memory(10000)`, and a plain `state` dictionary. Games define three functions: a factory (`demo_*`), an `_update` step, and a `_render` step. The `Runtime` class provides the game loop (update → render → vsync)
- Available SDK games and what they demonstrate:
  - **Pong** — bouncing ball, paddle collision (D-pad/DOWN/UP), score tracking. Uses `DEFAULT_SPRITES["ball"]` and `DEFAULT_SPRITES["paddle"]`
  - **Snake Deluxe** — TAL-compiled snake game. Game logic runs entirely on the ternary CPU via `TALSnake` (524 instructions compiled from `tal.py`). Rendering syncs from memory-mapped VRAM via `CPUSnakeDisplay`. Body stored in a circular buffer at mem 20–147. Launches with larger 8× pixels
  - **Breakout** — ball physics, paddle via LEFT/RIGHT, brick grid (7×4 = 28 bricks) with collision removal
  - **Particle System** — 50-particle fountain with gravity (`vy += 0.3`), randomized velocity and color, 30-frame lifetime
  - **Pixel Paint** — freeform drawing on the 64×64 canvas. D-pad moves cursor, A button paints. Cursor rendered as color 8
  - **Bouncing Logo** — a rect-within-rect "logo" bounces off screen edges at 45°. Shows the simplest update-render game structure
  - **Tilemap Scroller** — scrollable 32×32 tile world with camera control via D-pad. Shows `TileMap` rendering with `camera_x`/`camera_y`
  - **RPG Movement** — 16×16 tile world with collision. Player sprite walks in 8×8 tile grid, camera follows. Uses `is_solid` to block movement into walls
- The `_snake_factory` is the only demo that bridges the SDK to the ternary CPU — all other games run in pure Python with no CPU emulation
- Low-level graphics tests (`demo_graphics.py`): pixel test, color bars, moving pixel, bouncing box — direct `Framebuffer` manipulation, not part of the demo_games launcher
- Default sprites (`DEFAULT_SPRITES`) ship with the SDK: ball, paddle, player, brick, and a full ASCII character sheet. Custom sprites can be built with `make_sprite_from_strings`
- This chapter's code: launching any SDK game, inspecting its state and framebuffer, extending a game with new behaviour

---

## Chapter 27 — The TAL Compiler

- Purpose: a higher-level structured language that compiles down to ternary CPU assembly
- The `tal.py` module: tokenizer, parser, code generator in a single pass
- Control structures: `if_eq` / `if_ne` for conditional branching with automatic label generation
- Arithmetic helpers: `inc` / `dec` / `add` / `sub` operating on named variables mapped to memory addresses
- Pixel graphics: `draw` and `clear` pixel commands for the memory-mapped framebuffer
- Array access: `body_x` / `body_y` notation for indexed memory access into circular buffers
- Label syntax: `name:` (not `label name:`) with address constants in `@addr` notation resolved during compilation
- The snake game: 524 TAL-compiled instructions running entirely on the ternary CPU
- `TALSnake` class: drop-in replacement for `CPUSnake` via `init()` / `update()` / `render()` / `shutdown()`
- This chapter's code: writing a TAL program, compiling it to assembly, and running it on the CPU

---

## Chapter 28 — Native C Backend

- Motivation: pure Python ALU operations are too slow for compute-intensive workloads
- The C native layer: `libternary.so` implementing ALU ops in compiled C for 10–50× speedup
- ctypes bridge: `native_backend.py` auto-detects the shared library at import time
- `NATIVE_AVAILABLE` flag: callers check whether acceleration loaded and fall back to pure Python
- Building: `make -C src/trinary/native` or `bash build_native.sh` produces the shared library
- Performance benchmark: `python -m trinary.native_benchmark` comparing Python vs C throughput
- Benchmark results: C accelerates ALU-heavy workloads, especially MUL and DIV which dominate cycle costs
- This chapter's code: running the native benchmark, inspecting fallback behaviour

---

## Chapter 29 — The Dual Display System

- Two independent display subsystems coexist, each with its own VRAM range and feature set
- **Text mode** (legacy): VRAM addresses 200–255, 56 characters arranged in a 7×8 grid. Backward compatible with all original CPU programs and the OS shell. Uses the `DisplayMemoryMap` class for read/write/clear operations
- **Framebuffer mode** (SDK): VRAM addresses 1000–5095, 64×64 pixel grid with 9-color palette (0–8). Uses the `Framebuffer` class with per-pixel set/get/clear, horizontal and vertical line drawing, and rectangle fill
- Keyboard input at address 260 (text mode) vs addresses 9000–9001 (framebuffer mode, with 8-button D-pad mapping)
- Display subsystem refactored from a single `display.py` into the `display/` package — imports use `from trinary.display import ...`
- CPU default `Memory(512)` only covers text mode; framebuffer SDK path passes `CPU(memory=Memory(10000))`
- This chapter's code: writing text to the text display, drawing pixels to the framebuffer, running both simultaneously

---

## Chapter 30 — The Fantasy Console SDK

- Architecture: `Engine` + `Runtime` split — the Engine owns state and peripherals, the Runtime runs the game loop
- `Engine` class: wraps a `Framebuffer` (64×64), a `Memory(10000)` with mapped VRAM, a `Keyboard` at 9000–9001, and a plain `state` dictionary for game data
- `Runtime` class: provides the canonical game loop — `update()` → `render()` → vsync (with `pygame.time.Clock` or `time.sleep`). Supports variable `target_fps` and optional `cpu_sync` for CPU-driven games
- `Sprite` class: 8×8 pixel art with per-pixel transparency (color 8 = transparent). Construction via 8-string arrays, hex strings, or `ints_from_hex`. Sprites render with optional flip and scale. `DEFAULT_SPRITES` ships ball, paddle, player, brick, and a 95-character ASCII sheet
- `TileMap` class: 2D grid of tile indices with `camera_x` / `camera_y` scrolling. `render(fb)` draws visible tiles, `is_solid(x, y)` checks collision against a solid-tile set. Tile dimensions are 8×8 pixels by default
- `Animation` class: frame-based playback with a list of (sprite, duration) frames. Supports `play`, `stop`, `pause`, `next_frame`, `reset`. Tracks elapsed time via `update(dt)`. Works with any sprite sheet split into frames
- Input API: `btn(button)` returns pressed state, `btnp(button)` returns edge-triggered (just pressed). 8-button mapping: U (up), D (down), L (left), R (right), A, B, X, Y. Backed by the `Keyboard` class reading from memory at 9000–9001
- Audio: `sfx(sound_id, channel=0)` — stub system with placeholder. Accepts sound IDs and channels but no audio backend yet. Future expansion point for waveform synthesis
- `Cartridge` class: JSON-bundled game data packing sprites, tilemaps, palettes, metadata, and code as a portable file. Export/import with `save(path)` / `load(path)`
- 8 built-in demo games: Pong, Snake Deluxe, Breakout, Particle System, Pixel Paint, Bouncing Logo, Tilemap Scroller, RPG Movement
- This chapter's code: building a complete game from scratch using the SDK, loading a cartridge

---

## Chapter 31 — The Tensor Accelerator Coprocessor

- Purpose: offload compute-intensive linear algebra to dedicated hardware, freeing the CPU for control flow
- Module: `src/trinary/accelerator/` containing the accelerator, GPU mode, tensor core, SIMD, visualization, and packed storage
- 6 tensor ISA opcodes integrated into the CPU, assembler, and machine encoder:
  - `TLOADW addr rows cols` — load CPU memory into accelerator, returns tensor ID in R0
  - `TSTOREW tid addr` — store accelerator tensor back to CPU memory
  - `TVECADD dst src_a src_b` — element-wise vector addition, result TID in R0
  - `TMATMUL dst src_a src_b` — matrix multiplication, result TID in R0
  - `TDOT src_a src_b` — dot product, scalar result in R0 (ternary-encoded)
  - `TACT tid type` — in-place activation (type 0 = step function)
- Operands support immediate numbers or registers (R0–R3), with R0 reading the result TID via `decimal_to_ternary`
- Integration with the CPU pipeline: tensor instructions follow the same fetch-decode-execute cycle, dispatching to the accelerator coprocessor
- 70 unit tests for the accelerator, 11 CPU integration tests
- This chapter's code: writing tensor programs, running TVECADD and TMATMUL, comparing performance with pure CPU implementations

---

## Chapter 32 — Hardware Microarchitecture Simulation

- Purpose: cycle-accurate hardware simulation for educational computer architecture, enabled via `CPU(realistic_timing=True)`
- **Clock module** (`clock.py`): cycle counter, configurable frequency, period-based timing. Every `step()` consumes one clock cycle
- **5-stage pipeline** (`pipeline.py`): `PipelineStage` and `Pipeline` classes implementing IF→ID→EX→MEM→WB. Instructions flow through stages each cycle. ASCII pipeline visualizer shows stage occupancy (`pipeline.visualize(cycle=N)`)
- **Hazard unit** (`hazards.py`): `HazardUnit` detects RAW (read-after-write) hazards, generates forwarding paths to bypass the register file, and inserts stalls (bubbles) when forwarding cannot resolve the hazard
- **Cache** (`cache.py`): direct-mapped L1 cache with `CacheLine` entries. Tracks hits and misses, write-back policy, configurable size and associativity
- **Branch predictor** (`branch_predictor.py`): static always-taken / always-not-taken strategies plus dynamic 2-bit saturating counter predictor. Tracks prediction accuracy and mispredict counts
- **Bus** (`bus.py`): shared system bus with priority-based arbitration, `BusRequest` queue, contention modelling. Handles memory access requests from CPU, DMA, and peripherals
- **DMA** (`dma.py`): asynchronous memory-to-memory transfers running concurrently with the CPU. `DMATransfer` objects track source, destination, size, and status. DMA cycles are interleaved with CPU cycles on the bus
- **VRAM controller** (`vram_controller.py`): enforces display bandwidth limits, models scanline timing, provides frame synchronization signals
- **Interrupt controller** (`interrupts.py`): `InterruptController` with 8 interrupt lines, configurable priority levels, interrupt masking per line, and support for nested interrupt handling
- **Profiler** (`profiler.py`): collects cycle-by-cycle metrics — CPI (cycles per instruction), IPC (instructions per cycle), cache hit/miss rates, branch prediction accuracy, stall breakdowns. Export to CSV via `profiler.export_csv(path)`
- All hardware modules are optional and backward-compatible — `CPU()` without `realistic_timing` behaves identically to the original instant-execution emulator
- 9 CPU integration tests validate realistic-timing mode against known program behaviour
- This chapter's code: enabling realistic timing, reading profiler reports, viewing pipeline visualizations

---

## Chapter 33 — GPU Mode and Parallel Computing

- Module: `gpu.py` in `src/trinary/accelerator/` — a simulated GPU architecture for parallel computation
- Three-level hierarchy: `ProcessingElement` → `Workgroup` → `TernaryGPU`
  - `ProcessingElement`: the smallest compute unit, executes a single kernel thread with local register state
  - `Workgroup`: a group of PEs sharing local memory and synchronization barriers
  - `TernaryGPU`: the full GPU with configurable `PEs_per_wg × n_workgroups` processing elements
- Kernel dispatch: kernels are Python callables distributed across all PEs. Each PE receives its global and local ID plus access to shared workgroup memory
- Tensor pipelines: GPU-level dispatch for tensor operations (matmul, element-wise ops) with workgroup coordination
- Parallel matmul: matrix multiplication decomposed into workgroups, each computing a tile of the result matrix. PEs within a workgroup collaborate on tile computation with barrier synchronization
- ASCII visualization (`viz.py`): `render_simd_lanes`, `render_tensor_matrix`, `render_matmul`, `render_gpu_state` functions for terminal-based inspection of GPU state
- 19 GPU mode + visualization tests
- This chapter's code: writing a GPU kernel, dispatching it across workgroups, visualizing parallel execution

---

## Chapter 34 — SIMD and Packed Storage

- **SIMD processor** (`simd.py`): single-instruction multiple-data processor with configurable vector width. Operates on vector registers with lane-level parallelism
- Vector operations: `vector_add`, `vector_mul`, `vector_dot` — each applies the operation across all lanes simultaneously. Dot product reduces across lanes to a scalar
- **Packed trit storage** (`packed_trits.py`): memory-efficient encoding of ternary values. Each trit (0, 1, 2) encodes in 2 bits (00, 01, 10) instead of a full Python string. Packing ratio: 4 trits per byte versus 1 trit per Python string character
- Packing functions: `pack_trits` / `unpack_trits` for byte-level conversion, `packed_to_ternary_string` / `ternary_string_to_packed` for string interop
- ASCII lane visualization: `render_simd_lanes(trit_values)` displays vector lanes as a horizontal bar with lane indices and trit values
- SIMD integration with the accelerator: vector ops can dispatch to SIMD lanes for parallel execution
- 20 packed storage tests, 11 SIMD processor tests, 12 vector ops tests
- This chapter's code: writing SIMD programs, comparing packed vs unpacked memory usage, visualizing lane execution

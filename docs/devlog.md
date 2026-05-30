# Devlog 001 — Project Initialization

## Overview

Started the Ternary Computer Project.

Goal:

* explore ternary computing systems
* simulate ternary arithmetic and logic
* research alternate computational architectures

Initial setup:

* repository structure
* README
* documentation folders
* test folders

Created:

* docs/
* src/
* tests/

Key idea:
Traditional computers use binary:
0 and 1

This project investigates ternary systems:
0, 1, and 2

---

# Devlog 002 — Conversion System

## Implemented

* binary → decimal
* decimal → ternary
* ternary → binary
* ternary → decimal

Core realization:
ternary representations often use fewer digits than binary.

Example:
10101₂ = 21₁₀ = 210₃

Added:

* validation systems
* reusable conversion functions
* modular architecture

Key files:

* conversion.py
* validation.py

---

# Devlog 003 — Trit Datatype

## Implemented

Created foundational Trit datatype.

```python id="jlwm55"
class Trit
```

Features:

* allowed values:
  0, 1, 2
* validation
* string representation
* reusable datatype structure

Purpose:
This becomes the atomic unit of the ternary system, similar to a binary bit.

---

# Devlog 004 — Ternary Arithmetic

## Implemented

* ternary addition
* subtraction
* multiplication
* division

Initial implementation strategy:
ternary → decimal → operation → ternary

Reason:
Prioritized correctness and rapid prototyping before low-level optimization.

Key realization:
ternary arithmetic introduces different carry behavior compared to binary systems.

---

# Devlog 005 — Ternary Logic Gates

## Implemented

* TNOT
* TAND
* TOR

Logic definitions:
0 = FALSE
1 = NEUTRAL
2 = TRUE

TNOT truth table:
0 → 2
1 → 1
2 → 0

TAND:
minimum-value logic

TOR:
maximum-value logic

This established the project's first custom ternary logic system.

---

# Devlog 006 — Half Adder & Full Adder

## Implemented

* ternary half adder
* ternary full adder
* complete 27-state truth table

Inputs:

* A
* B
* Carry_in

Outputs:

* Sum
* Carry_out

Key observation:
Unlike binary adders, ternary adders can produce:

* carry = 0
* carry = 1
* carry = 2

Example:
2 + 2 + 2 = 20₃

Meaning:

* Sum = 0
* Carry_out = 2

This introduced multi-valued carry propagation behavior.

---

# Devlog 007 — Ripple Carry Adder

## Implemented

Multi-digit ternary ripple carry adder.

Key mechanism:
carry_out[i] → carry_in[i+1]

Implemented:

* chained full adders
* sequential carry propagation
* detailed arithmetic tracing

Verified results:
102₃ + 21₃ = 200₃
222₃ + 111₃ = 1110₃

Added detailed trace system:

```python id="jlwm56"
{
  "position": 0,
  "a": 2,
  "b": 1,
  "carry_in": 0,
  "sum": 0,
  "carry_out": 1
}
```

This establishes the first architecture-level arithmetic simulation layer.

Next targets:

* ALU
* registers
* instruction encoding
* memory simulation


NEXT STEP
Registers

Create:

registers.py

Simulate:

R0
R1
R2
R3

Each stores ternary values.

Example:

R0 = "102"

Operations:

LOAD
STORE
MOVE

# Devlog 009 — Register File Implementation

## Overview

Implemented a ternary register file system.

Registers provide temporary high-speed storage for computational operations and processor state management.

---

## Implemented Registers

Current architecture:

* R0
* R1
* R2
* R3

Each register stores ternary values as strings.

---

## Supported Operations

### LOAD

Stores a ternary value into a register.

Example:
LOAD R0, "102"

---

### STORE

Reads the current register value.

---

### MOVE

Copies one register value into another register.

Example:
MOVE R0, R1

---

### CLEAR

Resets register contents to:
0

---

## Architectural Importance

The register file introduces:

* processor state
* temporary working memory
* data transfer operations

This marks the transition from isolated arithmetic systems to processor-like computational state management.

---

## Next Targets

* instruction execution
* opcode decoding
* CPU control flow
* fetch-decode-execute cycle

# Devlog 010 — CPU Core & Instruction Execution

## Overview

Implemented the first functional ternary CPU execution core.

The architecture now supports:

* instruction parsing
* opcode decoding
* ALU execution
* register state management
* conditional branching
* program control flow

---

## CPU Components

Current CPU structure:

CPU
├── Registers (R0-R3)
├── Program Counter (PC)
├── Flags
├── ALU
└── Fetch-Decode-Execute Cycle

---

## Supported Instructions

### Data Operations

* LOAD
* MOV
* CLR

### Arithmetic

* ADD
* SUB

### Logic

* AND
* OR
* NOT

### Comparison

* CMP

### Control Flow

* JMP
* JZ
* JNZ

---

## Major Architectural Milestone

The project now supports:

* sequential program execution
* conditional branching
* processor state transitions

This marks the transition from isolated computational modules to a functioning processor architecture.

---

## Key Achievement

Implemented a complete fetch-decode-execute cycle for a custom ternary instruction set architecture (ISA).

---

## Next Targets

* memory simulation
* addressable RAM
* stack system
* subroutines
* execution tracing
* performance benchmarking

# Devlog 012 — Stack System & Subroutine Execution

## Overview

Implemented:

* stack operations
* subroutine execution
* function call mechanics
* return address management

The architecture now supports structured program flow similar to real processor systems.

---

## New Instructions

### PUSH

Push register value onto stack.

### POP

Restore value from stack.

### CALL

Jump to subroutine while preserving return address.

### RET

Restore return address and continue execution.

### HALT

Stop processor execution.

---

## Major Architectural Milestone

The CPU now supports:

* nested execution flow
* subroutine calls
* stack-based state preservation
* procedural execution structures

This marks the transition from a basic instruction interpreter to a complete virtual-machine-like architecture.

---

## Example Execution Flow

CALL:

* pushes current PC onto stack
* jumps to target address

RET:

* pops return address
* restores execution flow

---

## Current Architecture

CPU
├── Registers
├── ALU
├── Flags
├── Stack
├── Program Counter
├── Memory
└── Fetch-Decode-Execute Cycle

---

# Devlog 013 — v2.0.0 Release: Full Hardware Simulation, SDK, AI/ML

## Overview

Released v2.0.0 — a major expansion from 113 to 594 tests, adding entire subsystems for hardware microarchitecture simulation, a Fantasy Console SDK, tensor coprocessor, GPU mode, TAL compiler, native C backend, and much more.

## New Subsystems

### Hardware Microarchitecture (cycle-accurate)
- 5-stage pipeline (IF→ID→EX→MEM→WB) with hazard detection, forwarding, stalls
- Direct-mapped L1 cache with hit/miss tracking and write-back
- 2-bit saturating counter branch predictor
- Shared system bus with priority arbitration
- Async DMA transfers concurrent with CPU
- VRAM controller with bandwidth limits and scanline timing
- 8-line priority interrupt controller with masking and nesting
- Profiler: CPI, IPC, cache rates, branch accuracy, CSV export

### Tensor Accelerator Coprocessor
- 6 new ISA opcodes: TLOADW, TSTOREW, TVECADD, TMATMUL, TDOT, TACT
- Register-based tensor IDs, result → R0
- GPU mode with ProcessingElement → Workgroup → TernaryGPU hierarchy
- SIMD processor with vector lanes
- Packed trit storage for memory efficiency

### Fantasy Console SDK
- Engine + Runtime with fixed-timestep game loop (30 FPS)
- Sprite class with transparency, flip, 8×8 pixel art
- TileMap with camera scrolling and collision detection
- Animation system (frame-based, play/stop/pause)
- Input API with 8-button mapping (btn/btnp)
- Audio stub (sfx)
- Cartridge format (JSON serialization)
- 8 demo games: Pong, Snake, Breakout, Particles, Paint, Bouncing Logo, Tilemap, RPG

### TAL Compiler
- Structured language → ternary assembly
- if_eq/if_ne, inc/dec/add/sub, draw/clear pixel
- Array access, I/O ports
- Snake game compiled to 524 instructions

### Native C Backend
- libternary.so via ctypes
- 5× speedup on ALU operations
- Auto-detection and Python fallback

### Dual OS Paths
- Legacy: os.py (342-instruction TTY shell, text display)
- SDK: os/ package (Kernel/Shell/Terminal, framebuffer display)

### PyQt6 UI Expansion
- 8 new widgets: pipeline, cache, bus, branch, performance, timeline, waveform, debugger
- Game window for SDK games
- 15+ demo programs

## GPU Expansion (v2.1.0)
- Expanded GPU from 8 cores (2 WG × 4 PEs) to 64 cores (4 WG × 16 PEs)
- Added Warp class for SIMT lockstep execution (16 warps total)
- Added shared memory and barrier synchronization per workgroup
- Added multi-stream concurrent execution
- Added 2D thread block grid dispatch
- Added parallel reduction (sum/max/min), prefix scan, transpose
- Added fused operations (fused_linear, elementwise_fused)
- Added batch dispatch for bulk processing
- Native C GPU kernels (gpu_kernels.c): matmul 27x, reduce 6.5x, fused linear 4.4x speedup
- GPU visualization: render_gpu, render_warp, render_streams
- 71 GPU tests (up from 19)
- Updated ARCHITECTURE.md, paper, diagrams

## Stats
- 27 opcodes (up from 21)
- 646 tests (up from 113)
- ~30,000 lines of code
- All tests passing

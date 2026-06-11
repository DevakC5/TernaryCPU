# Ternary CPU Architecture Specification

## Overview

The Trinary CPU is a balanced ternary computer simulation with **27 instructions, 27 opcodes**, 4 general-purpose registers, 512/10000-byte addressable memory (two configurations), full interrupt support, memory-mapped I/O, a Tensor Accelerator Coprocessor, a Fantasy Console SDK, a TAL structured-language compiler, and cycle-accurate hardware simulation (pipeline, cache, branch predictor, DMA, bus, interrupts, VRAM timing).

The system supports **dual display subsystems** — a legacy text-mode memory-mapped display (7×8 chars, VRAM 200–255) and an SDK framebuffer display (64×64 pixels, VRAM 1000–5095). **Dual OS paths** coexist: a legacy single-file TTY shell (`os.py`) and a modular `os/` package with `Kernel`/`Shell`/`Terminal` classes.

---

## 1. Registers

### General Purpose (4)

| Register | Encoding | Convention |
|----------|----------|------------|
| R0       | 0        | Primary accumulator / tensor result TID |
| R1       | 1        | Secondary register |
| R2       | 2        | General purpose |
| R3       | 3        | Always 0 (OS convention) |

### Special Purpose

| Register | Size | Description |
|----------|------|-------------|
| PC       | int  | Program counter — address of next instruction |
| SP       | int  | Stack pointer — starts at 255, grows down to 128 |
| flags    | dict | ZERO, EQUAL, GREATER, LESS (set by CMP) |

### Flag Semantics

| Flag | Set When | Notes |
|------|----------|-------|
| ZERO | CMP result is `"EQ"` | Also set by operations that produce "0" |
| EQUAL | CMP result is `"EQ"` | Synonymous with ZERO |
| GREATER | CMP result is `"GT"` | dst > src in CMP |
| LESS | CMP result is `"LT"` | dst < src in CMP |

---

## 2. Memory Model

### Memory Map — Legacy Path (default: 512 addresses)

| Range | Size | Purpose |
|-------|------|---------|
| 0–127 | 128  | General data / program storage |
| 128–199 | 72 | Stack (grows down from 255) |
| 200–255 | 56  | Video RAM (7 rows × 8 cols) |
| 256–259 | 4   | Reserved |
| 260    | 1    | Keyboard buffer |
| 261–511 | 251 | Available |

### Memory Map — SDK Framebuffer Path (extended: 10000 addresses)

| Range | Size | Purpose |
|-------|------|---------|
| 0–999   | 1000 | General data / program / stack |
| 1000–5095 | 4096 | SDK framebuffer VRAM (64×64 pixels, 9 colors) |
| 5096–8999 | 3904 | Available |
| 9000    | 1    | SDK keyboard buffer |
| 9001    | 1    | SDK keyboard state flags |
| 9002–9999 | 998 | Available |

### Memory Cell

Each cell holds a ternary string (variable length, e.g., `"0"`, `"102"`, `"-10"`). Values are stored as-is — no fixed-width encoding.

### Stack

```
Initial SP = 255

PUSH R0:  memory[SP] = R0; SP -= 1
POP R0:   SP += 1; R0 = memory[SP]

Stack overflow: SP < 128 → StackOverflowError
Stack underflow: SP >= 255 → StackUnderflowError (on POP)
```

CALL/RET use the same hardware memory stack as PUSH/POP (SP grows downward from 255, pushing return address PC+1). This means nested subroutines consume physical stack space and can trigger StackOverflowError.

---

## 3. Instruction Set

### Opcode Map (27 opcodes, 27 ternary encodings)

| Ternary | Decimal | Mnemonic | Format | Cycles | Description |
|---------|---------|----------|--------|--------|-------------|
| 000     | 0       | LOAD     | C      | 1      | Load immediate into register |
| 001     | 1       | MOV      | A      | 1      | Copy register to register |
| 002     | 2       | CLR      | B      | 1      | Set register to "0" |
| 010     | 3       | ADD      | A      | 1      | Add registers |
| 011     | 4       | SUB      | A      | 1      | Subtract registers |
| 012     | 5       | AND      | A      | 1      | Ternary AND (element-wise min) |
| 020     | 6       | OR       | A      | 1      | Ternary OR (element-wise max) |
| 021     | 7       | NOT      | B      | 1      | Ternary NOT (0↔2, 1→1) |
| 022     | 8       | CMP      | A      | 1      | Compare, set flags |
| 100     | 9       | JMP      | D      | 1      | Unconditional jump |
| 101     | 10      | JZ       | D      | 1      | Jump if ZERO or EQUAL flag |
| 102     | 11      | JNZ      | D      | 1      | Jump if NOT ZERO and NOT EQUAL |
| 110     | 12      | PUSH     | B      | 2      | Push register to stack |
| 111     | 13      | POP      | B      | 2      | Pop register from stack |
| 112     | 14      | CALL     | D      | 3      | Call subroutine |
| 120     | 15      | RET      | E      | 3      | Return from subroutine |
| 121     | 16      | HALT     | E      | 1      | Halt execution |
| 122     | 17      | MUL      | A      | 3      | Multiply registers |
| 200     | 18      | DIV      | A      | 5      | Divide registers |
| 201     | 19      | STOREM   | M      | 2      | Store register to memory address |
| 202     | 20      | LOADM    | M      | 2      | Load memory address into register |
| 203     | 21      | —        | —      | —      | (unused) |
| 204     | 22      | —        | —      | —      | (unused) |
| 205     | 23      | —        | —      | —      | (unused) |
| 206     | 24      | —        | —      | —      | (unused) |
| 207     | 25      | —        | —      | —      | (unused) |
| 208     | 26      | —        | —      | —      | (unused) |
| 209     | 27      | —        | —      | —      | (unused) |
| 210     | 28      | TVECADD  | A3     | 4      | Tensor element-wise vector add, TID → R0 |
| 211     | 29      | TMATMUL  | A3     | 20     | Tensor matrix multiply, TID → R0 |
| 212     | 30      | TDOT     | A3     | 6      | Tensor dot product, scalar → R0 |
| 220     | 31      | TACT     | B2     | 3      | Tensor activation in-place (0=step) |
| 221     | 32      | TLOADW   | L      | 10     | Load CPU memory into accelerator tensor, TID → R0 |
| 222     | 33      | TSTOREW  | S2     | 10     | Store accelerator tensor to CPU memory |

### Interrupt / System Opcodes (no ternary encoding assigned)

| Mnemonic | Format | Cycles | Description |
|----------|--------|--------|-------------|
| INT      | D      | 3      | Software interrupt |
| IRET     | E      | 3      | Return from interrupt |
| EI       | E      | 1      | Enable interrupts |
| DI       | E      | 1      | Disable interrupts |
| SETIVT   | S      | 2      | Set interrupt vector |
| SETTIMER | T      | 1      | Set timer period |

### Instruction Formats

| Format | Pattern | Example | Encoding |
|--------|---------|---------|----------|
| A (two-reg) | `OP R_dst R_src` | `ADD R0 R1` | op(3) + dst(1) + src(1) |
| B (one-reg) | `OP R_op` | `CLR R0` | op(3) + reg(1) |
| C (imm) | `OP R_dst value` | `LOAD R0 10` | op(3) + dst(1) + value(ternary) |
| D (branch) | `OP addr` | `JMP loop` | op(3) + addr(ternary) |
| E (no-op) | `OP` | `HALT` | op(3) |
| M (mem) | `OP addr R_reg` | `STOREM 33 R0` | op(3) + reg(1) + addr(ternary) |
| S (ivt) | `SETIVT int addr` | — | op(3) + int(ternary) + addr(ternary) |
| T (timer) | `SETTIMER period` | — | op(3) + period(ternary) |

### Tensor Instruction Formats

| Format | Pattern | Example | Encoding |
|--------|---------|---------|----------|
| A3 (three-reg) | `OP dst src_a src_b` | `TVECADD 0 1 2` | op(3) + dst(1) + src_a(1) + src_b(1) |
| B2 (two-operand) | `OP dst src` | `TACT 0 0` | op(3) + dst(1) + src(1) |
| L (load tensor) | `TLOADW addr rows cols` | `TLOADW 100 4 4` | op(3) + addr(ternary) + rows(ternary) + cols(ternary) |
| S2 (store tensor) | `TSTOREW tid addr` | `TSTOREW 0 100` | op(3) + tid(1) + addr(ternary) |

All tensor operands (dst, src_a, src_b, tid, type) can be immediate numbers or register names (R0–R3). When a register is specified, its value is read at runtime.

### Assembly Syntax

```
label:
    OPCODE operand operand  # inline comment
    OPCODE operand          ; also a comment
```

Labels are identifiers followed by `:`. They can be used as branch targets and CALL addresses. Comments use `#` or `;`.

---

## 4. Display System

The system provides two independent display subsystems that can be used separately or together.

### Legacy Text-Mode Display (DisplayMemoryMap)

| Property | Value |
|----------|-------|
| Address range | 200–255 (56 bytes) |
| Display size | 7 rows × 8 columns = 56 characters |
| Encoding | Ternary ASCII code (e.g., `"10010"` for `'T'` = ASCII 84) |
| Null character | Ternary `"0"` renders as space |

Each VRAM cell stores the ternary representation of an ASCII code. The `DisplayMemoryMap` reads these, converts to integers, and produces `chr(code)`. Non-printable characters render as `.`.

### SDK Framebuffer Display (Framebuffer)

| Property | Value |
|----------|-------|
| Address range | 1000–5095 (4096 bytes) |
| Display size | 64 × 64 pixels |
| Colors | 9 colors (palette-indexed, 0=black) |
| VRAM base | 1000 |
| Mapping | pixel(x,y) at memory[1000 + y * 64 + x] |

Each VRAM cell stores a ternary value 0–8 mapping to a color in the palette. The `Framebuffer` class handles pixel read/write, dirty-rect tracking, and sync to/from CPU memory.

### Pixel Display (legacy graphics)

| Property | Value |
|----------|-------|
| Resolution | 27 × 27 pixels |
| Colors | 0 = black, 1 = gray, 2 = white |
| Drawing | Bresenham line algorithm |

The `PixelDisplay` is a separate framebuffer (not memory-mapped) used by the UI for legacy graphics demos.

### Keyboard — Legacy

| Property | Value |
|----------|-------|
| Buffer address | 260 |
| Polling | CPU reads `LOADM 260 R1` |
| Value | Ternary ASCII code of most recent key |
| Acknowledge | Write `"0"` to 260 after reading |

### Keyboard — SDK

| Property | Value |
|----------|-------|
| Buffer address | 9000 |
| State address | 9001 |
| Polling | CPU reads `LOADM 9000 R1` |
| Input API | `btn(name)` / `btnp(name)` via `sdk.input` module |

The SDK keyboard at 9000–9001 supports the Fantasy Console input model, while the legacy keyboard at 260 supports the simple OS shell polling model.

---

## 5. Interrupt System

### Interrupt Vector Table (IVT)

- 8 entries (indices 0–7)
- Each entry holds an instruction address
- `INT n` triggers vector `n`

### Timer

- `SETTIMER period` sets timer interval (in CPU cycles)
- Timer decrements each step by the cycle cost
- When timer_counter ≤ 0, interrupt 0 is pended
- Pending interrupt fires when `iflag` is True

### Interrupt Flow

On interrupt (software INT or timer), the CPU **automatically saves the full context** to the hardware memory stack before jumping to the handler:

1. Push R0, R1, R2, R3 to stack (SP decrements for each)
2. Push condition flags (encoded as 3-trit string ZGE: each trit "2"=True, "0"=False)
3. Push return address (PC)

On `IRET`, the CPU restores in reverse order: pop PC, pop flags, pop R3, R2, R1, R0.

```
Stack growth during interrupt:
  SP → ... → [R0] [R1] [R2] [R3] [flags] [PC]     ← SP after push
        255  254  253  252  251    250     249
```

This means interrupt handlers **cannot communicate via registers** — any changes to R0–R3 are overwritten by IRET's restore. Handlers should use memory (STOREM/LOADM) for data shared with the main program.

### Instructions

| Instruction | Description |
|-------------|-------------|
| `EI` | Set interrupt flag (enable) |
| `DI` | Clear interrupt flag (disable) |
| `INT n` | Software interrupt: save context (R0–R3, flags, PC), jump to IVT[n], disable interrupts |
| `IRET` | Restore context (PC, flags, R3–R0), enable interrupts |
| `SETIVT n addr` | Set IVT entry n to address addr |
| `SETTIMER period` | Set timer period in cycles |

---

## 6. Execution Cycle

### Instant-Execution Mode (default)

```
1. FETCH:   instruction = program[pc]
2. DECODE:  opcode, operands = parse(instruction)
3. EXECUTE: perform opcode operation
4. UPDATE:  pc += 1 (unless branch/halt/interrupt)
5. TIMER:   timer_counter -= cycle_cost
6. INTERRUPT: if pending and iflag, push PC, jump to handler
```

### Realistic Timing Mode (`CPU(realistic_timing=True)`)

In realistic timing mode, each `step()` advances one clock cycle. Instructions flow through a 5-stage pipeline and the CPU integrates:

- **Clock**: Cycle counter, frequency, period timing
- **Pipeline**: 5-stage IF→ID→EX→MEM→WB with bubbles, flushes, and ASCII visualization
- **Hazard Unit**: RAW hazard detection, forwarding paths, stall insertion
- **Cache**: Direct-mapped L1 cache with hit/miss tracking and write-back
- **Branch Predictor**: Static + 2-bit saturating counters with accuracy tracking
- **Bus**: Shared system bus with priority arbitration and contention modeling
- **DMA**: Concurrent memory-to-memory transfers interleaved with CPU execution
- **VRAM Controller**: Bandwidth limits, scanline timing, frame sync
- **Interrupt Controller**: 8-line priority controller with masking and nesting
- **Profiler**: CPI, IPC, cache hit/miss rates, branch accuracy, CSV export

### Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                   CPU EXECUTION CYCLE (5-stage)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────┐ │
│   │  FETCH  │ → │  DECODE │ → │ EXECUTE │ → │ MEMORY  │ → │ WRITE│ │
│   │   (IF)  │   │  (ID)   │   │  (EX)   │   │  (MEM)  │   │ (WB) │ │
│   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────┘ │
│        │              │              │              │          │      │
│        ▼              ▼              ▼              ▼          ▼      │
│   PC→inst       Decode op     ALU/accel/    Memory R/W      Reg     │
│   fetch         + operands    branch/ctrl   (+ cache)      write   │
│                                                                     │
│   Hazard Unit (forwarding, stalling) ← RAW detection               │
│   Branch Predictor (flush on mispredict)                            │
│   DMA (concurrent transfers interleaved) ← Bus arbitration          │
└─────────────────────────────────────────────────────────────────────┘
```

### Execution Example

```
Program:
   0: LOAD R0 10
   1: LOAD R1 12
   2: ADD R0 R1
   3: HALT

Step  PC  Instruction      R0   R1   R2   Action
───── ─── ──────────────── ──── ──── ──── ───────────────────
  0    0  LOAD R0 10       10   0    0    R0 ← ternary("10")
  1    1  LOAD R1 12       10   12   0    R1 ← ternary("12")
  2    2  ADD R0 R1        22   12   0    ADD: 3+5=8 → "22"
  3    3  HALT             22   12   0    halted = True
```

---

## 7. Number Representation

### Representation

- Positive numbers: standard ternary (e.g., `"10"` = 3, `"22"` = 8)
- Negative numbers: signed-magnitude with leading `-` (e.g., `"-10"` = −3)
- Zero: `"0"`

### Conversion

```python
ternary_to_decimal("102")    → 11
ternary_to_decimal("-10")    → -3
decimal_to_ternary(11)       → "102"
decimal_to_ternary(-3)       → "-10"
```

### Digit Efficiency

Ternary is more digit-efficient than binary:
- Value 1000: binary = `1111101000` (10 digits), ternary = `1101001` (7 digits)
- Average savings: ~37% fewer digits

---

## 8. Addition Paths

### Native Ternary (adder.py)

- Works only with non-negative strings of '0','1','2'
- Full-adder chain: each position adds a+b+carry
- Returns (sum_string, final_carry)

### Native Signed-Magnitude Arithmetic (arithmetic.py)

- Used by the CPU ALU for all signed arithmetic
- Implements sign-magnitude logic natively without decimal conversion:
  - **ADD**: compares magnitudes, routes to ripple-carry adder (same signs) or magnitude subtractor (opposite signs)
  - **SUB**: negates second operand, delegates to ADD
  - **MUL**: extracts signs, multiplies magnitudes via digit-by-digit + ripple-carry summation
  - **DIV**: extracts signs, long division on magnitudes
- Operates entirely on ternary strings with leading `-` for negatives
- The ripple-carry adder (`adder.py`) handles the non-negative magnitude core

### When Each Is Used

| Context | Path |
|---------|------|
| ALU ADD/SUB/MUL/DIV | arithmetic.py (native signed-magnitude) |
| Magnitude arithmetic | adder.py (ripple-carry, non-negative only) |
| CPU PUSH/POP | Memory (no arithmetic) |

---

## 9. Accelerator Coprocessor

The **Ternary Tensor Accelerator** (`src/trinary/accelerator/`) is a hardware-accelerated coprocessor integrated with the CPU via 6 tensor ISA opcodes. It provides SIMD vector processing, matrix multiplication, dot product, activation functions, and tensor memory management.

### Architecture

```
TernaryTensorAccelerator
├── TensorMemory (64 slots, variable-shape tensors)
├── SIMDProcessor (4+ lanes, element-wise ops)
├── TensorCore (matrix multiply engine)
└── Cycles / stats tracking
```

### CPU Tensor ISA

| Instruction | Format | Description |
|-------------|--------|-------------|
| `TLOADW addr rows cols` | L | Load CPU memory at `addr` into accelerator tensor; TID stored in R0 |
| `TSTOREW tid addr` | S2 | Store accelerator tensor `tid` to CPU memory at `addr` |
| `TVECADD dst src_a src_b` | A3 | Element-wise vector add; result TID in R0 |
| `TMATMUL dst src_a src_b` | A3 | Matrix multiply; result TID in R0 |
| `TDOT src_a src_b` | A3 | Dot product; scalar result in R0 (ternary-encoded) |
| `TACT tid type` | B2 | In-place activation (type 0 = step) |

Tensor operands accept immediate numbers or register names (R0–R3). When a register is specified, its current value is used. The result TID is written to R0 in ternary encoding.

### GPU Mode

A simulated GPU (`gpu.py`) extends the accelerator model with a four-level hierarchy:
- **ProcessingElement**: Individual trit-processing units with local memory and `active` state
- **Warp**: SIMT execution group — PEs in a warp execute the same instruction in lockstep
- **Workgroup** (Thread Block): Groups of warps sharing local memory, with barrier synchronization
- **TernaryGPU**: Full GPU with configurable `num_workgroups × pes_per_wg` cores (default: 4×16 = 64 cores, 16 warps)

Additional features:
- **Streams**: Multi-stream concurrent kernel execution
- **Grid dispatch**: 2D thread block grid model (`dispatch_grid`)
- **Parallel matmul**: Uses all PEs per workgroup, each computing different columns
- **Reduction**: Parallel sum/max/min across all PEs
- **Prefix scan**: Inclusive scan across data
- **Fused operations**: `fused_linear` (matmul+bias+activation), `elementwise_fused` (chained ops)
- **Native C acceleration**: `gpu_kernels.c` provides ~27x speedup for matmul, ~6.5x for reduction

### Visualization

ASCII rendering tools in `viz.py`:
- `render_simd_lanes()` — SIMD lane activity
- `render_tensor_matrix()` — 2D tensor data
- `render_matmul()` — matrix multiplication stages
- `render_packed_trits()` — packed storage layout
- `render_accelerator()` — accelerator state overview
- `render_pipeline()` — accelerator pipeline stages
- `render_gpu()` — full GPU architecture with workgroup/warp/PE hierarchy
- `render_warp()` — individual warp state
- `render_streams()` — stream queue/completion status

---

## 10. Hardware Simulation (`src/trinary/hardware/`)

Cycle-accurate hardware microarchitecture for educational computer architecture simulation. All components are optional — enabled via `CPU(realistic_timing=True)`.

### Modules

| Module | Class | Function |
|--------|-------|----------|
| `clock.py` | `Clock` | Cycle counter, frequency, period timing |
| `pipeline.py` | `Pipeline` / `PipelineStage` | 5-stage IF→ID→EX→MEM→WB, bubbles, flushes, ASCII viz |
| `hazards.py` | `HazardUnit` | RAW hazard detection, forwarding paths, stall insertion |
| `cache.py` | `Cache` / `CacheLine` / `CacheSet` | N-way set-associative L1, LRU replacement, hit/miss tracking, write-back |
| `branch_predictor.py` | `BranchPredictor` | Static + 2-bit saturating counters |
| `bus.py` | `Bus` / `BusRequest` | Shared system bus, burst transfers, split transactions, priority arbitration, contention |
| `dma.py` | `DMA` / `DMATransfer` | Async memory-to-memory transfers, concurrent with CPU |
| `vram_controller.py` | `VRAMController` | Bandwidth limits, scanline timing, frame sync |
| `interrupts.py` | `InterruptController` | 8-line priority controller, masking, nesting |
| `profiler.py` | `Profiler` | CPI, IPC, cache rates, branch accuracy, CSV export |

### Realistic Timing Usage

```python
from trinary.cpu import CPU
cpu = CPU(realistic_timing=True)
cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])
cpu.run(verbose=False)
print(cpu.clock.cycle)
print(cpu.profiler.report())
print(cpu.pipeline.visualize(cycle=5))
```

---

## 11. Fantasy Console SDK (`src/trinary/sdk/`)

A Fantasy Console development framework built on top of the ternary CPU. Provides a modern game-development API inspired by PICO-8 and TIC-80.

### Public API

| Function | Description |
|----------|-------------|
| `cls(color)` | Clear screen to color (0–8) |
| `spr(sprite, x, y, color)` | Draw sprite at position |
| `btn(name)` | Check if button is held |
| `btnp(name)` | Check if button was just pressed |
| `print_text(text, x, y, color)` | Render text using sprite font |
| `pixel(x, y, color)` | Set a single pixel |
| `rect(x, y, w, h, color)` | Draw filled rectangle |
| `sfx(name)` | Play sound effect |
| `poll_input()` | Sample keyboard state |
| `load_cartridge(cart)` | Load a cartridge |
| `run_demo(name)` | Run a built-in demo |

### Engine / Runtime

- **Engine**: Core game loop — manages sprites, tilemaps, animation, audio, input, and framebuffer
- **Runtime**: Orchestrates Engine + optional CPU execution per frame

### Cartridge Format

Sprites, tilemaps, and game code packaged in a `Cartridge` class:
- `sprites`: List of `Sprite` objects (8×8 pixel patterns)
- `tilemap`: `TileMap` with named layers and 2D tile data
- `code`: Optional TAL or assembly source

### Demos

| Name | Description |
|------|-------------|
| pong | Classic Pong |
| snake | Snake game (TAL-compiled CPU assembly) |
| breakout | Breakout clone |
| particles | Particle system demo |
| paint | Drawing program |
| bouncing_logo | Bouncing logo animation |
| tilemap | Tilemap scrolling demo |
| rpg | RPG overworld demo |

---

## 12. TAL Compiler (`src/trinary/tal.py`)

TAL (Ternary Assembly Language) compiles a compact structured language into ternary CPU assembly. It is a higher-level alternative to writing raw assembly.

### Features

- **Variables**: `var name @address` — named memory locations
- **Constants**: `const name = value` — named constants
- **Labels**: `name:` with optional `label name:` prefix
- **Arithmetic**: `inc`, `dec`, `add`, `sub` on variables
- **Control flow**: `if_eq`, `if_ne` with labels
- **I/O**: `load`/`write` port operations
- **Display**: `draw`/`clear` pixel operations
- **Arrays**: `body_x`/`body_y` circular buffer access (used by Snake)
- **Address constants**: `@addr` notation resolved during compilation

### Compilation Flow

```
TAL source → TALCompiler → Ternary CPU assembly → Assembler → Machine code
```

The Snake game uses TAL-compiled CPU assembly (524 instructions). The `TALSnake` class is a drop-in for `CPUSnake` via `init()`/`update()`/`render()`/`shutdown()`.

---

## 13. Dual OS Paths

Two operating system implementations coexist.

### Legacy OS (`os.py`)

- Single file, TTY-style shell
- CPU default memory (512 addresses)
- Legacy text-mode display (200–255, 7×8 chars)
- Keyboard at address 260
- Minimal command set
- Entry: `python -m trinary.os`

### Modular OS (`os/` package)

| Module | Class/Function | Description |
|--------|----------------|-------------|
| `kernel.py` | `Kernel` | OS kernel — program loading, syscall dispatch, process state |
| `shell.py` | `Shell` | Interactive shell — command parsing, I/O routing |
| `terminal.py` | `Terminal` | Terminal emulator — cursor, text rendering, scrolling |
| `syscalls.py` | `Syscalls` | System call interface — clear, print, input, file ops |
| `commands.py` | `COMMANDS` | Built-in command registry |
| `text_renderer.py` | `TextRenderer` | Bitmap font rendering on framebuffer |
| `boot.py` | `boot_sequence()` | Boot splash and initialization |
| `constants.py` | VERSION, COLORS, etc. | OS constants |
| `program_loader.py` | `ProgramLoader` | Load and verify programs from memory |

The modular OS uses the SDK framebuffer display (1000–5095, 64×64 pixels) and keyboard (9000–9001). It provides a richer shell experience with bitmap fonts, color support, and an extensible command system.

---

## 14. Complete System Stack

```
┌────────────────────────────────────────────────────────────────────┐
│  APPLICATION LAYER                                                 │
│  (OS Shell, Demo Programs, User Code, Fantasy Console Games)      │
├────────────────────────────────────────────────────────────────────┤
│  TAL COMPILER                    │  FANTASY CONSOLE SDK           │
│  (structured lang → assembly)   │  (Engine, Runtime, Cartridge)  │
├────────────────────────────────────────────────────────────────────┤
│  ASSEMBLER                                                         │
│  (two-pass: labels → addresses, branch resolution)                │
├────────────────────────────────────────────────────────────────────┤
│  MACHINE CODE ENCODER / DECODER                                    │
│  (assembly ↔ ternary opcode strings, 27 opcodes)                  │
├────────────────────────────────────────────────────────────────────┤
│  CPU                                                               │
│  (fetch-decode-execute, 27 opcodes, 4 regs, 512/10000B RAM)      │
├──────────────────────────────┬─────────────────────────────────────┤
│  ACCELERATOR COPROCESSOR     │  HARDWARE SIMULATION               │
│  (TensorMemory, SIMD,        │  (Pipeline, Cache, Branch Pred,   │
│   TensorCore, GPU mode,      │   DMA, Bus, Interrupts, VRAM,     │
│   Visualization)             │   Profiler, Clock)                 │
├──────────────────────────────┴─────────────────────────────────────┤
│  ALU  │  REGISTERS  │  MEMORY  │  DISPLAY  │  ARITHMETIC         │
│  (ADD/│  (R0–R3)    │  (512/   │  (Text +  │  (decimal           │
│   SUB/ │             │   10000) │   Frame-  │   round-trip)       │
│   MUL/ │             │          │   buffer) │                     │
│   DIV/ │             │          │           │                     │
│   AND/ │             │          │           │                     │
│   OR/  │             │          │           │                     │
│   NOT/ │             │          │           │                     │
│   CMP) │             │          │           │                     │
├────────┴─────────────┴──────────┴───────────┴─────────────────────┤
│  conversion.py  │  logic.py  │  adder.py  │  native C backend    │
│  (base conv)    │  (gates)   │  (ripple)  │  (libternary.so)     │
└────────────────────────────────────────────────────────────────────┘
```

---

## 15. Module Dependencies

```
conversion.py          (foundation — no trinary deps)
logic.py               (foundation — no trinary deps)
    ↑
adder.py               → logic.py
arithmetic.py          → conversion.py
    ↑
alu.py                 → arithmetic.py, logic.py, conversion.py
registers.py           → conversion.py
memory.py              (standalone)
    ↑
cpu.py                 → registers.py, alu.py, memory.py, accelerator/, hardware/
assembler.py           → cpu.py (instruction definitions only)
machine.py             → assembler.py, conversion.py

display/
├── text_display.py    → conversion.py
├── framebuffer.py     → display.constants, display.palette
├── constants.py       (standalone — VRAM_BASE, DISPLAY_WIDTH/HEIGHT)
├── palette.py         (standalone — color definitions)
├── keyboard.py        (standalone — key mapping)
├── display_controller.py  → framebuffer.py, text_display.py, keyboard.py
└── display_widget.py  (PyQt6, optional)

accelerator/
├── accelerator.py     → tensor_memory.py, simd.py, tensor_core.py, vector_ops.py
├── tensor_memory.py   (standalone — tensor storage)
├── simd.py            (standalone — SIMD processor)
├── tensor_core.py     (standalone — matrix multiply engine)
├── vector_ops.py      (standalone — trit-level operations)
├── packed_trits.py    (standalone — packed trit storage)
├── gpu.py             → processing elements, workgroups
├── instruction_set.py (standalone — opcode definitions)
├── viz.py             (standalone — ASCII renderers)
└── benchmarks.py      → accelerator.py

hardware/
├── clock.py           (standalone)
├── pipeline.py        (standalone)
├── hazards.py         (standalone)
├── cache.py           (standalone)
├── branch_predictor.py (standalone)
├── bus.py             (standalone)
├── dma.py             → memory.py, bus.py
├── vram_controller.py (standalone)
├── interrupts.py      (standalone)
├── profiler.py        (standalone)
└── timing.py          (standalone — latency tables)

sdk/
├── engine.py          → sprites.py, tilemap.py, animation.py, audio.py, input.py
├── runtime.py         → engine.py
├── api.py             → engine.py, sprites.py, input.py, audio.py, runtime.py
├── sprites.py         (standalone)
├── tilemap.py         (standalone)
├── animation.py       (standalone)
├── audio.py           (standalone)
├── input.py           (standalone)
├── cartridge.py       (standalone)
└── constants.py       (standalone)

tal.py                 → conversion.py

os/  (modular)
├── kernel.py          → shell.py, terminal.py, syscalls.py, program_loader.py
├── shell.py           → terminal.py, commands.py
├── terminal.py        → text_renderer.py, constants.py
├── syscalls.py        → terminal.py, text_renderer.py
├── commands.py        → syscalls.py
├── text_renderer.py   → constants.py
├── program_loader.py  (standalone)
├── boot.py            → constants.py, text_renderer.py
└── constants.py       (standalone)

os.py (legacy)         → cpu.py, assembler.py, conversion.py, display.py
demo_programs.py       → cpu.py, assembler.py, display.py
demo_games.py          → sdk/, accelerators/demos/
benchmark.py           → cpu.py, assembler.py, adder.py, conversion.py
native_backend.py      → ctypes, libternary.so
native_benchmark.py    → cpu.py, native_backend.py
snake_game.py          → tal.py
diagrams.py            (standalone)
```

---

## Revision History

- **v2.0.0 (2026-05-26)**: Full architecture expansion
  - 27 opcodes (added 6 tensor ops: TVECADD/TMATMUL/TDOT/TACT/TLOADW/TSTOREW)
  - Ternary Tensor Accelerator Coprocessor (SIMD, tensor core, GPU mode, visualization)
  - Cycle-accurate hardware simulation (pipeline, cache, branch predictor, DMA, bus, VRAM, interrupts, profiler)
  - Fantasy Console SDK (Engine, Runtime, Cartridge format, 8 demo games)
  - TAL structured-language compiler
  - SDK framebuffer display (64×64 pixels, 9 colors, VRAM 1000–5095)
  - Modular OS package (`os/` with Kernel/Shell/Terminal)
  - Dual display subsystems (legacy text + SDK framebuffer)
  - Dual OS paths (legacy `os.py` + modular `os/` package)
  - Native C backend (`libternary.so`, auto-detected with Python fallback)
  - Realistic timing mode (5-stage pipeline, hazards, forwarding, stalls)

- **v1.1.0 (2026-05-18)**: Feature expansion
  - 26 opcodes (added MUL, DIV, STOREM, LOADM, INT, IRET, EI, DI, SETIVT, SETTIMER)
  - 512-byte memory
  - Memory-mapped display (200–255)
  - Keyboard buffer (260)
  - Hardware timer and interrupt system
  - Minimal OS shell
  - PyQt6 desktop UI

- **v1.0.0 (2026-05-17)**: Initial specification
  - 4 general-purpose registers
  - 17 opcodes
  - 256-word memory
  - Two-pass assembler with labels
  - Variable-length ternary machine code

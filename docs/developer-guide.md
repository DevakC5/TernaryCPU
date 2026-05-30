# Developer Guide

---

## 1. Development Setup

### Prerequisites

- Python 3.10+
- pip
- C compiler (gcc/clang) for native backend

### Install

```sh
git clone <repo>
cd trinary
pip install -e .
```

This installs `trinary` as a development package. Changes to source files take effect immediately (no re-install needed).

### Optional: PyQt6 for UI

```sh
pip install pyqt6
```

---

## 2. Running Tests

```sh
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_cpu.py -v

# Run specific test
python -m pytest tests/test_cpu.py::TestCPU::test_add -v

# Run by keyword
python -m pytest tests/ -k "cmp" -v

# Run without verbose
python -m pytest tests/ -q

# Run with coverage
pip install pytest-cov
python -m pytest tests/ --cov=src/trinary
```

### Test Organization

| File | Tests | Focus |
|------|-------|-------|
| `test_conversion.py` | 10 | Trit, decimal↔ternary↔binary, validation |
| `test_arithmetic.py` | 12 | add/sub/mul/div with positives and negatives |
| `test_alu.py` | 10 | All 8 ALU operations (+ edge cases) |
| `test_assembler.py` | 5 | Labels, comments, inline `#` and `;` |
| `test_cpu.py` | 24 | All 26 opcodes, flags, stack, interrupts, timer |
| `test_cpu_stress.py` | 8 | Nested calls, heavy loops, random sequences |
| `test_display.py` | 20 | DisplayMemoryMap, PixelDisplay, keyboard, STOREM/LOADM |
| `test_accelerator.py` | 70 | Accelerator tensor ops |
| `test_gpu.py` | 71 | GPU mode, warps, streams, native C kernels, visualization |
| `test_pipeline.py` | 19 | Clock, pipeline, hazards, timing |
| `test_cache.py` | 10 | Cache hit/miss, write-back |
| `test_branch_predictor.py` | 7 | Static + 2-bit saturating predictors |
| `test_bus.py` | 7 | System bus, arbitration |
| `test_dma.py` | 7 | DMA transfers |
| `test_interrupts.py` | 8 | Interrupt controller |
| `test_vram.py` | 7 | VRAM timing, bandwidth |
| `test_profiler.py` | 9 | CPI, IPC, profiler reports |
| `test_realistic_cpu.py` | 9 | CPU integration |
| `test_sdk.py` | 50 | Fantasy Console SDK |
| `test_os.py` | 38 | OS shell and kernel |
| `test_tensor_core.py` | 12 | Tensor core operations |
| `test_simd.py` | 11 | SIMD processor |
| `test_packed_trits.py` | 20 | Packed trit storage |
| `test_vector_ops.py` | 12 | Vector operations |
| `test_native_backend.py` | 11 | Native C bridge |
| `test_display_framebuffer.py` | 20 | Framebuffer display |
| `test_viz_engine.py` | 22 | Visualization engine |
| `test_cpu_accelerator.py` | 11 | CPU-accelerator integration |

Total: **594 tests**

---

## 3. Code Organization

### Module Dependency Graph

```
conversion.py              (foundation)
    ↑
logic.py                   (foundation)
    ↑
adder.py                   → logic.py
arithmetic.py              → conversion.py
    ↑
alu.py                     → arithmetic.py, logic.py, conversion.py
registers.py               → conversion.py
memory.py                  (standalone)
    ↑
cpu.py                     → registers.py, alu.py, memory.py, interrupts.py
assembler.py               (standalone, cpu.py demo only)
machine.py                 → assembler.py, conversion.py
display/                   → conversion.py (lazy)
├── __init__.py
├── memory_map.py
├── pixel_display.py
├── framebuffer.py
└── keyboard.py
os/                        → cpu.py, assembler.py, display/
├── __init__.py
├── kernel.py
├── shell.py
└── terminal.py
os.py                      (legacy TTY shell, single file)
sdk/                       → cpu.py, memory.py, conversion.py, display/
├── __init__.py
├── engine.py
├── runtime.py
├── cartridge.py
└── assets.py
accelerator/               → cpu.py
├── __init__.py
├── accelerator_core.py
├── gpu.py
├── viz.py
├── simd.py
├── packed_trits.py
├── tensor_core.py
└── vector_ops.py
hardware/                  → cpu.py
├── __init__.py
├── clock.py
├── pipeline.py
├── hazards.py
├── cache.py
├── branch_predictor.py
├── bus.py
├── dma.py
├── vram_controller.py
├── interrupts.py
└── profiler.py
native/                    (C extension)
├── alu.c
├── ternary.h
├── Makefile
└── build.sh
native_backend.py          → ctypes, libternary.so
tal.py                     → assembler.py, conversion.py
demo_programs.py           → cpu.py, assembler.py, display.py
demo_games.py              → sdk/, cpu.py
benchmark.py               → cpu.py, assembler.py, adder.py, conversion.py
diagrams.py                (standalone)
```

Core execution path (fast mode — instant execution):

```
assembly string
  → CPU.execute_instruction()
    → registers.load/store() for register ops
    → alu.alu() for ALU operations
      → arithmetic.add_ternary() etc. (decimal round-trip)
    → memory.store/load() for STOREM/LOADM/PUSH/POP
```

Core execution path (realistic timing — cycle-accurate):

```
assembly string
  → CPU.step() [1 cycle]
    → Clock.tick()
    → Pipeline.cycle()
      → IF: fetch instruction from program memory
      → ID: decode, HazardUnit.check()
      → EX: alu.alu() / register ops
      → MEM: memory access (may use Bus arbitration)
      → WB: register write-back
    → Cache lookup on memory ops
    → BranchPredictor.predict() on branches
    → InterruptController.poll()
    → DMA transfers (concurrent)
    → VRAMController.tick() (scanline timing)
    → Profiler.record()
```

---

## 4. Building the Native Extension

C native layer (`libternary.so`) accelerates ALU operations. Not required — `native_backend.py` auto-probes paths via ctypes and falls back to pure Python.

```sh
make -C src/trinary/native
# Produces src/trinary/libternary.so
```

Or use the helper script:

```sh
bash build_native.sh
```

The flag `NATIVE_AVAILABLE` in `native_backend.py` tells callers whether acceleration loaded.

---

## 5. Native C Backend

`native_backend.py` provides a ctypes bridge to `libternary.so`. When loaded, ALU operations (ADD, SUB, MUL, DIV, AND, OR, NOT, CMP) run in C instead of Python, giving ~10× speedup for arithmetic-heavy code.

```
Python CPU → native_backend.add_ternary(a, b) → C alu_add() → result
```

Usage is transparent — `cpu.py` imports `native_backend` and delegates ALU calls when `NATIVE_AVAILABLE` is `True`. Fallback to pure Python is automatic.

### Building

```sh
make -C src/trinary/native       # build libternary.so
python -m pytest tests/test_native_backend.py -v   # verify
python -m trinary.native_benchmark                  # benchmark vs Python
```

---

## 6. TAL Compiler

`tal.py` compiles a higher-level structured language into ternary CPU assembly. Supports:

- `if_eq` / `if_ne` — conditional execution
- `inc` / `dec` / `add` / `sub` — arithmetic
- `draw` / `clear` pixel — framebuffer operations
- `body_x` / `body_y` array access — circular buffer indexing
- `load` / `write` I/O ports — keyboard and display
- Address constants in `@addr` notation — resolved during compilation

Labels use `name:` syntax (not `label name:`). The snake game (`snake_game.py`) uses TAL-compiled CPU assembly (524 instructions). The `TALSnake` class is a drop-in for `CPUSnake` via `init()` / `update()` / `render()` / `shutdown()`.

### Example

```tal
body_x[head] += 1
if_eq body_x[head] 20
    body_x[head] = 0
end
```

Compiles to LOAD/ADD/STOREM/CMP/JNZ sequences targeting the framebuffer snake game.

---

## 7. Fantasy Console SDK

The `sdk/` package provides a complete Fantasy Console development environment running on the ternary CPU.

### Components

| Module | Class | Purpose |
|--------|-------|---------|
| `engine.py` | `Engine` | Game loop, frame timing, input polling |
| `runtime.py` | `Runtime` | Script execution environment, API surface |
| `cartridge.py` | `Cartridge` | Packs sprites, tilemaps, code into portable cartridges |
| `assets.py` | — | Sprite and tilemap loaders |

### Public API

| Function | Description |
|----------|-------------|
| `cls()` | Clear framebuffer |
| `spr(id, x, y)` | Draw sprite |
| `btn(id)` | Check button state |
| `btnp(id)` | Check button pressed this frame |
| `print_text(text, x, y)` | Draw text |
| `pixel(x, y, color)` | Set pixel |
| `rect(x, y, w, h, color)` | Draw filled rectangle |
| `sfx(id)` | Play sound effect |
| `poll_input()` | Read keyboard state |

### Running Demos

```sh
python -m trinary.demo_games pong
python -m trinary.demo_games snake
python -m trinary.demo_games breakout
python -m trinary.demo_games particles
python -m trinary.demo_games paint
python -m trinary.demo_games bouncing_logo
python -m trinary.demo_games tilemap
python -m trinary.demo_games rpg
```

---

## 8. Tensor Accelerator

The `accelerator/` package implements a hardware tensor coprocessor integrated with the CPU via 6 tensor ISA opcodes.

### Tensor ISA Opcodes

| Opcode | Format | Description |
|--------|--------|-------------|
| `TLOADW` | `TLOADW addr rows cols` | Load CPU memory at `addr` into accelerator tensor, TID → R0 |
| `TSTOREW` | `TSTOREW tid addr` | Store accelerator tensor to CPU memory |
| `TVECADD` | `TVECADD dst src_a src_b` | Element-wise vector add, result TID → R0 |
| `TMATMUL` | `TMATMUL dst src_a src_b` | Matrix multiply, result TID → R0 |
| `TDOT` | `TDOT src_a src_b` | Dot product, scalar result → R0 (ternary encoded) |
| `TACT` | `TACT tid type` | Activation in-place (0=step), type via reg or immediate |

Operands can be immediate numbers or registers (R0–R3). All six opcodes are supported by the CPU, assembler (`assembler.py`), and machine encoder (`machine.py`).

### Sub-modules

| Module | Description |
|--------|-------------|
| `accelerator_core.py` | Core accelerator: tensor storage, dispatch, ops |
| `gpu.py` | Simulated GPU: ProcessingElement → Warp → Workgroup → TernaryGPU hierarchy, streams, native C acceleration |
| `simd.py` | SIMD processor: vectorized arithmetic on packed trits |
| `tensor_core.py` | Tensor core: matrix multiply-accumulate primitives |
| `packed_trits.py` | Packed trit storage: 5 trits per byte |
| `vector_ops.py` | Vector operation primitives |
| `viz.py` | ASCII visualization for SIMD lanes, tensor matrices, matmul, pipelines |

---

## 9. Hardware Simulation Modules

The `hardware/` package provides cycle-accurate microarchitecture simulation. All components are optional — enabled via `CPU(realistic_timing=True)`.

| Module | Class | Function |
|--------|-------|----------|
| `clock.py` | `Clock` | Cycle counter, frequency, period timing |
| `pipeline.py` | `Pipeline` / `PipelineStage` | 5-stage IF→ID→EX→MEM→WB, bubbles, flushes, ASCII viz |
| `hazards.py` | `HazardUnit` | RAW hazard detection, forwarding paths, stall insertion |
| `cache.py` | `Cache` / `CacheLine` | Direct-mapped L1, hit/miss tracking, write-back |
| `branch_predictor.py` | `BranchPredictor` | Static + 2-bit saturating counters |
| `bus.py` | `Bus` / `BusRequest` | Shared system bus, priority arbitration, contention |
| `dma.py` | `DMA` / `DMATransfer` | Async memory-to-memory transfers, concurrent with CPU |
| `vram_controller.py` | `VRAMController` | Bandwidth limits, scanline timing, frame sync |
| `interrupts.py` | `InterruptController` | 8-line priority controller, masking, nesting |
| `profiler.py` | `Profiler` | CPI, IPC, cache rates, branch accuracy, CSV export |

### Running Hardware Tests

```sh
python -m pytest tests/test_pipeline.py -v           # 19 tests (clock, pipeline, hazards)
python -m pytest tests/test_cache.py -v               # 10 tests
python -m pytest tests/test_branch_predictor.py -v    # 7 tests
python -m pytest tests/test_dma.py -v                 # 7 tests
python -m pytest tests/test_interrupts.py -v          # 8 tests
python -m pytest tests/test_bus.py -v                 # 7 tests
python -m pytest tests/test_vram.py -v                # 7 tests
python -m pytest tests/test_profiler.py -v            # 9 tests
python -m pytest tests/test_realistic_cpu.py -v       # 9 tests
```

---

## 10. Realistic Timing Mode

`CPU(realistic_timing=True)` enables the full hardware simulation stack while remaining backward-compatible with all existing programs.

```python
from trinary.cpu import CPU
cpu = CPU(realistic_timing=True)
cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])
cpu.run(verbose=False)
print(cpu.clock.cycle)          # Cycles consumed
print(cpu.profiler.report())    # CPI, stalls, etc.
print(cpu.pipeline.visualize(cycle=5))  # ASCII pipeline
```

In realistic mode every `step()` advances exactly 1 clock cycle:

- **Clock**: `step()` = 1 cycle; `run()` advances until HALT
- **Pipeline**: Instructions flow through IF→ID→EX→MEM→WB; visualizer shows occupancy per stage
- **Branch prediction**: 2-bit saturating counters; mispredicts flush the pipeline
- **DMA**: Transfers run concurrently; memory reads/writes interleaved with CPU
- **Profiler**: Tracks cycles, instructions retired, CPI, stall breakdown, branch accuracy

Fast mode (`CPU()` default) executes each instruction in zero simulated time — identical behavior, no timing overhead.

---

## 11. Adding a New Instruction

### Step-by-step

**1. Add to `OPCODE_MAP` in `machine.py`**

```python
OPCODE_MAP = {
    ...
    "XOR": "210",  # new instruction
}
```

Ternary opcode must be a 3-trit string. Use a unique value not already mapped.

**2. Add to `OPCODES` and `CYCLES` in `cpu.py`**

```python
OPCODES = {
    ..., "XOR",
}

CYCLES = {
    ..., "XOR": 2,
}
```

**3. Implement in `cpu.execute_instruction()`**

```python
elif opcode == "XOR":
    dst, src = operands
    a = self.registers.store(dst)
    b = self.registers.store(src)
    result, _ = alu("XOR", a, b)
    self.registers.load(dst, result)
```

Or implement directly if no ALU support:

```python
elif opcode == "XOR":
    dst, src = operands
    a = t2d(self.registers.store(dst))
    b = t2d(self.registers.store(src))
    result = d2t(a ^ b)  # Python XOR
    self.registers.load(dst, result)
```

**4. Add to `encode_instruction()` in `machine.py`**

If the instruction uses an existing format (A, B, C, D, E, M), it may work automatically. Otherwise add a format handler.

**5. Write tests**

```python
def test_xor(self):
    cpu = CPU()
    cpu.load_program(["LOAD R0 12", "LOAD R1 10", "XOR R0 R1"])
    cpu.run(verbose=False)
    assert cpu.registers[0] == "22"  # 5 XOR 3 = 6
```

**6. Update opcode count in docs**

---

## 12. Adding a New ALU Operation

**1. Add to `VALID_OPERATIONS` in `alu.py`**

```python
VALID_OPERATIONS = ("ADD", "SUB", "MUL", "DIV", "AND", "OR", "NOT", "CMP", "XOR")
```

**2. Implement in `alu()`**

```python
if operation == "XOR":
    x, y = ternary_to_decimal(a), ternary_to_decimal(b)
    result = decimal_to_ternary(x ^ y)
    return (result, None)
```

**3. Connect in CPU** (see above — the CPU calls `alu("XOR", a, b)`)

**4. Write ALU tests**

```python
def test_xor(self):
    result, _ = alu("XOR", "12", "10")  # 5 XOR 3
    assert result == "22"  # 6
```

---

## 13. Testing Patterns

### Pattern 1: Simple instruction test

```python
def test_add(self):
    cpu = CPU()
    cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1"])
    cpu.run(verbose=False)
    assert cpu.registers.store("R0") == "22"
```

### Pattern 2: Step-by-step with state checks

```python
def test_push_pop(self):
    cpu = CPU()
    cpu.load_program(["LOAD R0 10", "PUSH R0", "POP R1"])
    cpu.step()  # LOAD R0 10
    assert cpu.registers.store("R0") == "10"
    assert cpu.sp == 255
    cpu.step()  # PUSH R0
    assert cpu.memory.load(255) == "10"
    assert cpu.sp == 254
    cpu.step()  # POP R1
    assert cpu.registers.store("R1") == "10"
    assert cpu.sp == 255
```

### Pattern 3: Subroutine call

```python
def test_call_ret(self):
    cpu = CPU()
    cpu.load_program([
        "LOAD R0 10",
        "CALL 4",
        "HALT",
        "LOAD R1 12",
        "RET",
    ])
    cpu.run(verbose=False)
    assert cpu.registers.store("R0") == "10"
    assert cpu.registers.store("R1") == "12"
```

### Pattern 4: Interrupt test

```python
def test_timer_interrupt(self):
    cpu = CPU()
    cpu.load_program([
        "SETIVT 0 4",       # IVT[0] → address 4
        "EI",                # Enable interrupts
        "SETTIMER 3",        # Fire every 3 cycles
        "HALT",              # Stop main
        "LOAD R0 1",         # Handler
        "IRET",              # Return
    ])
    cpu.run(verbose=False)
    assert cpu.registers.store("R0") == "1"
```

### Pattern 5: Display and keyboard

```python
def test_storem_loadm(self):
    cpu = CPU()
    cpu.load_program(["LOAD R0 11", "STOREM 200 R0", "LOADM 200 R1"])
    cpu.step()  # LOAD
    cpu.step()  # STOREM: mem[200] = "11"
    assert cpu.memory.load(200) == "11"
    cpu.step()  # LOADM
    assert cpu.registers.store("R1") == "11"
```

### Pattern 6: Realistic timing

```python
def test_realistic_cpu(self):
    cpu = CPU(realistic_timing=True)
    cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])
    cpu.run(verbose=False)
    assert cpu.registers.store("R0") == "22"
    assert cpu.clock.cycle > 0
    assert cpu.profiler.instructions_retired > 0
```

---

## 14. Common Pitfalls

### CMP + JZ Interaction

The CMP instruction sets ZERO and EQUAL flags. JZ jumps if EITHER flag is True. JNZ jumps only if BOTH are False.

```asm
CMP R0 R1    # R0 = "0", R1 = "1012"
JZ done      # Will jump if a == b (ZERO/EQUAL True)
             # WON'T jump just because a == "0"
```

### Two Addition Paths

- `arithmetic.py` (decimal round-trip): used by CPU ALU. Handles negatives.
- `adder.py` (native base-3): standalone. Only handles non-negative. Not used by CPU.

The CPU's ADD uses `arithmetic.add_ternary()`, NOT the ripple-carry adder.

### Two Separate Stacks

- `PUSH/POP`: memory-based, address range 128–255, SP register
- `CALL/RET`: Python list-based (call_stack), entirely separate

Do NOT use POP to return from a subroutine. Use RET. Do NOT use CALL to push data. Use PUSH.

### Zero vs "0"

The ternary string `"0"` represents the value zero. The integer `0` is never used as a register value. All register values are ternary strings.

### STOREM Address Modes

```asm
STOREM 33 R0      # Literal address: store at memory address 33
STOREM R2 R0      # Register address: store at address = value(R2)
```

When using register-based addressing, the register's VALUE (converted to decimal) is the memory address.

### Dual Display Systems

| Layer | VRAM range | Display | Keyboard | Used by |
|-------|-----------|---------|----------|---------|
| Legacy (text) | 200–255 | 7×8 chars via `DisplayMemoryMap` | 260 | `os.py`, `demo_programs.py`, `cpu.py` default |
| SDK (framebuffer) | 1000–5095 | 64×64 pixel `Framebuffer` | 9000–9001 | `os/` package, `sdk/`, `demo_games.py`, PyQt6 |

For framebuffer SDK path, create CPU with larger memory: `CPU(memory=Memory(10000))`.

---

## 15. Debugging Techniques

### CPU Trace

```python
cpu = CPU()
cpu.load_program([...])
cpu.run(verbose=True)  # Print every instruction
```

### Memory Dump

```python
cpu.memory.dump(200, 256)    # Dump VRAM region
cpu.memory.dump_hex(0, 64)   # Hex-formatted dump
```

### Register State

```python
print(cpu.registers.dump())
print(f"PC={cpu.pc} SP={cpu.sp}")
print(f"Flags: {cpu.flags}")
```

### Stepping Manually

```python
while not cpu.halted:
    instr = cpu.program[cpu.pc]
    print(f"PC={cpu.pc}: {instr}")
    cpu.step()
    print(f"  R0={cpu.registers.store('R0')} R1={cpu.registers.store('R1')}")
```

### Pipeline Visualization

```python
cpu = CPU(realistic_timing=True)
cpu.load_program([...])
cpu.run(verbose=False)
print(cpu.pipeline.visualize(cycle=5))
```

### Profiler Report

```python
cpu = CPU(realistic_timing=True)
cpu.load_program([...])
cpu.run(verbose=False)
print(cpu.profiler.report())
cpu.profiler.export_csv("profile.csv")
```

---

## 16. Performance Considerations

- Pure Python simulation — not designed for raw speed
- `DIV` is the most expensive instruction (5 cycles in fast mode, variable in realistic mode)
- Decimal round-trip in arithmetic requires string conversion per operation
- The ripple-carry adder in `adder.py` is educational, not used by the CPU
- Memory is a Python dict, O(1) access
- **Native C backend** (`libternary.so`) accelerates ALU ops ~10× via ctypes — auto-loaded when available
- **Realistic timing mode** adds overhead proportional to pipeline depth and cache simulations
- 594 tests complete in ~1.5s — fast enough for development
- For benchmark comparisons: `python -m trinary.native_benchmark`

---

## 17. Contributing Guidelines

1. **Tests first**: Add a failing test before implementing a feature
2. **Follow conventions**: Study existing code for patterns (error handling, naming, documentation)
3. **Keep modules focused**: `conversion.py` does conversions, `alu.py` does ALU, etc.
4. **Document with examples**: Every instruction should have an assembly example
5. **Update docs**: When adding instructions or changing behavior, update ARCHITECTURE.md, instruction-set.md, AGENTS.md, and this guide
6. **Hardware modules**: New hardware components should inherit the `realistic_timing` opt-in pattern — zero impact on default fast-mode execution

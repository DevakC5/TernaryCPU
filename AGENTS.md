# AGENTS.md

## Project

Ternary (base-3) computer simulation — logic gates, ALU, 26-opcode CPU, two-pass assembler, machine-code encoder, dual memory-mapped display systems, native C acceleration, Fantasy Console SDK (sprites/tilemap/audio/animation), PyQt6 desktop UI, cycle-accurate microarchitecture simulation (pipeline, cache, branch predictor, bus, DMA, interrupts, VRAM timing).

## Setup & commands

```sh
pip install -e .                              # one-time install
python -m pytest tests/ -v                    # 572 tests
python -m pytest tests/test_os.py -v          # OS tests
python -m pytest tests/test_cpu.py -v         # CPU instruction tests
python -m pytest tests/test_sdk.py -v         # Fantasy Console SDK tests
python -m pytest tests/test_native_backend.py -v   # native C bridge tests
python -m pytest tests/ -k "cmp" -v           # keyword filter
python -m trinary.os                          # legacy OS shell (TTY)
python -m trinary.ui.app                      # PyQt6 UI (needs PyQt6)
python -m trinary.native_benchmark            # benchmark native C vs Python
python -m trinary.demo_games <name>           # SDK demos: pong/snake/breakout/particles/paint/bouncing_logo/tilemap/rpg
python test_snake_tal.py                      # TAL-compiled snake CPU test (13 frames)
```

## Native backend

C native layer (`libternary.so`) accelerates ALU ops. Not required — `native_backend.py` auto-probes paths via ctypes and falls back to pure Python. The flag `NATIVE_AVAILABLE` tells callers whether acceleration loaded.

```sh
make -C src/trinary/native                    # produces src/trinary/libternary.so
bash build_native.sh                          # alternative
```

## Architecture — two display/OS subsystems

| Layer | VRAM range | Display | Keyboard | Used by |
|-------|-----------|---------|----------|---------|
| **Legacy** (text) | 200–255 | 7×8 chars via `DisplayMemoryMap` | 260 | `os.py`, `demo_programs.py`, `cpu.py` default |
| **SDK** (framebuffer) | 1000–5095 | 64×64 pixel `Framebuffer` | 9000–9001 | `os/` package, `sdk/`, `demo_games.py`, PyQt6 |

Two OS paths coexist: `os.py` (legacy TTY shell, single file) and `os/` package with `Kernel`/`Shell`/`Terminal` classes. Both are live.

Display was refactored from a single `display.py` into the `display/` package — imports are `from trinary.display import ...`.

## Key gotchas

- **CPU default**: `CPU()` creates `Memory(512)`. For framebuffer SDK path, pass `CPU(memory=Memory(10000))` — keyboard at 9000, VRAM at 1000–5095.
- **CPU realistic timing**: `CPU(realistic_timing=True)` enables cycle-accurate pipeline, cache, branch prediction, DMA, bus, interrupt controller, and profiler. All existing programs and tests work identically in fast mode (default).
- **Dual stacks**: `sp` register (PUSH/POP, memory-based, grows down 255→128) vs `call_stack` list (CALL/RET, Python list).
- **Two addition paths**: `adder.py` (native base-3 ripple-carry, 0–2 only, no negatives) vs `arithmetic.py` (decimal round-trip, handles negatives). ALU uses `arithmetic.add_ternary`.
- **Signed-magnitude negatives**: leading `-` (e.g., `"-10"` = −3 decimal). Not balanced ternary.
- **`machine.py`** encodes 27 opcodes — tensor ops `TVECADD(210)`/`TMATMUL(211)`/`TDOT(212)`/`TACT(220)`/`TLOADW(221)`/`TSTOREW(222)` added. Still no mapping for INT/IRET/EI/DI/SETIVT/SETTIMER.
- **`tests/legacy/`** excluded by pytest (`norecursedirs` in `pyproject.toml`); contains only `.bak` files.
- **CPU tests** use `cpu.run(verbose=False)` to suppress output.
- **Inline comments**: `#` and `;` both work (handled by `assembler.parse_line`).
- **Memory hooks**: `memory.register_write_hook(start, end, callback)` for VRAM auto-sync.
- **No CI/lint/typecheck config** — `pytest` is the only enforcement.
- **conftest.py** does not exist; no pytest plugins.

## TAL compiler (`src/trinary/tal.py`)

Compiles higher-level structured language into ternary CPU assembly. Supports `if_eq`/`if_ne`, `inc`/`dec`/`add`/`sub`, `draw`/`clear` pixel, `body_x`/`body_y` array access, `load`/`write` I/O ports. Labels use `name:` (not `label name:`). Address constants in `@addr` notation resolved during compilation.

Snake game (`snake_game.py`) uses TAL-compiled CPU assembly (524 instructions). The `TALSnake` class is a drop-in for `CPUSnake` via `init()`/`update()`/`render()`/`shutdown()`. Body circular buffer at mem 20–147.

## SDK/Fantasy Console (`src/trinary/sdk/`)

`Engine` + `Runtime` host games. Public API: `cls`, `spr`, `btn`, `btnp`, `print_text`, `pixel`, `rect`, `sfx`, `poll_input`. Cartridge format (`Cartridge` class) packs sprites, tilemaps, code. Demos live in `demo_games.py` — run via `python -m trinary.demo_games <name>`.

## Tensor Accelerator Coprocessor (`src/trinary/accelerator/`)

Hardware-accelerated tensor operations integrated with the CPU. 6 tensor ISA opcodes supported by CPU, assembler, and machine encoder.

### CPU tensor ISA

| Opcode | Format | Description |
|--------|--------|-------------|
| `TLOADW` | `TLOADW addr rows cols` | Load CPU memory at `addr` into accelerator tensor, TID → `R0` |
| `TSTOREW` | `TSTOREW tid addr` | Store accelerator tensor to CPU memory |
| `TVECADD` | `TVECADD dst src_a src_b` | Element-wise vector add on accelerator, result TID → `R0` |
| `TMATMUL` | `TMATMUL dst src_a src_b` | Matrix multiply on accelerator, result TID → `R0` |
| `TDOT` | `TDOT src_a src_b` | Dot product, scalar result → `R0` (ternary encoded) |
| `TACT` | `TACT tid type` | Activation in-place (0=step). `type` via reg or immediate |

Operands can be immediate numbers or registers (R0-R3). The `R0` register reads the result TID (converted via `decimal_to_ternary`).

### Accelerator test commands

```sh
python -m pytest tests/test_accelerator.py -v       # 70 unit tests (accelerator)
python -m pytest tests/test_cpu_accelerator.py -v    # 11 CPU integration tests
python -m pytest tests/test_gpu.py -v                # 19 GPU mode + viz tests
python -m pytest tests/test_packed_trits.py -v       # 20 packed storage tests
python -m pytest tests/test_tensor_core.py -v        # 12 tensor core tests
python -m pytest tests/test_simd.py -v               # 11 SIMD processor tests
python -m pytest tests/test_vector_ops.py -v         # 12 vector ops tests
```

### GPU mode (`gpu.py`)

Simulated GPU with `ProcessingElement` → `Workgroup` → `TernaryGPU` hierarchy. Supports kernel dispatch, tensor pipelines, and parallel matmul. `PEs_per_wg × n_workgroups` processing elements.

### Visualization (`viz.py`)

ASCII rendering for SIMD lanes, tensor matrices, matmul, packed storage, accelerator state, and pipelines.

```python
from trinary.accelerator import render_simd_lanes, render_tensor_matrix, render_matmul
print(render_simd_lanes([2, 0, 1, 2]))
print(render_matmul([[2, 0], [0, 2]], [[2, 0], [0, 2]], result=[[2, 0], [0, 2]]))
```

## Hardware Simulation Subsystem (`src/trinary/hardware/`)

Cycle-accurate hardware microarchitecture for educational computer architecture simulation. All components are optional — enabled via `CPU(realistic_timing=True)`.

### Hardware modules

| Module | Class | Function |
|--------|-------|----------|
| `clock.py` | `Clock` | Cycle counter, frequency, period timing |
| `pipeline.py` | `Pipeline` / `PipelineStage` | 5-stage IF→ID→EX→MEM→WB, bubbles, flushes, ASCII viz |
| `hazards.py` | `HazardUnit` | RAW hazard detection, forwarding paths, stall insertion |
| `cache.py` | `Cache` / `CacheLine` | Direct-mapped L1, hit/miss tracking, write-back |
| `branch_predictor.py` | `BranchPredictor` | Static (always taken/not taken) + 2-bit saturating counters |
| `bus.py` | `Bus` / `BusRequest` | Shared system bus, priority arbitration, contention |
| `dma.py` | `DMA` / `DMATransfer` | Async memory-to-memory transfers, concurrent with CPU |
| `vram_controller.py` | `VRAMController` | Bandwidth limits, scanline timing, frame sync |
| `interrupts.py` | `InterruptController` | 8-line priority controller, masking, nesting |
| `profiler.py` | `Profiler` | CPI, IPC, cache rates, branch accuracy, CSV export |

### Realistic timing mode

```python
from trinary.cpu import CPU
cpu = CPU(realistic_timing=True)
cpu.load_program(["LOAD R0 10", "LOAD R1 12", "ADD R0 R1", "HALT"])
cpu.run(verbose=False)
print(cpu.clock.cycle)      # Cycles consumed
print(cpu.profiler.report()) # CPI, stalls, etc.
print(cpu.pipeline.visualize(cycle=5))  # ASCII pipeline
```

In realistic mode the CPU provides:
- **Clock**: Every `step()` = 1 clock cycle
- **Pipeline**: Instructions flow through 5 stages; pipeline visualizer shows occupancy
- **Branch prediction**: 2-bit counters with accuracy tracking; mispredicts flush pipeline
- **DMA**: Transfers run concurrently, memory reads/writes interleaved
- **Profiler**: Tracks cycles, instructions retired, CPI, stalls, branch accuracy

### Test commands

```sh
python -m pytest tests/test_pipeline.py -v          # 19 tests (clock, pipeline, hazards, timing)
python -m pytest tests/test_cache.py -v              # 10 tests
python -m pytest tests/test_branch_predictor.py -v   # 7 tests
python -m pytest tests/test_dma.py -v                # 7 tests
python -m pytest tests/test_interrupts.py -v         # 8 tests
python -m pytest tests/test_bus.py -v                # 7 tests
python -m pytest tests/test_vram.py -v               # 7 tests
python -m pytest tests/test_profiler.py -v           # 9 tests
python -m pytest tests/test_realistic_cpu.py -v      # 9 tests (CPU integration)
```

All hardware is **optional** and **backward-compatible**. `CPU()` without `realistic_timing` behaves identically to the original instant-execution emulator.

# AGENTS.md

Ternary (base-3) computer simulation — logic gates, ALU, 27-opcode CPU, two-pass assembler, machine-code encoder, dual display subsystems, native C acceleration, Fantasy Console SDK, TAL compiler, ternary neural networks (`ai/`+`ai2/`), PyQt6 desktop UI, FastAPI+React web visualizer (`backend/`+`frontend/`), cycle-accurate hardware simulation, tensor accelerator coprocessor, multi-core SMP (`system.py`), cellular automaton (`demo_automaton`).

## Setup & commands

```sh
pip install -e .                              # one-time install; src/trinary is package root
python -m pytest tests/ -v                    # 703 tests (697 pass, 6 fail in ai2 trainer)
python -m pytest tests/ -k "keyword" -v       # keyword filter
python -m pytest tests/test_cpu.py -v         # single file
python -m pytest tests/test_ai2/ -v           # ai2 package (57 tests, 6 known failures)
python -m trinary.os                          # legacy OS shell (TTY)
python -m trinary.ui.app                      # PyQt6 UI (needs PyQt6)
python -m trinary.demo_games <name>           # SDK demos: pong/snake/breakout/particles/paint/bouncing_logo/tilemap/rpg
python -m trinary.demo_programs               # legacy assembly demos
python -m trinary.demo_graphics               # framebuffer tests
python -m trinary.demo_automaton              # cellular automaton
python -m trinary.demo_multicore              # multi-core SMP demo
python -m trinary.native_benchmark            # benchmark native C vs Python
python test_snake_tal.py                      # TAL-compiled snake CPU test (13 frames)
python train_mnist.py                         # MNIST training (ternary NN)
```

Use `-s` and `--tb=short` for debugging.

## Key docs

| File | What |
|------|------|
| `ARCHITECTURE.md` (745ℓ) | Full CPU spec, memory map, pipeline, interrupts |
| `docs/instruction-set.md` (1215ℓ) | All 31 opcodes, cycle costs, operand types |
| `docs/developer-guide.md` (705ℓ) | Setup, testing, adding instructions |
| `docs/FANTASY_CONSOLE.md` (351ℓ) | SDK reference |
| `docs/TERNARY_OS.md` (163ℓ) | Dual OS internals |
| `docs/ui-guide.md` (253ℓ) | PyQt6 desktop UI widgets |
| `docs/display-system.md` (284ℓ) | Dual display internals |

## Gotchas

- **CPU default**: `CPU()` → `Memory(512)`. For framebuffer SDK path: `CPU(memory=Memory(10000))` — keyboard at 9000, VRAM at 1000–5095.
- **CPU realistic timing**: `CPU(realistic_timing=True)` enables pipeline, cache, branch predictor, DMA, bus, interrupt controller, profiler, and structural hazard unit.
- **Unified hardware stack**: PUSH/POP/CALL/RET/INT/IRET all use the same physical memory stack (SP grows down 255→128). No separate Python call stack. CALL/RET can overflow.
- **Native signed-magnitude arithmetic**: ALU uses `arithmetic.py` which implements ADD/SUB/MUL/DIV on ternary strings directly (no decimal round-trip). `adder.py` (ripple-carry) handles non-negative magnitude core.
- **Interrupts auto-save context**: INT/timer interrupts push R0–R3, flags, PC to the hardware stack; IRET restores them. Handlers cannot communicate via registers.
- **Register-indirect addressing**: JMPR, JZR, JNZR, CALLR allow computed jumps via register (opcodes 203–206, format B). Enables function pointers and computed dispatch.
- **Audio**: `sfx()` queues tones; `audio.flush()` writes WAV file to `audio_output/`. Not real-time — file-based output.
- **VRAM read bandwidth**: VRAMController now limits both reads and writes per frame (symmetric `check_read()` / `check_write()`).
- **Structural hazards**: Memory-port conflicts (IF vs. MEM) and ALU contention modeled in `StructuralHazardUnit`. Tracked in profiler.
- **TAL peephole optimizer**: Removes redundant PUSH/POP pairs and duplicate LOAD to same register.
- **Signed-magnitude negatives**: leading `-` (e.g., `"-10"` = −3 decimal). Not balanced ternary.
- **`machine.py`** encodes 31 opcodes (27 original + 4 register-indirect: JMPR/JZR/JNZR/CALLR). No ternary encoding for INT/IRET/EI/DI/SETIVT/SETTIMER.
- **BackpropOptimizer** replaces per-neuron SGD for multi-layer `TernaryNeuralNetwork` — computes true gradients through hidden layers in {-1,0,+1} space with STE. `TernaryHillClimber` is deprecated.
- **Cache** is N-way set-associative with LRU (not direct-mapped). Default associativity=2. `Bus` supports burst mode and split transactions.
- **`__init__.py`** at `src/trinary/` re-exports types from `ai` (TritTensor, Perceptron, TernaryNeuralNetwork) and `accelerator` (PackedTritArray, TritSIMD, TensorCore, etc.).
- **Dual OS paths**: `os.py` (legacy TTY shell, single file) and `os/` package (Kernel/Shell/Terminal classes). Display refactored into `display/` package — imports are `from trinary.display import ...`.
- **`tests/legacy/`** excluded by pytest (`norecursedirs` in `pyproject.toml`); contains only `.bak` files.
- **Inline comments**: `#` and `;` both work (handled by `assembler.parse_line`).
- **Memory hooks**: `memory.register_write_hook(start, end, callback)` for VRAM auto-sync.
- **No CI/lint/typecheck** — `pytest` is the only enforcement.
- **No conftest.py**, no pytest plugins.
- **6 known test failures** in `tests/test_ai2/test_trit_trainer.py` — AttributeError in `trit_trainer.py:106` (ai2 trainer needs fixes).

## Architecture — dual display/OS

| Layer | VRAM range | Display | Keyboard | Used by |
|-------|-----------|---------|----------|---------|
| **Legacy** (text) | 200–255 | 7×8 chars via `DisplayMemoryMap` | 260 | `os.py`, `demo_programs.py`, `cpu.py` default |
| **SDK** (framebuffer) | 1000–5095 | 64×64 pixel `Framebuffer` | 9000–9001 | `os/` package, `sdk/`, `demo_games.py`, PyQt6 |

## Native C backend

`libternary.so` (pre-built at `src/trinary/libternary.so`) accelerates ALU/GPU ops via ctypes, falls back to pure Python. `NATIVE_AVAILABLE` / `GPU_NATIVE_AVAILABLE` tell callers whether acceleration loaded.

```sh
make -C src/trinary/native                    # rebuild libternary.so
bash build_native.sh                          # alternative
```

`gpu_native.py` and `native_backend.py` are separate files, both probe via ctypes.

## TAL compiler (`src/trinary/tal.py`, 337ℓ)

Compiles structured language → ternary CPU assembly. Labels: `name:` (not `label name:`). Address constants: `@addr` notation. Snake game (`snake_game.py`) uses TAL-compiled CPU assembly (524 instructions).

## Paper (`paper/`)

40 files, 6005ℓ `main.tex`, 23 PDF diagrams. Build: `cd paper && bash build.sh`. Diagrams regenerated: `python generate_diagrams.py`.

## `ai2/` package (`src/trinary/ai2/`)

Newer NN package — `TritGraph`, `TritModule`, `TritSequential`, `TritTanh`, `TritMSELoss`, `TritCrossEntropyLoss`, `TritTrainer`. 57 tests, 6 known failures (trainer AttributeError).

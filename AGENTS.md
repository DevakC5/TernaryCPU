# AGENTS.md

Ternary (base-3) computer simulation — logic gates, ALU, 27-opcode CPU, two-pass assembler, machine-code encoder, dual display subsystems, native C acceleration, Fantasy Console SDK, TAL compiler, ternary neural networks (`ai/`), PyQt6 desktop UI, FastAPI+React web visualizer (`backend/`+`frontend/`), cycle-accurate hardware simulation (pipeline, cache, branch predictor, bus, DMA, interrupts, VRAM timing), tensor accelerator coprocessor.

## Setup & commands

```sh
pip install -e .                              # one-time install; src/trinary is package root
python -m pytest tests/ -v                    # 648 tests
python -m pytest tests/test_cpu.py -v         # CPU instruction tests
python -m pytest tests/ -k "cmp" -v           # keyword filter
python -m trinary.os                          # legacy OS shell (TTY)
python -m trinary.ui.app                      # PyQt6 UI (needs PyQt6)
python -m trinary.demo_games <name>           # SDK demos: pong/snake/breakout/particles/paint/bouncing_logo/tilemap/rpg
python -m trinary.demo_programs               # legacy assembly demos
python -m trinary.demo_graphics               # framebuffer pixel/color/noise tests
python -m trinary.native_benchmark            # benchmark native C vs Python
python test_snake_tal.py                      # TAL-compiled snake CPU test (13 frames)
```

Key reference: [`ARCHITECTURE.md`](ARCHITECTURE.md) (732 lines) — full CPU spec, memory map, pipeline, interrupt mechanics. Read this first for deep understanding.

## Documentation

| File | Lines | Content |
|------|-------|---------|
| `docs/instruction-set.md` | 1139 | All 27 opcode formats, cycle costs, operand types |
| `docs/display-system.md` | 284 | Dual display internals (text + framebuffer) |
| `docs/developer-guide.md` | 705 | Setup, testing, adding instructions |
| `docs/FANTASY_CONSOLE.md` | 351 | SDK reference |
| `docs/TERNARY_OS.md` | 163 | Dual OS internals |
| `docs/ui-guide.md` | 253 | PyQt6 desktop UI widgets |
| `docs/tutorial.md` | 826 | 17-step walkthrough |
| `docs/TODO.md` | 196 | Feature completeness status |
| `docs/GRAPHICS_SYSTEM.md` | 175 | SDK graphics pipeline |
| `docs/benchmarks.md` | 139 | Performance benchmarks |
| `docs/book.md` | 451 | Extended book-format documentation |
| `docs/devlog.md` | 541 | Development log |

## Academic paper

`paper/` (42 files) — full 34-chapter LaTeX monograph (5975 lines `main.tex`) with 30 matplotlib-generated PDF diagrams. Build: `cd paper && bash build.sh`. Diagrams regenerated via `python generate_diagrams.py`.

## Native backend

C native layer (`libternary.so`) accelerates ALU ops and GPU kernels. Not required — `native_backend.py` / `gpu_native.py` auto-probe paths via ctypes and fall back to pure Python. `NATIVE_AVAILABLE` / `GPU_NATIVE_AVAILABLE` tell callers whether acceleration loaded. Pre-built `.so` already lives in `src/trinary/`.

```sh
make -C src/trinary/native                    # produces src/trinary/libternary.so
bash build_native.sh                          # alternative
```

GPU native speedups (C vs Python): matmul ~27x, reduce ~6.5x, fused linear ~4.4x, scan ~2.6x. `gpu.py` uses `USE_GPU_NATIVE` flag to auto-select C paths.

## Architecture — dual display/OS subsystems

| Layer | VRAM range | Display | Keyboard | Used by |
|-------|-----------|---------|----------|---------|
| **Legacy** (text) | 200–255 | 7×8 chars via `DisplayMemoryMap` | 260 | `os.py`, `demo_programs.py`, `cpu.py` default |
| **SDK** (framebuffer) | 1000–5095 | 64×64 pixel `Framebuffer` | 9000–9001 | `os/` package, `sdk/`, `demo_games.py`, PyQt6 |

Two OS paths coexist: `os.py` (legacy TTY shell, single file) and `os/` package with `Kernel`/`Shell`/`Terminal` classes. Display was refactored into `display/` package — imports are `from trinary.display import ...`.

## Web visualizer (undocumented elsewhere)

- `backend/` — FastAPI WebSocket server (port 8000), wraps CPU via `SnapshotEngine`. Start: `cd backend && uvicorn main:app` (needs `pip install fastapi uvicorn websockets pydantic`).
- `frontend/` — React+Vite+TypeScript web UI. Start: `cd frontend && npm install && npm run dev`.

## Ternary neural networks (`src/trinary/ai/`)

Package for ternary-based neural networks: `TritTensor`, `Perceptron`, `TernaryNeuralNetwork`, `TernaryTrainer`, `SGDOptimizer`, `TernaryHillClimber`, loss functions, datasets, visualizers.

```sh
python -m pytest tests/test_ternary_nn.py tests/test_activations.py tests/test_losses.py \
  tests/test_optimizers.py tests/test_perceptron.py tests/test_trainer.py \
  tests/test_datasets.py tests/test_trit_tensor.py -v    # 128 NN tests (included in 648 total)
```

## Key gotchas

- **CPU default**: `CPU()` creates `Memory(512)`. For framebuffer SDK path, pass `CPU(memory=Memory(10000))` — keyboard at 9000, VRAM at 1000–5095.
- **CPU realistic timing**: `CPU(realistic_timing=True)` enables cycle-accurate pipeline, cache, branch prediction, DMA, bus, interrupt controller, and profiler. All programs and tests work identically in fast mode (default).
- **Dual stacks**: `sp` register (PUSH/POP, memory-based, grows down 255→128) vs `call_stack` list (CALL/RET, Python list).
- **Two addition paths**: `adder.py` (native base-3 ripple-carry, 0–2 only, no negatives) vs `arithmetic.py` (decimal round-trip, handles negatives). ALU uses `arithmetic.add_ternary`.
- **Signed-magnitude negatives**: leading `-` (e.g., `"-10"` = −3 decimal). Not balanced ternary.
- **`machine.py`** encodes 27 opcodes — tensor ops `TVECADD(210)`/`TMATMUL(211)`/`TDOT(212)`/`TACT(220)`/`TLOADW(221)`/`TSTOREW(222)` added. No ternary encoding for INT/IRET/EI/DI/SETIVT/SETTIMER.
- **`__init__.py`** at `src/trinary/` re-exports key types from `ai` (TritTensor, Perceptron, TernaryNeuralNetwork) and `accelerator` (PackedTritArray, TritSIMD, TensorCore, etc.).
- **`tests/legacy/`** excluded by pytest (`norecursedirs` in `pyproject.toml`); contains only `.bak` files.
- **CPU tests** use `cpu.run(verbose=False)` to suppress output.
- **Inline comments**: `#` and `;` both work (handled by `assembler.parse_line`).
- **Memory hooks**: `memory.register_write_hook(start, end, callback)` for VRAM auto-sync.
- **No CI/lint/typecheck** — `pytest` is the only enforcement. Use `-s` and `--tb=short` for debugging.
- **No conftest.py**, no pytest plugins.

## MNIST training (`train_mnist.py`)

Trains a ternary neural network on MNIST using Straight-Through Estimator (STE). Maintains real-valued weights during training, ternarized only for forward pass.

```sh
python train_mnist.py                                              # 500 train, 100 test, linear 784→10
python train_mnist.py --epochs 200 --hidden 64                     # deeper network
python train_mnist.py --train-size 5000                            # more data
python train_mnist.py --lr 0.005 --seed 42                         # tuning
```

Current best: 784→10 linear model, 1000 train/50 epochs → 65% validation / 60.8% full test. Models saved to `models/`:
- `mnist_model_best.json` — STE format (real-valued + ternary weights)
- `mnist_model_tnn.json` — `TernaryNeuralNetwork`-compatible (ternary-only weights)

Accuracy metric: argmax over output vector (like standard MNIST).

## TAL compiler (`src/trinary/tal.py`)

Compiles higher-level structured language into ternary CPU assembly. Labels use `name:` (not `label name:`). Address constants in `@addr` notation resolved during compilation. Snake game (`snake_game.py`) uses TAL-compiled CPU assembly (524 instructions). Body circular buffer at mem 20–147.

## SDK/Fantasy Console (`src/trinary/sdk/`)

`Engine` + `Runtime` host games. Public API: `cls`, `spr`, `btn`, `btnp`, `print_text`, `pixel`, `rect`, `sfx`, `poll_input`. Cartridge format (`Cartridge` class) packs sprites, tilemaps, code. Demos in `demo_games.py`.

## Tensor Accelerator (`src/trinary/accelerator/`)

6 tensor ISA opcodes (TLOADW, TSTOREW, TVECADD, TMATMUL, TDOT, TACT) integrated with CPU, assembler, and machine encoder. GPU mode with `ProcessingElement` → `Workgroup` → `TernaryGPU`. SIMD processor, packed trit storage. ASCII viz in `viz.py`.

## Hardware simulation (`src/trinary/hardware/`)

All components optional — enabled via `CPU(realistic_timing=True)`: `Clock`, `Pipeline` (5-stage IF→ID→EX→MEM→WB), `HazardUnit`, `Cache` (direct-mapped L1), `BranchPredictor` (2-bit saturating), `Bus`, `DMA`, `VRAMController`, `InterruptController` (8-line), `Profiler` (CPI/IPC/cache/branch CSV export).

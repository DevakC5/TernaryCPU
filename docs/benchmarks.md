# Benchmarks

Performance measurements of the Trinary ternary computer system (v2.0.0).

---

## 1. Instruction Throughput

### Cycle Costs

| Opcode | Cycles | Category |
|--------|--------|----------|
| LOAD, MOV, CLR, ADD, SUB, AND, OR, NOT, CMP | 1 | Register ops |
| JMP, JZ, JNZ | 1 | Control flow |
| EI, DI, SETIVT, SETTIMER | 1 | System |
| HALT | 1 | System |
| PUSH, POP | 2 | Stack ops (memory) |
| STOREM, LOADM | 2 | Memory ops |
| INT, IRET | 2 | Interrupts |
| MUL | 3 | Arithmetic |
| CALL, RET | 3 | Subroutines |
| TACT | 3 | Tensor activation |
| TVECADD | 4 | Tensor vector add |
| TDOT | 6 | Tensor dot product |
| TLOADW, TSTOREW | 10 | Tensor load/store |
| TMATMUL | 20 | Tensor matrix multiply |
| DIV | 5 | Arithmetic |

### Execution Rate

| Metric | Pure Python | With Native C |
|--------|-------------|---------------|
| Simple instruction | ~1M ops/sec | ~5M ops/sec |
| Complex (DIV) | ~200K ops/sec | ~800K ops/sec |
| Full demo program | ~50K cycles/sec | ~250K cycles/sec |
| 594-test suite | ~0.4s total | — |

---

## 2. Digit Density: Ternary vs Binary

| Value | Binary Digits | Ternary Digits | Savings |
|-------|--------------|----------------|---------|
| 0 | 1 | 1 | 0% |
| 10 | 4 | 3 | 25% |
| 100 | 7 | 5 | 29% |
| 1,000 | 10 | 7 | 30% |
| 10,000 | 14 | 9 | 36% |
| 100,000 | 17 | 11 | 35% |
| 1,000,000 | 20 | 13 | 35% |
| 100,000,000 | 27 | 17 | 37% |

Ternary uses **~37% fewer digits** than binary on average.

---

## 3. Hardware Simulation Overhead

When `realistic_timing=True` is enabled:

| Component | Overhead |
|-----------|----------|
| Pipeline (5-stage) | ~2× cycle count |
| Cache (direct-mapped L1) | ~1–5% miss rate |
| Branch predictor (2-bit) | ~85–95% accuracy |
| DMA (concurrent transfer) | ~10–30% bus contention |
| Full realistic mode | ~3–5× slower Python execution |

---

## 4. Native C Backend Speedup

| Operation | Python (μs) | C Native (μs) | Speedup |
|-----------|-------------|---------------|---------|
| Ternary add (10 trits) | 2.1 | 0.4 | 5.3× |
| Ternary mul (10 trits) | 5.8 | 1.1 | 5.3× |
| Ternary to decimal | 1.5 | 0.3 | 5.0× |
| Decimal to ternary | 1.8 | 0.4 | 4.5× |

Run the benchmark: `python -m trinary.native_benchmark`

---

## 5. Memory Usage

| Component | Size |
|-----------|------|
| Register file | 4 ternary strings |
| Memory (default) | 512 cells |
| Memory (SDK mode) | 10,000 cells |
| Stack (SP) | ~128 cells (128–255) |
| VRAM (text) | 56 cells (200–255) |
| VRAM (framebuffer) | 4,096 cells (1000–5095) |
| Program (100 instr) | ~100 instruction strings |

---

## 6. SDK / Fantasy Console Performance

| Metric | Value |
|--------|-------|
| Target FPS | 30 |
| Framebuffer size | 64×64 = 4,096 pixels |
| Sprite blit (8×8) | ~5μs |
| Tilemap render (32×32) | ~200μs |
| Particle update (50 particles) | ~100μs |
| Full game loop (Pong) | ~1ms |

---

## 7. OS Shell Metrics

| Metric | Legacy OS | SDK OS |
|--------|-----------|--------|
| Program size | 342 instructions | Python classes |
| Boot cycles | ~1000 steps | Instant |
| Key response | ~100 cycles | ~1ms |
| Display | 7×8 chars | 64×64 pixels |
| Commands | 5 | 10+ |

---

## 8. Test Suite Growth

| Version | Tests | Run Time |
|---------|-------|----------|
| v1.0.0 | 113 | ~0.06s |
| v2.0.0 | 594 | ~0.4s |

---

## 9. Running Benchmarks

```sh
python -m trinary.benchmark                    # Legacy benchmarks
python -m trinary.native_benchmark             # Python vs C comparison
python -m pytest tests/ -v                     # All 594 tests
python -m pytest tests/test_realistic_cpu.py -v  # Hardware sim tests
```

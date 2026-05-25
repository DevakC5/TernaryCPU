# Developer Guide

---

## 1. Development Setup

### Prerequisites

- Python 3.10+
- pip

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

Total: **113 tests**

---

## 3. Code Organization

### Module Dependency Graph

```
conversion.py         (foundation)
    ↑
logic.py              (foundation)
    ↑
adder.py              → logic.py
arithmetic.py         → conversion.py
    ↑
alu.py                → arithmetic.py, logic.py, conversion.py
registers.py          → conversion.py
memory.py             (standalone)
    ↑
cpu.py                → registers.py, alu.py, memory.py
assembler.py          → (standalone, cpu.py demo only)
machine.py            → assembler.py, conversion.py
display.py            → conversion.py (lazy)
os.py                 → cpu.py, assembler.py, conversion.py, display.py
demo_programs.py      → cpu.py, assembler.py, display.py
benchmark.py          → cpu.py, assembler.py, adder.py, conversion.py
diagrams.py           (standalone)
```

Core execution path (instruction → result):
```
assembly string
  → CPU.execute_instruction()
    → registers.load/store() for register ops
    → alu.alu() for ALU operations
      → arithmetic.add_ternary() etc. (decimal round-trip)
    → memory.store/load() for STOREM/LOADM/PUSH/POP
```

---

## 4. Adding a New Instruction

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

## 5. Adding a New ALU Operation

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

## 6. Testing Patterns

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

---

## 7. Common Pitfalls

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

---

## 8. Debugging Techniques

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

---

## 9. Performance Considerations

- The CPU is a pure Python simulation — not designed for speed
- `DIV` is the most expensive instruction (5 cycles)
- Decimal round-trip in arithmetic requires string conversion each operation
- The ripple-carry adder in `adder.py` is educational, not used by the CPU
- Memory is a Python dict, so access is O(1)
- 113 tests complete in ~0.06s — fast enough for development

---

## 10. Contributing Guidelines

1. **Tests first**: Add a failing test before implementing a feature
2. **Follow conventions**: Study existing code for patterns (error handling, naming, documentation)
3. **Keep modules focused**: `conversion.py` does conversions, `alu.py` does ALU, etc.
4. **Document with examples**: Every instruction should have an assembly example
5. **Update docs**: When adding instructions or changing behavior, update ARCHITECTURE.md, instruction-set.md, and AGENTS.md

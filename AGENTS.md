# AGENTS.md

## Project

Trinary — a ternary (base-3) computer simulation in pure Python. Research/educational.

## Structure

```
src/core/
  conversion.py    Trit class + binary/ternary/decimal converters (also the CLI entrypoint)
  arithmetic.py    add/subtract/multiply/divide on ternary strings (via decimal round-trip)
  logic.py         TNOT, TAND, TOR gates + truth table printer
tests/             standalone scripts with input()—not automated, no test framework
docs/              devlog and TODO
```

No `__init__.py`, no package config, no linting/formatting/CI.

## Running

Always from project root. No install step.

```sh
python src/core/conversion.py          # interactive CLI conversion demo
python -m src.core.logic               # prints truth tables
python tests/test_TrinaryAddition.py   # prompts for input
```

## Key facts

- **No pytest / no automated tests** — test scripts use `input()` and must be run manually.
- **Arithmetic** converts ternary→decimal, operates, then decimal→ternary. Not a native base-3 ALU.
- **Trit class** is in `conversion.py`, not its own module.
- **No negative numbers** — `subtract_ternary` raises if result < 0; all converters expect non-negative ints.
- **No package manager** — no `pyproject.toml`, `requirements.txt`, or lockfile. Only stdlib.
- **No `__init__.py`** — `from core.conversion import ...` works because the runner is at project root.

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

DEMOS = {
    "Simple Add": """\
# Add two numbers, store result
start:
    LOAD R0 12
    LOAD R1 21
    ADD R0 R1
    MOV R2 R0
    HALT
""",
    "Countdown": """\
# Countdown from decimal 5 (12 in ternary)
start:
    LOAD R0 12
    LOAD R1 0
    LOAD R2 1
loop:
    CMP R0 R1
    JZ done
    SUB R0 R2
    JMP loop
done:
    HALT
""",
    "Fibonacci": """\
# Compute F(3)=2 (unrolled 2 iterations)
    LOAD R0 0
    LOAD R1 1
    LOAD R2 0
    ADD R2 R0
    ADD R2 R1
    MOV R0 R1
    MOV R1 R2
    LOAD R2 0
    ADD R2 R0
    ADD R2 R1
    MOV R0 R1
    MOV R1 R2
    HALT
""",
    "Factorial": """\
# 3! = 6 (20 in ternary)
    LOAD R0 1
    ADD R0 R0
    MOV R1 R0
    ADD R0 R1
    ADD R0 R1
    HALT
""",
    "Calculator": """\
# ((10 + 5) - 3) + 2 = 14
start:
    LOAD R0 101
    LOAD R1 12
    ADD R0 R1
    LOAD R2 10
    SUB R0 R2
    LOAD R3 2
    ADD R0 R3
    HALT
""",
    "Subroutine": """\
# CALL/RET subroutine demo
main:
    LOAD R0 10
    LOAD R1 20
    CALL add_routines
    HALT
add_routines:
    ADD R0 R1
    RET
""",
    "Stack Ops": """\
# PUSH/POP demo
start:
    LOAD R0 10
    LOAD R1 20
    LOAD R2 100
    PUSH R0
    PUSH R1
    PUSH R2
    POP R3
    POP R2
    POP R1
    HALT
""",
    "Logical Ops": """\
# AND, OR, NOT demo
start:
    LOAD R0 102
    LOAD R1 21
    AND R0 R1
    LOAD R0 102
    OR R0 R1
    LOAD R0 102
    NOT R0
    HALT
""",
    "Comparison": """\
# CMP + conditional jump
start:
    LOAD R0 101
    LOAD R1 202
    CMP R0 R1
    JZ equal
    JNZ not_equal
equal:
    HALT
not_equal:
    HALT
""",
    "Sum 1..N": """\
# Sum numbers 1 to N (N=5)
start:
    LOAD R0 12
    LOAD R1 0
    LOAD R2 0
    LOAD R3 1
loop:
    ADD R2 R3
    CMP R2 R0
    JZ done
    ADD R1 R2
    JMP loop
done:
    HALT
""",
    "CPU Stress": """\
# CPU stress test: 5-level nested calls + push/pop + long countdown
start:
    LOAD R0 2
    CALL level1
countdown:
    LOAD R0 100
    LOAD R1 0
    LOAD R2 1
    CLR R3
loop:
    CMP R0 R1
    JZ done
    SUB R0 R2
    JMP loop
done:
    HALT
level1:
    ADD R0 R0
    CALL level2
    RET
level2:
    ADD R0 R0
    CALL level3
    RET
level3:
    ADD R0 R0
    CALL level4
    RET
level4:
    ADD R0 R0
    CALL level5
    RET
level5:
    ADD R0 R0
    PUSH R0
    POP R1
    RET
""",
    "Keyboard Echo": """\
# Poll memory[260] and echo typed characters to VRAM
# Click the Display area to give it focus, then press keys.
# Step or Run to advance the CPU.
start:
    LOAD R0 21102     # ternary 21102 = decimal 200 (VRAM start)
    LOAD R2 1         # increment constant
loop:
    LOADM 260 R1      # poll keyboard buffer
    LOAD R3 0
    CMP R1 R3         # non-zero?
    JZ loop           # no -> keep polling
    STOREM R0 R1      # echo char to VRAM at R0
    CLR R1
    STOREM 260 R1     # clear keyboard buffer
    ADD R0 R2         # advance pointer
    LOAD R3 100110    # ternary 100110 = decimal 255 (VRAM end)
    CMP R0 R3
    JNZ loop
    JMP start         # wrap to beginning
""",
    "HELLO TERNARY": """\
# Writes 'HELLO TERNARY' to the memory-mapped display
start:
    LOAD R0 2200   # H
    STOREM 200 R0
    LOAD R0 2120   # E
    STOREM 201 R0
    LOAD R0 2211   # L
    STOREM 202 R0
    LOAD R0 2211   # L
    STOREM 203 R0
    LOAD R0 2221   # O
    STOREM 204 R0
    LOAD R0 1012   # (space)
    STOREM 205 R0
    LOAD R0 10010  # T
    STOREM 206 R0
    LOAD R0 2120   # E
    STOREM 207 R0
    LOAD R0 10001  # R
    STOREM 208 R0
    LOAD R0 2220   # N
    STOREM 209 R0
    LOAD R0 2102   # A
    STOREM 210 R0
    LOAD R0 10001  # R
    STOREM 211 R0
    LOAD R0 10022  # Y
    STOREM 212 R0
    HALT
""",
    "Pipeline Demo": """\
# Pipeline visualization demo with branches
# Shows RAW hazards and branch prediction
start:
    LOAD R0 10
    LOAD R1 20
    ADD R0 R1       # RAW hazard: R0,R1 from LOAD
    MOV R2 R0
    SUB R2 R1       # RAW hazard: R2 from MOV, R1 from LOAD
    JZ done
    LOAD R0 100
    LOAD R1 200
    ADD R0 R1
done:
    HALT
""",
    "Branch Prediction": """\
# Branch prediction demo — multiple conditional jumps
start:
    LOAD R0 2
    LOAD R1 0
    LOAD R2 1
    CLR R3
loop:
    ADD R3 R2       # count up
    CMP R3 R0       # compare with limit
    JZ exit         # predictable: taken once, not taken many times
    JMP loop        # always taken
exit:
    HALT
""",
    "Pipeline Hazards": """\
# RAW hazard chain — each instruction depends on the previous
start:
    LOAD R0 1
    ADD R0 R0       # RAW: R0
    ADD R0 R0       # RAW: R0
    ADD R0 R0       # RAW: R0
    MOV R1 R0       # RAW: R0
    ADD R1 R1       # RAW: R1
    ADD R1 R1       # RAW: R1
    HALT
""",
    "Hello Display": """\
# Memory-mapped display demo
# Writes text into video RAM at addresses 200-215
start:
    LOAD R0 2200   # H
    STOREM 200 R0
    LOAD R0 2120   # E
    STOREM 201 R0
    LOAD R0 2211   # L
    STOREM 202 R0
    LOAD R0 2211   # L
    STOREM 203 R0
    LOAD R0 2221   # O
    STOREM 204 R0
    LOAD R0 1012   # (space)
    STOREM 205 R0
    LOAD R0 10010  # T
    STOREM 206 R0
    LOAD R0 2120   # E
    STOREM 207 R0
    LOAD R0 10001  # R
    STOREM 208 R0
    LOAD R0 2220   # N
    STOREM 209 R0
    LOAD R0 2102   # A
    STOREM 210 R0
    LOAD R0 10001  # R
    STOREM 211 R0
    LOAD R0 10022  # Y
    STOREM 212 R0
    LOAD R0 1012   # (space)
    STOREM 213 R0
    LOAD R0 10012  # V
    STOREM 214 R0
    LOAD R0 2212   # M
    STOREM 215 R0
    HALT
""",
}

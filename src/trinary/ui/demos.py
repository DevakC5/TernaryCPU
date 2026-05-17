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
}

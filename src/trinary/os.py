"""Minimal Operating System shell for the Ternary CPU.

Boots into a command shell. Uses memory-mapped display (200-255)
for output and keyboard buffer (260) for input.

DEPRECATED: Use ``trinary.os`` package (``os/`` directory) for the
new modular OS implementation with SDK display support.

Memory:
   0       cursor offset (ternary)
   1-32    input buffer characters
   33      input length
   34+     OS working data
   200-255 VRAM
   260     keyboard buffer
"""

import warnings
warnings.warn(
    "legacy os.py is deprecated; use the trinary.os package (os/ directory) instead.",
    DeprecationWarning, stacklevel=2
)

from trinary.cpu import CPU
from trinary.assembler import Assembler
from trinary.conversion import decimal_to_ternary as d2t
from trinary.display import DisplayMemoryMap, DISPLAY_START, DISPLAY_END


def _t(ch):
    return d2t(ord(ch))


def _gen():
    SPC = _t(" ")
    H = _t("H"); E = _t("E"); L = _t("L"); P = _t("P")
    M = _t("M"); D = _t("D"); U = _t("U"); N = _t("N")
    R = _t("R"); S = _t("S"); C = _t("C"); G = _t("G")
    GT = _t(">")
    VRB = d2t(DISPLAY_START)
    VRE = d2t(DISPLAY_END + 1)  # 256, one past end
    LAR = d2t(DISPLAY_END - 7)  # 248
    BL32 = d2t(32)
    FMT = f"""
# Ternary Shell v1

# === Boot ===
start:
    LOAD R3 0
    CALL cls
    CALL banner
    CALL prompt

main:
    LOADM 260 R1
    CMP R1 R3
    JZ main
    STOREM 260 R3
    CALL kbd
    JMP main

# kbd: handle one keypress in R1
kbd:
    LOAD R0 {_t(chr(127))}
    CMP R0 R1
    JZ kbsp
    LOAD R0 {_t(chr(10))}
    CMP R0 R1
    JZ kent
    LOAD R0 {_t(chr(13))}
    CMP R0 R1
    JZ kent
    CALL bufadd
    LOAD R0 {BL32}
    CMP R1 R0
    JZ main
    CALL vput
    RET

kbsp:
    CALL bufpop
    RET

kent:
    CALL vput
    CALL exec
    CALL prompt
    CALL bufclr
    RET

# vput: write R1 to VRAM[cursor], advance
vput:
    LOADM 0 R0
    LOAD R2 {d2t(55)}
    CMP R0 R2
    JZ vfull
    LOAD R2 {VRB}
    ADD R0 R2
    STOREM R0 R1
    CALL vinc
    RET
vfull:
    CALL doscroll
    LOADM 0 R0
    LOAD R2 {VRB}
    ADD R0 R2
    STOREM R0 R1
    LOAD R0 {d2t(49)}
    STOREM 0 R0
    RET

# vinc: cursor += 1
vinc:
    LOADM 0 R0
    LOAD R2 1
    ADD R0 R2
    STOREM 0 R0
    RET

# doscroll: copy 201→200 … 247→246, clear 248-255
doscroll:
    LOAD R2 {d2t(DISPLAY_START + 1)}
sc_lp:
    LOADM R2 R0
    LOAD R1 1
    SUB R2 R1
    STOREM R2 R0
    LOAD R1 2
    ADD R2 R1
    LOAD R0 {LAR}
    CMP R2 R0
    JZ sclr
    JMP sc_lp
sclr:
    LOAD R2 {LAR}
sclp:
    STOREM R2 R3
    LOAD R0 1
    ADD R2 R0
    LOAD R0 {VRE}
    CMP R2 R0
    JZ sdon
    JMP sclp
sdon:
    LOAD R0 {d2t(48)}
    STOREM 0 R0
    RET

# bufadd: append R1 to input buffer at addresses 1-32
bufadd:
    LOADM 33 R0
    LOAD R2 {BL32}
    CMP R0 R2
    JZ bful
    LOAD R2 1
    ADD R0 R2
    STOREM 33 R0
    STOREM R0 R1
bful:
    RET

# bufpop: remove last char
bufpop:
    LOADM 33 R0
    CMP R0 R3
    JZ bpd
    LOAD R2 1
    SUB R0 R2
    STOREM 33 R0
    STOREM R0 R3
    CALL vdec
bpd:
    RET

# vdec: cursor -= 1
vdec:
    LOADM 0 R0
    CMP R0 R3
    JZ vdd
    LOAD R2 1
    SUB R0 R2
    STOREM 0 R0
vdd:
    RET

# bufclr: reset length to 0
bufclr:
    STOREM 33 R3
    RET

# prompt: "> "
prompt:
    LOAD R1 {GT}
    CALL vput
    LOAD R1 {SPC}
    CALL vput
    RET

# banner: "Trishell!"
banner:
    LOAD R1 {_t("T")}
    CALL vput
    LOAD R1 {_t("r")}
    CALL vput
    LOAD R1 {_t("i")}
    CALL vput
    LOAD R1 {_t("s")}
    CALL vput
    LOAD R1 {_t("h")}
    CALL vput
    LOAD R1 {_t("e")}
    CALL vput
    LOAD R1 {_t("l")}
    CALL vput
    LOAD R1 {_t("l")}
    CALL vput
    LOAD R1 {_t("!")}
    CALL vput
    RET

# exec: parse command
exec:
    LOADM 1 R1
    LOAD R0 {H}
    CMP R0 R1
    JZ xhelp
    LOAD R0 {M}
    CMP R0 R1
    JZ xmem
    LOAD R0 {R}
    CMP R0 R1
    JZ xregs
    LOAD R0 {C}
    CMP R0 R1
    JZ xcls
    LOAD R1 {_t("?")}
    CALL vput
    RET

xhelp:
    LOADM 2 R1
    LOAD R0 {E}
    CMP R0 R1
    JNZ unk
    LOADM 3 R1
    LOAD R0 {L}
    CMP R0 R1
    JNZ unk
    LOADM 4 R1
    LOAD R0 {P}
    CMP R0 R1
    JNZ unk
    CALL help
    RET

xmem:
    LOADM 2 R1
    LOAD R0 {E}
    CMP R0 R1
    JNZ unk
    LOADM 3 R1
    LOAD R0 {M}
    CMP R0 R1
    JNZ unk
    LOADM 4 R1
    LOAD R0 {D}
    CMP R0 R1
    JNZ unk
    LOADM 5 R1
    LOAD R0 {U}
    CMP R0 R1
    JNZ unk
    LOADM 6 R1
    LOAD R0 {M}
    CMP R0 R1
    JNZ unk
    LOADM 7 R1
    LOAD R0 {P}
    CMP R0 R1
    JNZ unk
    CALL mem
    RET

xregs:
    LOADM 2 R1
    LOAD R0 {E}
    CMP R0 R1
    JNZ xrunn
    LOADM 3 R1
    LOAD R0 {G}
    CMP R0 R1
    JNZ unk
    LOADM 4 R1
    LOAD R0 {S}
    CMP R0 R1
    JNZ unk
    CALL regs
    RET

xrunn:
    LOAD R0 {U}
    CMP R0 R1
    JNZ unk
    LOADM 3 R1
    LOAD R0 {N}
    CMP R0 R1
    JNZ unk
    CALL run_
    RET

xcls:
    LOADM 2 R1
    LOAD R0 {L}
    CMP R0 R1
    JNZ unk
    LOADM 3 R1
    LOAD R0 {S}
    CMP R0 R1
    JNZ unk
    CALL cls
    RET

unk:
    LOAD R1 {_t("?")}
    CALL vput
    RET

# help: print available commands
help:
    LOAD R1 {H}
    CALL vput
    LOAD R1 {E}
    CALL vput
    LOAD R1 {L}
    CALL vput
    LOAD R1 {P}
    CALL vput
    LOAD R1 {SPC}
    CALL vput
    LOAD R1 {_t("-")}
    CALL vput
    LOAD R1 {SPC}
    CALL vput
    LOAD R1 {C}
    CALL vput
    LOAD R1 {L}
    CALL vput
    LOAD R1 {S}
    CALL vput
    LOAD R1 {SPC}
    CALL vput
    LOAD R1 {M}
    CALL vput
    LOAD R1 {_t("E")}
    CALL vput
    LOAD R1 {M}
    CALL vput
    LOAD R1 {D}
    CALL vput
    LOAD R1 {U}
    CALL vput
    LOAD R1 {_t("M")}
    CALL vput
    LOAD R1 {P}
    CALL vput
    LOAD R1 {SPC}
    CALL vput
    LOAD R1 {R}
    CALL vput
    LOAD R1 {_t("E")}
    CALL vput
    LOAD R1 {_t("G")}
    CALL vput
    LOAD R1 {S}
    CALL vput
    LOAD R1 {SPC}
    CALL vput
    LOAD R1 {R}
    CALL vput
    LOAD R1 {U}
    CALL vput
    LOAD R1 {N}
    CALL vput
    RET

# mem: dump addresses 0-7
mem:
    LOAD R2 0
mlp:
    LOADM R2 R1
    CALL vput
    LOAD R0 1
    ADD R2 R0
    LOAD R0 {d2t(8)}
    CMP R2 R0
    JZ mdn
    LOAD R1 {SPC}
    CALL vput
    JMP mlp
mdn:
    RET

# regs: display register values by storing to temp memory and reading back
regs:
    LOAD R1 {R}
    CALL vput
    LOAD R1 {_t("0")}
    CALL vput
    LOAD R1 {_t(":")}
    CALL vput
    STOREM 34 R0
    LOADM 34 R1
    CALL vput
    LOAD R1 {SPC}
    CALL vput
    LOAD R1 {R}
    CALL vput
    LOAD R1 {_t("1")}
    CALL vput
    LOAD R1 {_t(":")}
    CALL vput
    STOREM 34 R1
    LOADM 34 R1
    CALL vput
    LOAD R1 {SPC}
    CALL vput
    LOAD R1 {R}
    CALL vput
    LOAD R1 {_t("2")}
    CALL vput
    LOAD R1 {_t(":")}
    CALL vput
    STOREM 34 R2
    LOADM 34 R1
    CALL vput
    LOAD R1 {SPC}
    CALL vput
    LOAD R1 {R}
    CALL vput
    LOAD R1 {_t("3")}
    CALL vput
    LOAD R1 {_t(":")}
    CALL vput
    STOREM 34 R3
    LOADM 34 R1
    CALL vput
    RET

# run_: display "RUN!"
run_:
    LOAD R1 {R}
    CALL vput
    LOAD R1 {U}
    CALL vput
    LOAD R1 {N}
    CALL vput
    LOAD R1 {_t("!")}
    CALL vput
    RET

# cls: clear VRAM 200-255, reset cursor
cls:
    LOAD R2 {VRB}
clp:
    STOREM R2 R3
    LOAD R0 1
    ADD R2 R0
    LOAD R0 {VRE}
    CMP R2 R0
    JZ cdn
    JMP clp
cdn:
    STOREM 0 R3
    RET
"""
    return FMT


class OS:
    def __init__(self):
        self.cpu = CPU()
        self.display = DisplayMemoryMap()
        self.asm = Assembler()

    def assemble_os(self):
        return self.asm.assemble(_gen())[0]

    def boot(self):
        prog = self.assemble_os()
        self.cpu.load_program(prog)
        self.cpu.memory.store(0, "0")
        self.cpu.memory.store(33, "0")

    def step_os(self):
        if self.cpu.halted:
            return 0
        return self.cpu.step()

    def read_display(self):
        return self.display.read_display(self.cpu.memory)

    def display_text(self):
        return "".join(self.read_display())

    def feed_key(self, char):
        self.cpu.memory.store(260, d2t(ord(char)))

    def render_console(self):
        chars = self.read_display()
        print("\033[H", end="")
        print("\u250c" + "\u2500" * 10 + "\u2510")
        for row in range(7):
            line = "".join(chars[row * 8:(row + 1) * 8])
            print(f"\u2502{line:8}\u2502")
        print("\u2514" + "\u2500" * 10 + "\u2518")


def boot_os():
    o = OS()
    o.boot()
    return o


def boot_interactive():
    import sys
    import select
    import termios
    import tty

    o = boot_os()
    old = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        print("\033[2J\033[?25l", end="", flush=True)
        while not o.cpu.halted:
            o.cpu.step()
            o.render_console()
            if select.select([sys.stdin], [], [], 0.01)[0]:
                ch = sys.stdin.read(1)
                if ch == "\x03":
                    break
                o.feed_key(ch)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
        print("\033[?25h\033[0m\n--- OS halted ---")
        print(f"Cycles: {o.cpu.cycles}")


if __name__ == "__main__":
    boot_interactive()

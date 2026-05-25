from trinary.os.terminal import Terminal
from trinary.os.shell import Shell
from trinary.os.syscalls import Syscalls
from trinary.os.boot import boot_sequence
from trinary.os.constants import COLOR_CURSOR
from trinary.display.constants import KEYBOARD_ADDR
from trinary.conversion import decimal_to_ternary as d2t, ternary_to_decimal as t2d


class Kernel:
    def __init__(self, framebuffer, cpu):
        self.fb = framebuffer
        self.cpu = cpu
        self.memory = cpu.memory

        self.terminal = Terminal(self.fb)
        self.syscalls = Syscalls(self.fb, self.terminal, self.memory)
        self.shell = Shell(self.terminal, self.syscalls, self)

        self.running = False
        self._booted = False

    def boot(self):
        boot_sequence(self.syscalls, self.terminal, self)
        self._booted = True
        self.running = True

    def tick(self):
        if not self._booted or not self.running:
            return False

        self.memory.store(KEYBOARD_ADDR, d2t(0))

        if self._check_keyboard():
            return True

        return True

    def _check_keyboard(self):
        raw = self.memory.load(KEYBOARD_ADDR)
        code = t2d(raw)
        if code == 0:
            return False

        self.memory.store(KEYBOARD_ADDR, d2t(0))
        char = chr(code) if 0 < code < 256 else ""
        if not char:
            return False

        result = self.terminal.handle_key(char)
        if result is not None:
            line = result
            self.shell.execute(line)
            self.terminal.show_prompt()

        return True

    def shutdown(self):
        self.running = False

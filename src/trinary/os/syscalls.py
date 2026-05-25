import time

from trinary.display.constants import DISPLAY_WIDTH, DISPLAY_HEIGHT
from trinary.os.constants import COLOR_BG


class Syscalls:
    def __init__(self, framebuffer, terminal, memory):
        self.fb = framebuffer
        self.terminal = terminal
        self.memory = memory

    def print_text(self, text, color=None):
        self.terminal.write(text, color=color)

    def println(self, text, color=None):
        self.terminal.writeln(text, color=color)

    def clear_screen(self):
        self.fb.clear(COLOR_BG)
        self.terminal.renderer.cursor_x = 0
        self.terminal.renderer.cursor_y = 0
        self.terminal.input_buffer = ""

    def draw_pixel(self, x, y, color):
        if 0 <= x < DISPLAY_WIDTH and 0 <= y < DISPLAY_HEIGHT and 0 <= color <= 8:
            self.fb.set_pixel(x, y, color)

    def read_key(self):
        from trinary.display.constants import KEYBOARD_ADDR
        from trinary.conversion import ternary_to_decimal
        raw = self.memory.load(KEYBOARD_ADDR)
        return ternary_to_decimal(raw)

    def sleep(self, seconds):
        time.sleep(seconds)

    def beep(self):
        pass

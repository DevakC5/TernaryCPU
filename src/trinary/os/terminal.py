import time

from trinary.os.constants import COLOR_TEXT, COLOR_PROMPT, COLOR_CURSOR
from trinary.os.text_renderer import TextRenderer


class Terminal:
    def __init__(self, framebuffer):
        self.renderer = TextRenderer(framebuffer)
        self.input_buffer = ""
        self.cursor_pos = 0
        self.history = []
        self.history_index = 0
        self._cursor_visible = True
        self._last_toggle = 0.0

    def clear(self):
        self.renderer.clear()
        self.input_buffer = ""
        self.cursor_pos = 0

    def write(self, text, color=None):
        self.renderer.write(text, color=color)

    def writeln(self, text, color=None):
        self.renderer.writeln(text, color=color)

    def print_at(self, text, x, y, color=None):
        self.renderer.print_at(text, x, y, color=color)

    def show_prompt(self):
        self.renderer.print_at("> ", 0, self.renderer.cursor_y, COLOR_PROMPT)
        self.renderer.cursor_x = 2
        for i, ch in enumerate(self.input_buffer):
            self.renderer.put_char(ch, x=2 + i, y=self.renderer.cursor_y)
        self.cursor_pos = len(self.input_buffer)

    def handle_key(self, char):
        now = time.time()
        if now - self._last_toggle > 0.5:
            self._cursor_visible = not self._cursor_visible
            self._last_toggle = now

        if char == "\x7f":
            if self.cursor_pos > 0:
                self.input_buffer = (
                    self.input_buffer[:self.cursor_pos - 1] +
                    self.input_buffer[self.cursor_pos:]
                )
                self.cursor_pos -= 1
        elif char == "\n" or char == "\r":
            return self._submit_line()
        elif char == "\x1b[A":
            if self.history:
                self.history_index = max(0, self.history_index - 1)
                self.input_buffer = self.history[self.history_index]
                self.cursor_pos = len(self.input_buffer)
        elif char == "\x1b[B":
            if self.history:
                self.history_index = min(len(self.history), self.history_index + 1)
                if self.history_index >= len(self.history):
                    self.input_buffer = ""
                else:
                    self.input_buffer = self.history[self.history_index]
                self.cursor_pos = len(self.input_buffer)
        elif 32 <= ord(char) <= 126:
            self.input_buffer = (
                self.input_buffer[:self.cursor_pos] +
                char + self.input_buffer[self.cursor_pos:]
            )
            self.cursor_pos += 1
        return None

    def _submit_line(self):
        line = self.input_buffer.strip()
        self.input_buffer = ""
        self.cursor_pos = 0
        if line:
            self.history.append(line)
            self.history_index = len(self.history)
        self.renderer.newline()
        return line

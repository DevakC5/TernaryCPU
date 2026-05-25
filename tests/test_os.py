from trinary.os import Kernel, Shell, Terminal, TextRenderer, COMMANDS
from trinary.os.constants import VERSION, NAME, COLS, ROWS, COLOR_TEXT
from trinary.os.text_renderer import FONT_8x8
from trinary.display.framebuffer import Framebuffer
from trinary.cpu import CPU
from trinary.memory import Memory


class TestTextRenderer:
    def setup_method(self):
        self.fb = Framebuffer()
        self.tr = TextRenderer(self.fb)

    def test_clear(self):
        self.tr.put_char("A", x=3, y=4)
        self.tr.clear()
        for y in range(64):
            for x in range(64):
                assert self.fb.get_pixel(x, y) == 0
        assert self.tr.cursor_x == 0
        assert self.tr.cursor_y == 0

    def test_put_char_at_position(self):
        self.tr.put_char("A", color=2, x=2, y=3)
        assert self.fb.get_pixel(16, 24) == 0
        assert self.fb.get_pixel(19, 24) == 2
        assert self.fb.get_pixel(20, 24) == 2

    def test_put_char_bounds(self):
        self.tr.put_char("X", x=-1, y=0)
        self.tr.put_char("X", x=8, y=0)
        self.tr.put_char("X", x=0, y=-1)
        self.tr.put_char("X", x=0, y=8)
        for y in range(64):
            for x in range(64):
                assert self.fb.get_pixel(x, y) == 0

    def test_print_at(self):
        self.tr.print_at("HI", 1, 2, color=2)
        assert self.fb.get_pixel(9, 16) == 2

    def test_scroll_shifts_up(self):
        self.tr.print_at("TOP", 0, 2, color=2)
        assert self.fb.get_pixel(1, 16) == 2
        self.tr.scroll()
        assert self.fb.get_pixel(1, 16) == 0
        assert self.fb.get_pixel(1, 8) == 2

    def test_newline_moves_cursor(self):
        self.tr.cursor_x = 5
        self.tr.newline()
        assert self.tr.cursor_x == 0
        assert self.tr.cursor_y == 1

    def test_newline_scrolls_at_bottom(self):
        self.tr.cursor_y = 7
        self.tr.print_at("TOP", 0, 0, color=2)
        self.tr.newline()
        assert self.tr.cursor_y == 7

    def test_write_text(self):
        self.tr.write("AB")
        assert self.tr.cursor_x == 2
        assert self.tr.cursor_y == 0

    def test_write_newline_char(self):
        self.tr.write("A\nB")
        assert self.tr.cursor_x == 1
        assert self.tr.cursor_y == 1

    def test_writeln(self):
        self.tr.writeln("AB")
        assert self.tr.cursor_x == 0
        assert self.tr.cursor_y == 1

    def test_set_color(self):
        self.tr.set_color(3)
        assert self.tr.color == 3

    def test_draw_cursor(self):
        self.tr.cursor_x = 1
        self.tr.cursor_y = 0
        self.tr.draw_cursor(visible=True)
        assert self.fb.get_pixel(15, 7) == 2

    def test_font_has_common_chars(self):
        for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?:;-+=/()[]#@\"'%><|~_*":
            assert ch in FONT_8x8, f"Missing font glyph: '{ch}'"


class TestTerminal:
    def setup_method(self):
        self.fb = Framebuffer()
        self.term = Terminal(self.fb)

    def test_initial_state(self):
        assert self.term.input_buffer == ""
        assert self.term.cursor_pos == 0

    def test_handle_key_appends(self):
        self.term.handle_key("a")
        assert self.term.input_buffer == "a"
        assert self.term.cursor_pos == 1

    def test_handle_key_backspace(self):
        self.term.handle_key("a")
        self.term.handle_key("b")
        self.term.handle_key("\x7f")
        assert self.term.input_buffer == "a"
        assert self.term.cursor_pos == 1

    def test_handle_key_enter_returns_line(self):
        self.term.handle_key("H")
        self.term.handle_key("I")
        line = self.term.handle_key("\n")
        assert line == "HI"
        assert self.term.input_buffer == ""

    def test_handle_key_printable_only(self):
        self.term.handle_key("\x01")
        assert self.term.input_buffer == ""

    def test_history(self):
        self.term.handle_key("A")
        self.term.handle_key("\n")
        assert len(self.term.history) == 1
        assert self.term.history[0] == "A"

    def test_clear(self):
        self.term.write("hello")
        self.term.clear()
        assert self.term.input_buffer == ""
        assert self.term.cursor_pos == 0

    def test_show_prompt(self):
        self.term.input_buffer = "TEST"
        self.term.show_prompt()


class TestShell:
    def setup_method(self):
        self.fb = Framebuffer()
        self.cpu = CPU(memory=Memory(10000))
        self.kernel = Kernel(self.fb, self.cpu)
        self.kernel.boot()
        self.shell = Shell(self.kernel.terminal, self.kernel.syscalls, self.kernel)

    def test_help(self):
        self.shell.execute("HELP")

    def test_cls(self):
        self.shell.execute("CLS")

    def test_mem(self):
        self.shell.execute("MEM")

    def test_regs(self):
        self.shell.execute("REGS")

    def test_about(self):
        self.shell.execute("ABOUT")

    def test_cpu(self):
        self.shell.execute("CPU")

    def test_unknown_command(self):
        self.shell.execute("XYZ123")

    def test_empty_command(self):
        self.shell.execute("")

    def test_mem_with_arg(self):
        self.shell.execute("MEM 10")

    def test_halt(self):
        self.shell.execute("HALT")
        assert not self.kernel.running


class TestKernel:
    def setup_method(self):
        self.fb = Framebuffer()
        self.cpu = CPU(memory=Memory(10000))
        self.kernel = Kernel(self.fb, self.cpu)

    def test_boot(self):
        self.kernel.boot()
        assert self.kernel._booted
        assert self.kernel.running

    def test_tick_before_boot(self):
        assert self.kernel.tick() is False

    def test_tick_after_boot(self):
        self.kernel.boot()
        result = self.kernel.tick()
        assert result is True

    def test_shutdown(self):
        self.kernel.boot()
        self.kernel.shutdown()
        assert not self.kernel.running

    def test_boot_sets_cursor(self):
        self.kernel.boot()
        t = self.kernel.terminal.renderer
        assert t.cursor_y == 7


class TestCommands:
    def test_all_commands_registered(self):
        expected = {"HELP", "CLS", "MEM", "REGS", "CLEAR",
                     "ABOUT", "DEMO", "RUN", "HALT", "CPU"}
        for cmd in expected:
            assert cmd in COMMANDS, f"Missing command: {cmd}"

    def test_no_empty_descriptions(self):
        from trinary.os.commands import DESCRIPTIONS
        for name, desc in DESCRIPTIONS.items():
            assert desc, f"Empty description for {name}"

from trinary.os.constants import (
    VERSION, NAME,
    COLOR_BANNER, COLOR_INFO, COLOR_TEXT, COLOR_CURSOR,
    COLS, ROWS, FONT_WIDTH, FONT_HEIGHT,
)
from trinary.os.text_renderer import TextRenderer


def boot_sequence(syscalls, terminal, kernel):
    syscalls.clear_screen()

    t = terminal.renderer

    t.set_color(COLOR_BANNER)
    t.print_at("TERNARY", 0, 0, COLOR_BANNER)
    t.print_at(f"OS v{VERSION}", 0, 1, COLOR_BANNER)

    t.set_color(COLOR_INFO)
    t.print_at("64x64 DISP", 0, 3, COLOR_INFO)
    t.print_at("256W RAM", 0, 4, COLOR_INFO)
    t.print_at("TCPU-4", 0, 5, COLOR_INFO)

    for x in range(8):
        t.put_char("=", color=COLOR_CURSOR, x=x, y=6)

    t.set_color(COLOR_TEXT)
    terminal.renderer.cursor_x = 0
    terminal.renderer.cursor_y = 7

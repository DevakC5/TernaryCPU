"""Memory-mapped display system for the ternary computer.

Reserved memory region 200-255 acts as video RAM.
Values stored as ternary-encoded ASCII codes.
The UI reads this region and renders characters on a terminal-like screen.
"""

DISPLAY_START = 200
DISPLAY_END = 255
DISPLAY_SIZE = DISPLAY_END - DISPLAY_START + 1


class DisplayMemoryMap:
    """Backend for memory-mapped text display.

    Reads ternary-encoded ASCII values from a reserved RAM region
    and converts them to displayable characters. Zero-values render
    as spaces. Non-printable codes render as '.'.
    """

    def read_display(self, memory):
        """Read the display buffer from memory.

        Args:
            memory: Memory object with .load(addr) method.

        Returns:
            list: Character strings, one per display cell.
        """
        from trinary.conversion import ternary_to_decimal

        chars = []
        for addr in range(DISPLAY_START, DISPLAY_END + 1):
            raw = memory.load(addr)
            code = ternary_to_decimal(raw)
            if code == 0:
                chars.append(" ")
            elif 32 <= code <= 126:
                chars.append(chr(code))
            else:
                chars.append(".")
        return chars

    def write_text(self, memory, text, offset=0):
        """Write a text string into display memory.

        Each character is converted to its ASCII code, then stored
        as a ternary string at the corresponding display address.

        Args:
            memory: Memory object with .store(addr, value) method.
            text (str): Text to display.
            offset (int): Starting position within the display buffer.
        """
        from trinary.conversion import decimal_to_ternary as d2t

        for i, ch in enumerate(text):
            addr = DISPLAY_START + offset + i
            if addr > DISPLAY_END:
                break
            code = d2t(ord(ch))
            memory.store(addr, code)

    def clear(self, memory):
        """Clear the display buffer (set all cells to space/"0")."""
        from trinary.conversion import decimal_to_ternary as d2t
        for addr in range(DISPLAY_START, DISPLAY_END + 1):
            memory.store(addr, "0")


class PixelDisplay:
    """27x27 pixel framebuffer.

    Each cell stores a trit value:
        0 = black
        1 = gray
        2 = white
    """

    WIDTH = 27
    HEIGHT = 27

    def __init__(self):
        self.buffer = [[0] * self.WIDTH for _ in range(self.HEIGHT)]

    def set_pixel(self, x, y, color):
        """Set a single pixel.

        Args:
            x (int): Column (0-26)
            y (int): Row (0-26)
            color (int): 0=black, 1=gray, 2=white
        """
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT and color in (0, 1, 2):
            self.buffer[y][x] = color

    def get_pixel(self, x, y):
        """Get the value of a single pixel.

        Returns 0 for out-of-bounds coordinates.
        """
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            return self.buffer[y][x]
        return 0

    def clear(self):
        """Set all pixels to 0 (black)."""
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                self.buffer[y][x] = 0

    def draw_line(self, x0, y0, x1, y1, color=2):
        """Bresenham's line algorithm.

        Args:
            x0, y0: Start coordinate
            x1, y1: End coordinate
            color: 0=black, 1=gray, 2=white (default 2)
        """
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        while True:
            self.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def get_buffer(self):
        """Return the raw buffer (list of lists)."""
        return self.buffer

    def __repr__(self):
        filled = sum(1 for row in self.buffer for v in row if v)
        return f"PixelDisplay({self.WIDTH}x{self.HEIGHT}, {filled} pixels set)"

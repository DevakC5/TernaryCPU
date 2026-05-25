from trinary.display.constants import DISPLAY_WIDTH, DISPLAY_HEIGHT
from trinary.display.palette import PALETTE


class Framebuffer:
    def __init__(self):
        self.width = DISPLAY_WIDTH
        self.height = DISPLAY_HEIGHT
        self._pixels = [[0] * self.width for _ in range(self.height)]
        self._dirty = False
        self._dirty_rect = None

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height and 0 <= color <= 8:
            self._pixels[y][x] = color
            self._mark_dirty(x, y)

    def get_pixel(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._pixels[y][x]
        return 0

    def clear(self, color=0):
        for y in range(self.height):
            for x in range(self.width):
                self._pixels[y][x] = color
        self._dirty = True
        self._dirty_rect = (0, 0, self.width, self.height)

    def get_buffer(self):
        return self._pixels

    def load_from_memory(self, memory):
        from trinary.conversion import ternary_to_decimal
        for addr in range(self.width * self.height):
            y = addr // self.width
            x = addr % self.width
            raw = memory.load(self.vram_base + addr)
            val = ternary_to_decimal(raw)
            if 0 <= val <= 8:
                self._pixels[y][x] = val
        self._dirty = True
        self._dirty_rect = (0, 0, self.width, self.height)

    def sync_to_memory(self, memory):
        from trinary.conversion import decimal_to_ternary as d2t
        for addr in range(self.width * self.height):
            y = addr // self.width
            x = addr % self.width
            memory.store(self.vram_base + addr, d2t(self._pixels[y][x]))

    def is_dirty(self):
        return self._dirty

    def clear_dirty(self):
        self._dirty = False
        self._dirty_rect = None

    def get_dirty_rect(self):
        return self._dirty_rect

    def _mark_dirty(self, x, y):
        self._dirty = True
        if self._dirty_rect is None:
            self._dirty_rect = (x, y, x + 1, y + 1)
        else:
            x0, y0, x1, y1 = self._dirty_rect
            self._dirty_rect = (min(x0, x), min(y0, y), max(x1, x + 1), max(y1, y + 1))

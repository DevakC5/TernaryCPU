from trinary.display.framebuffer import Framebuffer
from trinary.display.constants import VRAM_BASE, DISPLAY_WIDTH, DISPLAY_HEIGHT, VRAM_SIZE
from trinary.conversion import ternary_to_decimal, decimal_to_ternary


class DisplayController:
    def __init__(self, memory):
        self.memory = memory
        self.framebuffer = Framebuffer()
        self.vram_base = VRAM_BASE

    def set_pixel(self, x, y, color):
        self.framebuffer.set_pixel(x, y, color)
        addr = self.vram_base + y * DISPLAY_WIDTH + x
        self.memory.store(addr, decimal_to_ternary(color))

    def get_pixel(self, x, y):
        addr = self.vram_base + y * DISPLAY_WIDTH + x
        raw = self.memory.load(addr)
        val = ternary_to_decimal(raw)
        if 0 <= val <= 8:
            return val
        return 0

    def clear(self, color=0):
        self.framebuffer.clear(color)
        for addr in range(self.vram_base, self.vram_base + VRAM_SIZE):
            self.memory.store(addr, decimal_to_ternary(color))

    def sync_from_memory(self):
        for addr in range(VRAM_SIZE):
            y = addr // DISPLAY_WIDTH
            x = addr % DISPLAY_WIDTH
            raw = self.memory.load(self.vram_base + addr)
            val = ternary_to_decimal(raw)
            if 0 <= val <= 8:
                self.framebuffer.set_pixel(x, y, val)

    def sync_to_memory(self):
        buf = self.framebuffer.get_buffer()
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                addr = self.vram_base + y * DISPLAY_WIDTH + x
                self.memory.store(addr, decimal_to_ternary(buf[y][x]))

    def is_dirty(self):
        return self.framebuffer.is_dirty()

    def clear_dirty(self):
        self.framebuffer.clear_dirty()

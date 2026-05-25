from trinary.display import (
    Framebuffer, DisplayController, KeyboardMapper,
    VRAM_BASE, DISPLAY_WIDTH, DISPLAY_HEIGHT, VRAM_SIZE,
    KEYBOARD_ADDR, KEYBOARD_STATE_ADDR,
    PALETTE,
)
from trinary.memory import Memory
from trinary.conversion import decimal_to_ternary as d2t, ternary_to_decimal as t2d


class TestFramebuffer:
    def setup_method(self):
        self.fb = Framebuffer()

    def test_buffer_size(self):
        assert self.fb.width == DISPLAY_WIDTH
        assert self.fb.height == DISPLAY_HEIGHT
        buf = self.fb.get_buffer()
        assert len(buf) == DISPLAY_HEIGHT
        assert len(buf[0]) == DISPLAY_WIDTH

    def test_initial_all_black(self):
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                assert self.fb.get_pixel(x, y) == 0

    def test_set_and_get_pixel(self):
        self.fb.set_pixel(10, 10, 3)
        assert self.fb.get_pixel(10, 10) == 3
        assert self.fb.get_pixel(0, 0) == 0

    def test_set_pixel_clamps_bounds(self):
        self.fb.set_pixel(-1, 0, 2)
        self.fb.set_pixel(0, -1, 2)
        self.fb.set_pixel(DISPLAY_WIDTH, 0, 2)
        self.fb.set_pixel(0, DISPLAY_HEIGHT, 2)
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                assert self.fb.get_pixel(x, y) == 0

    def test_set_pixel_invalid_color(self):
        self.fb.set_pixel(0, 0, 9)
        assert self.fb.get_pixel(0, 0) == 0
        self.fb.set_pixel(0, 0, -1)
        assert self.fb.get_pixel(0, 0) == 0
        self.fb.set_pixel(0, 0, 3)
        assert self.fb.get_pixel(0, 0) == 3

    def test_clear(self):
        self.fb.set_pixel(0, 0, 3)
        self.fb.set_pixel(63, 63, 5)
        self.fb.clear()
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                assert self.fb.get_pixel(x, y) == 0

    def test_dirty_tracking(self):
        assert not self.fb.is_dirty()
        self.fb.set_pixel(0, 0, 1)
        assert self.fb.is_dirty()
        self.fb.clear_dirty()
        assert not self.fb.is_dirty()
        self.fb.clear()
        assert self.fb.is_dirty()


class TestDisplayController:
    def setup_method(self):
        self.memory = Memory(10000)
        self.dc = DisplayController(self.memory)

    def test_set_pixel_updates_memory(self):
        self.dc.set_pixel(0, 0, 3)
        addr = VRAM_BASE
        assert t2d(self.memory.load(addr)) == 3

    def test_get_pixel_from_memory(self):
        addr = VRAM_BASE + 10 * DISPLAY_WIDTH + 5
        self.memory.store(addr, d2t(7))
        assert self.dc.get_pixel(5, 10) == 7

    def test_clear_clears_all(self):
        self.dc.set_pixel(0, 0, 3)
        self.dc.set_pixel(63, 63, 5)
        self.dc.clear()
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                assert self.dc.get_pixel(x, y) == 0

    def test_sync_from_memory(self):
        addr = VRAM_BASE + 5 * DISPLAY_WIDTH + 3
        self.memory.store(addr, d2t(4))
        self.dc.sync_from_memory()
        assert self.dc.framebuffer.get_pixel(3, 5) == 4

    def test_sync_to_memory(self):
        self.dc.framebuffer.set_pixel(10, 20, 6)
        self.dc.sync_to_memory()
        addr = VRAM_BASE + 20 * DISPLAY_WIDTH + 10
        assert t2d(self.memory.load(addr)) == 6


class TestKeyboardMapper:
    def setup_method(self):
        self.memory = Memory(10000)
        self.kb = KeyboardMapper(self.memory)

    def test_write_key(self):
        self.kb.write_key(65)
        assert t2d(self.memory.load(KEYBOARD_ADDR)) == 65
        assert t2d(self.memory.load(KEYBOARD_STATE_ADDR)) == 1

    def test_read_key(self):
        self.kb.write_key(65)
        assert self.kb.read_key() == 65

    def test_is_key_pressed(self):
        assert not self.kb.is_key_pressed()
        self.kb.write_key(65)
        assert self.kb.is_key_pressed()

    def test_clear_key(self):
        self.kb.write_key(65)
        self.kb.clear_key()
        assert t2d(self.memory.load(KEYBOARD_STATE_ADDR)) == 0
        assert not self.kb.is_key_pressed()

    def test_roundtrip(self):
        for code in [32, 65, 97, 48, 13, 27]:
            self.kb.write_key(code)
            assert self.kb.read_key() == code


class TestMemoryHooks:
    def test_write_hook_fires(self):
        mem = Memory(10000)
        calls = []
        mem.register_write_hook(1000, 2000, lambda addr, val: calls.append((addr, val)))
        mem.store(1500, d2t(5))
        assert len(calls) == 1
        assert calls[0][0] == 1500
        assert calls[0][1] == d2t(5)

    def test_write_hook_outside_range(self):
        mem = Memory(10000)
        calls = []
        mem.register_write_hook(1000, 2000, lambda addr, val: calls.append((addr, val)))
        mem.store(500, d2t(3))
        assert len(calls) == 0

    def test_palette_defined(self):
        assert len(PALETTE) == 9
        for i in range(9):
            assert i in PALETTE
            assert len(PALETTE[i]) == 3
            for c in PALETTE[i]:
                assert 0 <= c <= 255

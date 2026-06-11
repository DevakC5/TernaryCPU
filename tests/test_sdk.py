import json
import tempfile
import os
import pytest

from trinary.sdk.sprites import Sprite, DEFAULT_SPRITES, make_sprite_from_strings
from trinary.sdk.tilemap import TileMap
from trinary.sdk.animation import Animation
from trinary.sdk.input import Input
from trinary.sdk.audio import Audio
from trinary.sdk.cartridge import Cartridge
from trinary.sdk.engine import Engine
from trinary.sdk.api import cls, spr, set_engine


class FakeFramebuffer:
    def __init__(self):
        self.width = 64
        self.height = 64
        self._pixels = [[0] * 64 for _ in range(64)]

    def set_pixel(self, x, y, color):
        if 0 <= x < 64 and 0 <= y < 64:
            self._pixels[y][x] = color

    def get_pixel(self, x, y):
        if 0 <= x < 64 and 0 <= y < 64:
            return self._pixels[y][x]
        return 0

    def clear(self, color=0):
        for y in range(64):
            for x in range(64):
                self._pixels[y][x] = color


@pytest.fixture
def fb():
    return FakeFramebuffer()


@pytest.fixture
def engine(fb):
    return Engine(fb)


# --- Sprite tests ---

class TestSprite:
    def test_create_sprite(self):
        s = Sprite(8, 8)
        assert s.width == 8
        assert s.height == 8
        assert all(s.data[y][x] == 0 for y in range(8) for x in range(8))

    def test_set_get_pixel(self):
        s = Sprite(16, 16)
        s.set_pixel(5, 7, 3)
        assert s.get_pixel(5, 7) == 3
        assert s.get_pixel(0, 0) == 0

    def test_out_of_bounds(self):
        s = Sprite(8, 8)
        s.set_pixel(100, 100, 5)
        assert s.get_pixel(10, 10) == 0

    def test_fill(self):
        s = Sprite(4, 4)
        s.fill(7)
        assert all(s.data[y][x] == 7 for y in range(4) for x in range(4))

    def test_copy(self):
        s = Sprite(4, 4, [[1, 2, 3, 4] for _ in range(4)])
        c = s.copy()
        c.set_pixel(0, 0, 9)
        assert s.get_pixel(0, 0) == 1
        assert c.get_pixel(0, 0) == 9

    def test_flip_h(self):
        s = Sprite(3, 1, [[1, 2, 3]])
        s.flip_h()
        assert s.data[0] == [3, 2, 1]

    def test_flip_v(self):
        s = Sprite(1, 3, [[1], [2], [3]])
        s.flip_v()
        assert s.data == [[3], [2], [1]]

    def test_blit_to(self):
        fb = FakeFramebuffer()
        s = Sprite(2, 2, [[1, 2], [3, 4]])
        s.blit_to(fb, 0, 0)
        assert fb.get_pixel(0, 0) == 1
        assert fb.get_pixel(1, 0) == 2
        assert fb.get_pixel(0, 1) == 3
        assert fb.get_pixel(1, 1) == 4

    def test_blit_to_transparent(self):
        fb = FakeFramebuffer()
        s = Sprite(2, 2, [[-1, 2], [3, -1]])
        s.transparent = -1
        s.blit_to(fb, 0, 0)
        assert fb.get_pixel(0, 0) == 0
        assert fb.get_pixel(1, 0) == 2
        assert fb.get_pixel(0, 1) == 3
        assert fb.get_pixel(1, 1) == 0

    def test_make_from_strings(self):
        strings = ["12", "34"]
        s = make_sprite_from_strings(strings)
        assert s.width == 2
        assert s.height == 2
        assert s.get_pixel(0, 0) == 1
        assert s.get_pixel(1, 0) == 2
        assert s.get_pixel(0, 1) == 3
        assert s.get_pixel(1, 1) == 4

    def test_default_sprites(self):
        assert "ball" in DEFAULT_SPRITES
        assert DEFAULT_SPRITES["ball"].width == 8
        assert DEFAULT_SPRITES["ball"].height == 8


# --- Animation tests ---

class TestAnimation:
    def test_create(self):
        a = Animation([1, 2, 3], frame_duration=5)
        assert a.current_frame() == 1
        assert not a.is_finished()

    def test_update_frame_advance(self):
        a = Animation([10, 20, 30], frame_duration=3)
        a.play()
        for _ in range(3):
            a.update()
        assert a.current_frame() == 20

    def test_loop(self):
        a = Animation([1, 2], frame_duration=2, loop=True)
        a.play()
        for _ in range(4):
            a.update()
        assert a.current_frame() == 1

    def test_no_loop(self):
        a = Animation([1, 2], frame_duration=2, loop=False)
        a.play()
        for _ in range(5):
            a.update()
        assert a.current_frame() == 2
        assert a.is_finished()

    def test_reset(self):
        a = Animation([1, 2], frame_duration=2)
        a.play()
        for _ in range(3):
            a.update()
        a.reset()
        assert a.current_frame() == 1
        assert not a.is_finished()

    def test_stop(self):
        a = Animation([1, 2], frame_duration=2)
        a.play()
        a.stop()
        a.update()
        assert a.current_frame() == 1

    def test_pause_resume(self):
        a = Animation([1, 2], frame_duration=2)
        a.play()
        a.update()
        a.update()
        a.pause()
        ca = a.current_frame()
        for _ in range(5):
            a.update()
        assert a.current_frame() == ca
        a.resume()
        a.update()
        a.update()
        assert a.current_frame() != ca


# --- TileMap tests ---

class TestTileMap:
    def test_create(self):
        tm = TileMap(10, 10)
        assert tm.cols == 10
        assert tm.rows == 10

    def test_set_get_tile(self):
        tm = TileMap(10, 10)
        tm.set_tile(3, 5, 7)
        assert tm.get_tile(3, 5) == 7

    def test_out_of_bounds(self):
        tm = TileMap(10, 10)
        tm.set_tile(100, 100, 5)
        assert tm.get_tile(100, 100) == 0

    def test_collision(self):
        tm = TileMap(10, 10)
        tm.set_collision(2, 3, True)
        assert tm.is_solid(2, 3) is True
        assert tm.is_solid(0, 0) is False

    def test_collision_out_of_bounds(self):
        tm = TileMap(10, 10)
        assert tm.is_solid(100, 100) is True

    def test_fill(self):
        tm = TileMap(5, 5)
        tm.fill(9)
        for r in range(5):
            for c in range(5):
                assert tm.get_tile(c, r) == 9

    def test_pixel_to_tile(self):
        tm = TileMap(10, 10)
        assert tm.pixel_to_tile(15, 23) == (1, 2)
        assert tm.pixel_to_tile(0, 0) == (0, 0)
        assert tm.pixel_to_tile(7, 7) == (0, 0)
        assert tm.pixel_to_tile(8, 8) == (1, 1)

    def test_render_empty(self):
        fb = FakeFramebuffer()
        tm = TileMap(10, 10)
        tm.render(fb)
        assert fb.get_pixel(0, 0) == 0

    def test_render_with_sprite_sheet(self):
        fb = FakeFramebuffer()
        tm = TileMap(10, 10)
        wall = Sprite(8, 8, [[3] * 8 for _ in range(8)])
        tm._sprite_sheet = [wall]
        tm.set_tile(1, 1, 1)
        tm.camera_x = 0
        tm.camera_y = 0
        tm.render(fb)
        assert fb.get_pixel(8, 8) == 3

    def test_set_get_layer(self):
        tm = TileMap(5, 5)
        tm.set_layer(2, 3, 1)
        assert tm.get_layer(2, 3) == 1
        assert tm.get_layer(0, 0) == 0

    def test_load_from_grid(self):
        tm = TileMap(3, 3)
        grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        tm.load_from_grid(grid)
        assert tm.get_tile(0, 0) == 1
        assert tm.get_tile(2, 2) == 9


# --- Input tests ---

class TestInput:
    def test_create(self):
        inp = Input()
        assert not inp.btn("UP")
        assert not inp.btnp("DOWN")

    def test_btn(self):
        inp = Input()
        inp._state["LEFT"] = True
        assert inp.btn("LEFT")
        assert not inp.btn("RIGHT")

    def test_btnp(self):
        inp = Input()
        inp._state["A"] = True
        assert inp.btnp("A")
        inp._old_state["A"] = True
        inp._state["A"] = True
        assert not inp.btnp("A")

    def test_clear(self):
        inp = Input()
        inp._state["UP"] = True
        inp.clear()
        assert not inp.btn("UP")


# --- Audio tests ---

class TestAudio:
    def test_default_enabled(self):
        a = Audio()
        assert a._enabled is True

    def test_enable_disable(self):
        a = Audio()
        a.enable()
        assert a._enabled is True
        a.disable()
        assert a._enabled is False

    def test_play_beep(self):
        a = Audio()
        a.enable()
        a.play_beep(440, 0.1)
        assert len(a._notes) == 1
        a.clear()
        assert len(a._notes) == 0


# --- Cartridge tests ---

class TestCartridge:
    def test_save_load_roundtrip(self):
        c = Cartridge()
        c.name = "Test Cart"
        c.author = "Tester"
        c.code = "LOAD R0 1\nHALT"
        s = Sprite(4, 4, [[1, 2, 3, 4] for _ in range(4)])
        c.sprites.append(s)
        c.tilemap = [[1, 2], [3, 4]]
        d = c.to_dict()
        c2 = Cartridge.from_dict(d)
        assert c2.name == "Test Cart"
        assert c2.author == "Tester"
        assert c2.code == "LOAD R0 1\nHALT"
        assert len(c2.sprites) == 1
        assert c2.sprites[0].width == 4
        assert c2.sprites[0].height == 4
        assert c2.tilemap == [[1, 2], [3, 4]]

    def test_save_load_file(self):
        c = Cartridge()
        c.name = "File Test"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            c.save(path)
            c2 = Cartridge.load(path)
            assert c2.name == "File Test"
        finally:
            os.unlink(path)

    def test_to_json(self):
        c = Cartridge()
        c.name = "JSON Test"
        j = c.to_json()
        assert '"name": "JSON Test"' in j

    def test_from_json(self):
        j = '{"format": "TERNARY_CARTRIDGE", "name": "From JSON", "sprites": [], "tilemap_data": []}'
        c = Cartridge.from_json(j)
        assert c.name == "From JSON"

    def test_default_values(self):
        c = Cartridge()
        assert c.name == "Untitled"
        assert c.author == "Anonymous"
        assert c.version == "0.1"
        assert c.sprites == []
        assert c.tilemap == []


# --- Engine tests ---

class TestEngine:
    def test_create(self, engine):
        assert engine.fb is not None
        assert engine.background_color == 0

    def test_clear(self, engine):
        engine.clear(5)
        assert engine.fb.get_pixel(0, 0) == 5
        assert engine.fb.get_pixel(63, 63) == 5

    def test_draw_sprite(self, engine):
        s = Sprite(2, 2, [[1, 2], [3, 4]])
        engine.draw_sprite(s, 10, 10)
        assert engine.fb.get_pixel(10, 10) == 1
        assert engine.fb.get_pixel(11, 11) == 4

    def test_draw_rect(self, engine):
        engine.draw_rect(5, 5, 3, 3, 7)
        assert engine.fb.get_pixel(5, 5) == 7
        assert engine.fb.get_pixel(7, 7) == 7
        assert engine.fb.get_pixel(4, 5) == 0

    def test_set_get_pixel(self, engine):
        engine.set_pixel(20, 20, 6)
        assert engine.get_pixel(20, 20) == 6

    def test_load_sprite(self, engine):
        s = Sprite(4, 4)
        idx = engine.load_sprite(s)
        assert idx == 0
        assert len(engine.sprites) == 1

    def test_add_animation(self, engine):
        a = Animation([1, 2], frame_duration=2)
        idx = engine.add_animation(a)
        assert idx == 0
        assert len(engine.animations) == 1

    def test_init_shutdown(self, engine):
        engine.init()
        assert engine._running is True
        engine.shutdown()
        assert engine._running is False

    def test_update_animations(self, engine):
        a = Animation([1, 2], frame_duration=2)
        a.play()
        engine.add_animation(a)
        engine.update()
        assert a.current_frame() == 1
        engine.update()
        assert a.current_frame() == 2

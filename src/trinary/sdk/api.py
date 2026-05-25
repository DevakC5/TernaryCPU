from trinary.sdk.sprites import Sprite, DEFAULT_SPRITES, make_sprite_from_strings
from trinary.sdk.tilemap import TileMap
from trinary.sdk.animation import Animation
from trinary.sdk import input as sdk_input
from trinary.sdk.audio import audio
from trinary.sdk.cartridge import Cartridge
from trinary.sdk.runtime import Runtime
from trinary.sdk.engine import Engine

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        from trinary.display.framebuffer import Framebuffer
        _engine = Engine(Framebuffer())
    return _engine


def set_engine(engine):
    global _engine
    _engine = engine


def cls(color=0):
    _get_engine().clear(color)


def spr(sprite, x, y, color_override=None):
    if isinstance(sprite, int):
        e = _get_engine()
        if 0 <= sprite < len(e.sprites):
            sprite = e.sprites[sprite]
        else:
            return
    _get_engine().draw_sprite(sprite, x, y, color_override)


def btn(name):
    return sdk_input.btn(name)


def btnp(name):
    return sdk_input.btnp(name)


def print_text(text, x, y, color=7):
    e = _get_engine()
    ox, oy = x, y
    for ch in text:
        ascii_sprites = e.sprites
        idx = ord(ch)
        if 0 <= idx < len(ascii_sprites):
            spr(ascii_sprites[idx], ox, oy, color)
        ox += 8


def pixel(x, y, color=7):
    _get_engine().set_pixel(x, y, color)


def rect(x, y, w, h, color=7):
    _get_engine().draw_rect(x, y, w, h, color)


def poll_input(memory):
    sdk_input.poll(memory)


def sfx(frequency=440, duration=0.1):
    audio.play_beep(frequency, duration)


def load_cartridge(path):
    return Cartridge.load(path)


def run_demo(engine_fn, title=None):
    from trinary.display.framebuffer import Framebuffer
    fb = Framebuffer()
    eng = engine_fn(fb)
    set_engine(eng)
    rt = Runtime(eng, target_fps=30)
    rt.run()


__all__ = [
    "cls", "spr", "btn", "btnp", "print_text",
    "pixel", "rect", "sfx",
    "Sprite", "DEFAULT_SPRITES", "make_sprite_from_strings",
    "TileMap", "Animation", "Cartridge",
    "Engine", "Runtime",
    "set_engine", "load_cartridge", "run_demo",
    "poll_input",
]

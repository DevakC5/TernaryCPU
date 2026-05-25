from trinary.sdk.sprites import Sprite
from trinary.sdk.tilemap import TileMap
from trinary.sdk.animation import Animation
from trinary.sdk.input import Input
from trinary.sdk.audio import Audio
from trinary.sdk.constants import SPRITE_SIZE


class Engine:
    def __init__(self, fb):
        self.fb = fb
        self._width = fb.width
        self._height = fb.height
        self.sprites = []
        self.tilemap = TileMap()
        self.animations = []
        self.input = Input()
        self.audio = Audio()
        self.background_color = 0
        self._running = False

    def init(self):
        self._running = True
        self.clear()

    def clear(self, color=None):
        if color is not None:
            self.background_color = color
        self.fb.clear(self.background_color)

    def update(self):
        for anim in self.animations:
            anim.update()

    def render(self):
        pass

    def shutdown(self):
        self._running = False

    def draw_sprite(self, sprite, x, y, color_override=None):
        if isinstance(sprite, Sprite):
            sprite.blit_to(self.fb, x, y, color_override)

    def draw_rect(self, x, y, w, h, color):
        for dy in range(h):
            for dx in range(w):
                self.fb.set_pixel(x + dx, y + dy, color)

    def set_pixel(self, x, y, color):
        self.fb.set_pixel(x, y, color)

    def get_pixel(self, x, y):
        return self.fb.get_pixel(x, y)

    def load_sprite(self, sprite):
        self.sprites.append(sprite)
        return len(self.sprites) - 1

    def add_animation(self, anim):
        self.animations.append(anim)
        return len(self.animations) - 1

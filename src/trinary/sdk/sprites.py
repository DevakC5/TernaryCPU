from trinary.sdk.constants import SPRITE_SIZE, TRANSPARENT


class Sprite:
    def __init__(self, width=SPRITE_SIZE, height=SPRITE_SIZE, data=None):
        self.width = width
        self.height = height
        self.transparent = TRANSPARENT
        if data:
            self.data = [list(row) for row in data]
        else:
            self.data = [[0] * width for _ in range(height)]

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y][x] = color

    def get_pixel(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x]
        return 0

    def fill(self, color):
        for y in range(self.height):
            for x in range(self.width):
                self.data[y][x] = color

    def flip_h(self):
        for row in self.data:
            row.reverse()

    def flip_v(self):
        self.data.reverse()

    def copy(self):
        s = Sprite(self.width, self.height)
        s.data = [row[:] for row in self.data]
        s.transparent = self.transparent
        return s

    def blit_to(self, fb, x, y, color_override=None):
        for sy in range(self.height):
            for sx in range(self.width):
                color = self.data[sy][sx]
                if color == self.transparent:
                    continue
                if color_override is not None:
                    color = color_override
                fb.set_pixel(x + sx, y + sy, color)


def make_sprite_from_strings(strings):
    h = len(strings)
    w = max(len(s) for s in strings) if strings else 0
    data = []
    for s in strings:
        row = [int(c) if c.isdigit() else 0 for c in s[:w]]
        while len(row) < w:
            row.append(0)
        data.append(row)
    return Sprite(w, h, data)


DEFAULT_SPRITES = {
    "ball": Sprite(8, 8, [
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 2, 2, 2, 2, 2, 2, 0],
        [2, 2, 2, 2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2, 2, 2, 2],
        [0, 2, 2, 2, 2, 2, 2, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 2, 2, 0, 0, 0],
    ]),
    "paddle": Sprite(8, 8, [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [2, 2, 2, 2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2, 2, 2, 2],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]),
    "player": Sprite(8, 8, [
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 0, 5, 5, 5, 5, 0, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 2, 2, 5, 5, 2, 2, 0],
        [0, 2, 2, 5, 5, 2, 2, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 2, 2, 0, 0, 0],
    ]),
    "brick": Sprite(8, 8, [
        [3, 3, 3, 3, 3, 3, 3, 3],
        [3, 0, 3, 0, 3, 0, 3, 0],
        [3, 3, 3, 3, 3, 3, 3, 3],
        [3, 0, 3, 0, 3, 0, 3, 0],
        [3, 3, 3, 3, 3, 3, 3, 3],
        [3, 0, 3, 0, 3, 0, 3, 0],
        [3, 3, 3, 3, 3, 3, 3, 3],
        [3, 0, 3, 0, 3, 0, 3, 0],
    ]),
    "snake_head": Sprite(8, 8, [
        [0, 0, 0, 4, 4, 0, 0, 0],
        [0, 0, 4, 4, 4, 4, 0, 0],
        [0, 4, 2, 4, 4, 2, 4, 0],
        [4, 4, 4, 4, 4, 4, 4, 4],
        [4, 4, 4, 4, 4, 4, 4, 4],
        [0, 4, 4, 4, 4, 4, 4, 0],
        [0, 0, 4, 4, 4, 4, 0, 0],
        [0, 0, 0, 4, 4, 0, 0, 0],
    ]),
}

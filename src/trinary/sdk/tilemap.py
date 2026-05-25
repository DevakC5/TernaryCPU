from trinary.sdk.constants import TILE_SIZE, MAP_COLS, MAP_ROWS, TRANSPARENT


class TileMap:
    def __init__(self, cols=MAP_COLS, rows=MAP_ROWS):
        self.cols = cols
        self.rows = rows
        self.tiles = [[0] * cols for _ in range(rows)]
        self.collision = [[False] * cols for _ in range(rows)]
        self.layers = [[0] * cols for _ in range(rows)]
        self.camera_x = 0
        self.camera_y = 0
        self._sprite_sheet = []

    def set_sprite_sheet(self, sprites):
        self._sprite_sheet = list(sprites)

    def set_tile(self, col, row, tile_id):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            self.tiles[row][col] = tile_id

    def get_tile(self, col, row):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.tiles[row][col]
        return 0

    def set_collision(self, col, row, solid=True):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            self.collision[row][col] = solid

    def is_solid(self, col, row):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.collision[row][col]
        return True

    def render(self, fb):
        start_col = max(0, self.camera_x // TILE_SIZE)
        start_row = max(0, self.camera_y // TILE_SIZE)
        vis_cols = fb.width // TILE_SIZE + 2
        vis_rows = fb.height // TILE_SIZE + 2
        for r in range(vis_rows):
            for c in range(vis_cols):
                tc = start_col + c
                tr = start_row + r
                if tc >= self.cols or tr >= self.rows:
                    continue
                tid = self.tiles[tr][tc]
                if tid == 0 or not self._sprite_sheet:
                    continue
                sprite_idx = (tid - 1) % len(self._sprite_sheet)
                sprite = self._sprite_sheet[sprite_idx]
                sx = tc * TILE_SIZE - self.camera_x
                sy = tr * TILE_SIZE - self.camera_y
                sprite.blit_to(fb, sx, sy)

    def pixel_to_tile(self, px, py):
        return (px // TILE_SIZE, py // TILE_SIZE)

    def fill(self, tile_id):
        for r in range(self.rows):
            for c in range(self.cols):
                self.tiles[r][c] = tile_id

    def set_layer(self, col, row, layer):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            self.layers[row][col] = layer

    def get_layer(self, col, row):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.layers[row][col]
        return 0

    def load_from_grid(self, grid):
        for r, row in enumerate(grid):
            for c, val in enumerate(row):
                if r < self.rows and c < self.cols:
                    self.tiles[r][c] = val

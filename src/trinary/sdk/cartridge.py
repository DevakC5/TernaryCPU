import json
import os

from trinary.sdk.constants import SPRITE_SIZE
from trinary.sdk.sprites import Sprite


class Cartridge:
    def __init__(self):
        self.name = "Untitled"
        self.author = "Anonymous"
        self.description = ""
        self.version = "0.1"
        self.sprites = []
        self.tilemap = []
        self.tilemap_cols = 32
        self.tilemap_rows = 32
        self.code = ""
        self.config = {}

    def to_dict(self):
        return {
            "format": "TERNARY_CARTRIDGE",
            "name": self.name,
            "author": self.author,
            "description": self.description,
            "version": self.version,
            "sprites": [
                {"width": s.width, "height": s.height, "data": s.data}
                for s in self.sprites
            ],
            "tilemap_data": self.tilemap,
            "tilemap_cols": self.tilemap_cols,
            "tilemap_rows": self.tilemap_rows,
            "code": self.code,
            "config": self.config,
        }

    @classmethod
    def from_dict(cls, data):
        c = cls()
        c.name = data.get("name", "Untitled")
        c.author = data.get("author", "Anonymous")
        c.description = data.get("description", "")
        c.version = data.get("version", "0.1")
        for sd in data.get("sprites", []):
            s = Sprite(sd.get("width", 8), sd.get("height", 8), sd.get("data"))
            c.sprites.append(s)
        c.tilemap = data.get("tilemap_data", [])
        c.tilemap_cols = data.get("tilemap_cols", 32)
        c.tilemap_rows = data.get("tilemap_rows", 32)
        c.code = data.get("code", "")
        c.config = data.get("config", {})
        return c

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, text):
        return cls.from_dict(json.loads(text))

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path):
        with open(path) as f:
            return cls.from_dict(json.load(f))

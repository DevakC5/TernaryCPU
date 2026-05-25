# Trinary Fantasy Console — SDK Documentation

The Trinary Fantasy Console brings retro game development to the ternary computer. Inspired by PICO-8, TIC-80, and CHIP-8, it provides a sprite engine, tilemap system, animation API, and game loop runtime — all running on the Trinary CPU simulator.

## Architecture Overview

```
                   ┌──────────────────────┐
                   │    Demo Game Code     │
                   │  (update/render)      │
                   └──────────┬───────────┘
                              │
                   ┌──────────▼───────────┐
                   │    SDK API (api.py)   │
                   │  cls/spr/btn/pixel   │
                   └──────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────▼───┐  ┌───────▼──────┐  ┌─────▼─────┐
     │  Runtime   │  │   Engine     │  │ Cartridge │
     │ game loop  │  │ game state   │  │  I/O      │
     └────────────┘  └───────┬──────┘  └───────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌──────▼──────┐  ┌───▼───────┐
     │  Framebuf  │  │  Memory     │  │  CPU      │
     │  (64×64)   │  │  (VRAM)    │  │  (ALU)    │
     └────────────┘  └─────────────┘  └───────────┘
```

## Game Loop Flow

```
Runtime.run(update_fn, render_fn)
  │
  ├─ engine.init()                 # One-time setup
  │
  ├─ Fixed-timestep loop (30 FPS)
  │   │
  │   ├─ poll_input()              # Read keyboard register
  │   ├─ update_fn()               # Game logic
  │   ├─ engine.update()           # Animation ticks
  │   ├─ render_fn()               # Draw calls
  │   └─ engine.render()           # Post-processing
  │
  └─ engine.shutdown()             # Cleanup
```

### Fixed Timestep

The Runtime uses a fixed timestep accumulator pattern. At 30 FPS, each tick is ~33.3ms. If the CPU falls behind, multiple updates run per frame to catch up, keeping physics deterministic.

## Sprite System

### Sprite Class

The `Sprite` class represents a pixel art image:

```python
from trinary.sdk.api import Sprite

# 8×8 sprite from 2D data
heart = Sprite(8, 8, [
    [0,1,1,0,0,1,1,0],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,0,0],
    [0,0,0,1,1,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
])
```

### Sprite from Strings

```python
from trinary.sdk.api import make_sprite_from_strings

cross = make_sprite_from_strings([
    "101",
    "010",
    "101",
])
```

### Default Sprites

Built-in sprites in `DEFAULT_SPRITES`: `ball`, `paddle`, `player`, `brick`, `snake_head`.

```python
from trinary.sdk.api import DEFAULT_SPRITES
spr(DEFAULT_SPRITES["ball"], x, y)
```

### Blitting and Transparency

- `sprite.blit_to(fb, x, y)` — draw onto framebuffer; pixels matching `transparent` (-1) are skipped
- `sprite.copy()` — deep copy
- `sprite.flip_h()` / `sprite.flip_v()` — mirror
- `sprite.fill(color)` — fill all pixels

## Tilemap Engine

The `TileMap` class provides a 2D grid with camera scrolling and collision detection.

```python
from trinary.sdk.api import TileMap

tm = TileMap(32, 32)          # 32×32 tile grid
tm.set_sprite_sheet(sprites)  # tile ID → sprite mapping
tm.set_tile(col, row, id)     # place tile
tm.set_collision(col, row)    # mark as solid
tm.camera_x = 16              # scroll camera
tm.camera_y = 8

# In render:
tm.render(fb)                 # draw visible tiles only

# Collision:
if tm.is_solid(tx, ty):       # blocked?
    # handle collision
```

### Tile Coordinates

- `tilemap.pixel_to_tile(px, py)` → `(col, row)` — pixel-space to grid
- Tiles are 8×8 pixels by default
- Only tiles within the camera viewport are rendered (frustum culling)

## Animation System

```python
from trinary.sdk.api import Animation

# Frame-by-frame animation
walk = Animation(
    frames=[sprite1, sprite2, sprite3, sprite4],
    frame_duration=6,  # ticks per frame
    loop=True,
)

walk.play()
# In update:
walk.update()

# In render:
spr(walk.current_frame(), x, y)
```

### Animation Controls

- `play()` — start from beginning
- `stop()` / `pause()` / `resume()`
- `reset()` — rewind to start
- `is_finished()` — non-looping animations report done

## Input API

### Button Mapping

| Button  | Key         | Function     |
|---------|-------------|--------------|
| LEFT    | A / ←      | `btn("LEFT")`  |
| RIGHT   | D / →      | `btn("RIGHT")` |
| UP      | W / ↑      | `btn("UP")`    |
| DOWN    | S / ↓      | `btn("DOWN")`  |
| A       | Z / Space   | `btn("A")`     |
| B       | X / Shift   | `btn("B")`     |
| START   | Enter       | `btn("START")` |
| SELECT  | Escape      | `btn("SELECT")`|

```python
from trinary.sdk.api import btn, btnp

if btn("LEFT"):   x -= 1    # held
if btnp("A"):     jump()     # single press
```

Input reads from CPU memory address 9000 (the keyboard register).

## Audio

The audio system is currently a stub. `sfx(freq, dur)` stores sound requests but does not play them yet. A future mixer will support:

- Square wave beeps
- Named sound effects
- Channel-based mixing

## Cartridge Format

Cartridges bundle game code, sprites, tilemaps, and metadata into a single JSON file.

```json
{
  "format": "TERNARY_CARTRIDGE",
  "name": "Pong",
  "author": "You",
  "version": "1.0",
  "description": "Classic Pong",
  "sprites": [
    {
      "width": 8,
      "height": 8,
      "data": [[0,0,2,2,2,2,0,0], [0,2,2,2,2,2,2,0], ...]
    }
  ],
  "tilemap_data": [[1, 1, 0, 1, 1], [0, 0, 0, 0, 0], ...],
  "tilemap_cols": 32,
  "tilemap_rows": 32,
  "code": "LOAD R0 1\nADD R0 R0\nHALT",
  "config": {
    "palette": "default",
    "fps": 30
  }
}
```

```python
from trinary.sdk.api import Cartridge

c = Cartridge.load("pong.json")
c.save("pong.json")
```

## SDK API Reference

### Drawing

| Function | Description |
|----------|-------------|
| `cls(color=0)` | Clear screen to color |
| `spr(sprite, x, y, color_override=None)` | Draw sprite by object or index |
| `pixel(x, y, color=7)` | Set a single pixel |
| `rect(x, y, w, h, color=7)` | Draw filled rectangle |
| `print_text(text, x, y, color=7)` | Draw ASCII text (8×8 per char) |

### Input

| Function | Description |
|----------|-------------|
| `btn(name)` | Is button held? |
| `btnp(name)` | Was button just pressed? |
| `poll_input(memory)` | Read keyboard register from memory |

### Audio

| Function | Description |
|----------|-------------|
| `sfx(freq=440, duration=0.1)` | Queue a beep (stub) |

### Engine / Runtime

| Class | Description |
|-------|-------------|
| `Engine(fb)` | Game engine: owns sprites, tilemap, animations, input, audio |
| `Runtime(engine, target_fps=30)` | Fixed-timestep game loop |
| `set_engine(engine)` | Set global engine for API functions |
| `run_demo(engine_fn, title=None)` | Create engine + runtime, start loop |

### Sprites & Tilemaps

| Class / Function | Description |
|-----------------|-------------|
| `Sprite(w, h, data=None)` | Create a sprite |
| `make_sprite_from_strings(strings)` | Create sprite from ASCII art strings |
| `DEFAULT_SPRITES` | Dict of built-in sprites |
| `TileMap(cols=32, rows=32)` | 2D tile grid with collision |

### Animation

| Class | Description |
|-------|-------------|
| `Animation(frames, frame_duration=15, loop=True)` | Frame-based animation |

### Cartridge

| Class / Method | Description |
|----------------|-------------|
| `Cartridge()` | Create new cartridge |
| `c.save(path)` | Save to JSON file |
| `Cartridge.load(path)` | Load from JSON file |
| `c.to_dict()` / `c.to_json()` | Serialize |

## How to Build a Game

```python
from trinary.sdk.api import *
from trinary.display.framebuffer import Framebuffer

# 1. Define state
state = {"x": 32, "y": 32, "dx": 1, "dy": 1}

# 2. Update function
def update():
    poll_input(memory)  # read keyboard
    state["x"] += state["dx"]
    state["y"] += state["dy"]
    if state["x"] <= 0 or state["x"] >= 48:
        state["dx"] = -state["dx"]
    if state["y"] <= 0 or state["y"] >= 48:
        state["dy"] = -state["dy"]

# 3. Render function
def render():
    cls(0)
    rect(state["x"], state["y"], 16, 16, 2)

# 4. Wire up
fb = Framebuffer()
eng = Engine(fb)
eng.state = state
eng.memory = memory
set_engine(eng)
rt = Runtime(eng, target_fps=30)

# 5. Run
rt.run(update, render)
```

## Built-in Demo Games

Run from command line:

```bash
python -m trinary.demo_games pong
python -m trinary.demo_games snake
python -m trinary.demo_games breakout
python -m trinary.demo_games particles
python -m trinary.demo_games paint
python -m trinary.demo_games bouncing_logo
python -m trinary.demo_games tilemap_scroller
python -m trinary.demo_games rpg_movement
```

| Demo | Description |
|------|-------------|
| Pong | Two-player paddle ball game |
| Snake | Classic snake with keyboard controls |
| Breakout | Brick-breaking with paddle |
| Particles | Interactive particle system |
| Paint | Free-form pixel art |
| Bouncing Logo | DVD-style bouncing rectangle |
| Tilemap Scroller | Scrollable 32×32 tile world |
| RPG Movement | Top-down tilemap with collision |

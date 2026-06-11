from trinary.sdk.api import (
    cls, spr, btn, btnp, pixel, rect, print_text, sfx,
    Sprite, DEFAULT_SPRITES, Engine, Runtime, set_engine,
    make_sprite_from_strings, poll_input,
)
from trinary.memory import Memory
from trinary.demo_automaton import demo_automaton, _automaton_update, _automaton_render


def _pong_update(state):
    poll_input(state["memory"])
    state["bx"] += state["bdx"]
    state["by"] += state["bdy"]
    if state["by"] <= 0 or state["by"] >= 56:
        state["bdy"] = -state["bdy"]
    if btn("DOWN") and state["py"] < 56:
        state["py"] += 2
    if btn("UP") and state["py"] > 0:
        state["py"] -= 2
    if btn("A"):
        pass
    if state["bx"] <= 4 and state["py"] <= state["by"] <= state["py"] + 8:
        state["bdx"] = 1
    if state["bx"] >= 56:
        state["bx"], state["by"] = 32, 32
        state["bdx"] = -1
    if state["bx"] < 0:
        state["bx"], state["by"] = 32, 32
        state["bdx"] = 1
    state["score"] += state["bx"] == 0 and state["py"] <= state["by"] <= state["py"] + 8


def _pong_render(state):
    cls(0)
    ball = DEFAULT_SPRITES["ball"]
    paddle = DEFAULT_SPRITES["paddle"]
    spr(ball, state["bx"], state["by"])
    spr(paddle, 2, state["py"])
    spr(paddle, 58, state["py"])


def demo_pong(fb):
    eng = Engine(fb)
    mem = Memory(10000)
    eng.memory = mem
    eng.state = {"bx": 32, "by": 32, "bdx": -1, "bdy": 1, "py": 28, "score": 0, "memory": mem}
    return eng





def _breakout_update(state):
    poll_input(state["memory"])
    state["bx"] += state["bdx"]
    state["by"] += state["bdy"]
    if state["bx"] <= 0 or state["bx"] >= 56:
        state["bdx"] = -state["bdx"]
    if state["by"] <= 0:
        state["bdy"] = -state["bdy"]
    if btn("LEFT") and state["px"] > 0:
        state["px"] -= 2
    if btn("RIGHT") and state["px"] < 56:
        state["px"] += 2
    if state["by"] >= 60:
        state["bx"], state["by"] = 32, 40
        state["bdx"], state["bdy"] = -1, -1
    px, py = state["px"], 60
    if py <= state["by"] <= py + 2 and px <= state["bx"] <= px + 8:
        state["bdy"] = -1
    for brick in list(state["bricks"]):
        bx, by = brick
        if bx <= state["bx"] <= bx + 8 and by <= state["by"] <= by + 4:
            state["bricks"].remove(brick)
            state["bdy"] = -state["bdy"]
            break


def _breakout_render(state):
    cls(0)
    pixel(state["bx"], state["by"], 7)
    rect(state["px"], 60, 8, 2, 7)
    for brick in state["bricks"]:
        rect(brick[0], brick[1], 8, 4, 3)


def demo_breakout(fb):
    eng = Engine(fb)
    mem = Memory(10000)
    eng.memory = mem
    bricks = [(x * 9 + 1, y * 6 + 4) for y in range(4) for x in range(7)]
    eng.state = {
        "bx": 32, "by": 40, "bdx": -1, "bdy": -1,
        "px": 28, "bricks": bricks, "memory": mem,
    }
    return eng


def _particles_update(state):
    poll_input(state["memory"])
    for p in state["particles"]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.3
        p["life"] -= 1
    state["particles"] = [p for p in state["particles"] if p["life"] > 0]
    if len(state["particles"]) < 50:
        import random
        for _ in range(3):
            state["particles"].append({
                "x": 32, "y": 32,
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-2, 2),
                "life": 30,
                "color": random.randint(1, 8),
            })


def _particles_render(state):
    cls(0)
    for p in state["particles"]:
        pixel(int(p["x"]), int(p["y"]), p["color"])


def demo_particles(fb):
    eng = Engine(fb)
    mem = Memory(10000)
    eng.memory = mem
    eng.state = {"particles": [], "memory": mem}
    return eng


def _paint_update(state):
    poll_input(state["memory"])
    dx, dy = 0, 0
    if btn("LEFT"): dx -= 1
    if btn("RIGHT"): dx += 1
    if btn("UP"): dy -= 1
    if btn("DOWN"): dy += 1
    state["cx"] = max(0, min(63, state["cx"] + dx))
    state["cy"] = max(0, min(63, state["cy"] + dy))
    if btn("A"):
        pixel(state["cx"], state["cy"], state["color"])


def _paint_render(state):
    pixel(state["cx"], state["cy"], 8)


def demo_paint(fb):
    eng = Engine(fb)
    mem = Memory(10000)
    eng.memory = mem
    eng.state = {"cx": 32, "cy": 32, "color": 7, "memory": mem}
    return eng


def _bouncing_logo_update(state):
    poll_input(state["memory"])
    state["x"] += state["dx"]
    state["y"] += state["dy"]
    if state["x"] <= 0 or state["x"] >= 48:
        state["dx"] = -state["dx"]
    if state["y"] <= 0 or state["y"] >= 48:
        state["dy"] = -state["dy"]


def _bouncing_logo_render(state):
    cls(0)
    rect(state["x"], state["y"], 16, 16, 2)
    rect(state["x"] + 2, state["y"] + 2, 12, 12, 4)
    pixel(state["x"] + 8, state["y"] + 8, 7)


def demo_bouncing_logo(fb):
    eng = Engine(fb)
    mem = Memory(10000)
    eng.memory = mem
    eng.state = {"x": 24, "y": 24, "dx": 1, "dy": 1, "memory": mem}
    return eng


def _tilemap_scroller_update(state):
    poll_input(state["memory"])
    if btn("RIGHT"):
        state["cam_x"] = min(state["cam_x"] + 2, 128)
    if btn("LEFT"):
        state["cam_x"] = max(state["cam_x"] - 2, 0)
    if btn("DOWN"):
        state["cam_y"] = min(state["cam_y"] + 2, 128)
    if btn("UP"):
        state["cam_y"] = max(state["cam_y"] - 2, 0)
    state["tilemap"].camera_x = state["cam_x"]
    state["tilemap"].camera_y = state["cam_y"]


def _tilemap_scroller_render(state):
    cls(0)
    state["tilemap"].render(state["eng"].fb)


def demo_tilemap_scroller(fb):
    from trinary.sdk.tilemap import TileMap
    eng = Engine(fb)
    mem = Memory(10000)
    eng.memory = mem
    tm = TileMap(32, 32)
    for r in range(32):
        for c in range(32):
            if r == 0 or r == 31 or c == 0 or c == 31:
                tm.set_tile(c, r, 1)
            elif (r + c) % 5 == 0:
                tm.set_tile(c, r, 1)
    tm._sprite_sheet = [DEFAULT_SPRITES["brick"]]
    eng.tilemap = tm
    eng.state = {"cam_x": 0, "cam_y": 0, "tilemap": tm, "eng": eng, "memory": mem}
    return eng


def _rpg_movement_update(state):
    poll_input(state["memory"])
    dx, dy = 0, 0
    if btn("LEFT"): dx = -1
    if btn("RIGHT"): dx = 1
    if btn("UP"): dy = -1
    if btn("DOWN"): dy = 1
    nx = state["px"] + dx
    ny = state["py"] + dy
    tc = nx // 8
    tr = ny // 8
    if not state["tilemap"].is_solid(tc, tr):
        state["px"] = nx
        state["py"] = ny


def _rpg_movement_render(state):
    cls(0)
    state["tilemap"].camera_x = state["px"] - 32
    state["tilemap"].camera_y = state["py"] - 32
    state["tilemap"].render(state["eng"].fb)
    spr(DEFAULT_SPRITES["player"], 32, 32)


def demo_rpg_movement(fb):
    from trinary.sdk.tilemap import TileMap
    eng = Engine(fb)
    mem = Memory(10000)
    eng.memory = mem
    tm = TileMap(16, 16)
    for r in range(16):
        for c in range(16):
            if r == 0 or r == 15 or c == 0 or c == 15:
                tm.set_tile(c, r, 1)
                tm.set_collision(c, r, True)
            elif (r + c) % 7 == 0:
                tm.set_tile(c, r, 1)
                tm.set_collision(c, r, True)
    tm._sprite_sheet = [DEFAULT_SPRITES["brick"]]
    eng.tilemap = tm
    eng.state = {"px": 16, "py": 16, "tilemap": tm, "eng": eng, "memory": mem}
    return eng


def _snake_factory(fb):
    from trinary.snake_game import TALSnake, CPUSnakeDisplay
    from trinary.sdk.engine import Engine
    display = CPUSnakeDisplay(memory=None, width=64, height=64)
    tal = TALSnake(display=display)
    eng = Engine(fb)
    eng.memory = tal.memory
    eng.fb = display
    eng.state = {"engine": tal}
    set_engine(eng)
    return eng


def _snake_update(state):
    state["engine"].update()


def _snake_render(state):
    state["engine"].render()


DEMOS = {
    "pong": (demo_pong, _pong_update, _pong_render),
    "snake": (_snake_factory, _snake_update, _snake_render),
    "breakout": (demo_breakout, _breakout_update, _breakout_render),
    "particles": (demo_particles, _particles_update, _particles_render),
    "paint": (demo_paint, _paint_update, _paint_render),
    "bouncing_logo": (demo_bouncing_logo, _bouncing_logo_update, _bouncing_logo_render),
    "tilemap_scroller": (demo_tilemap_scroller, _tilemap_scroller_update, _tilemap_scroller_render),
    "rpg_movement": (demo_rpg_movement, _rpg_movement_update, _rpg_movement_render),
    "automaton": (demo_automaton, _automaton_update, _automaton_render),
}

_GAME_TITLES = {
    "pong": "Pong",
    "snake": "Snake Deluxe",
    "breakout": "Breakout",
    "particles": "Particle System",
    "paint": "Pixel Paint",
    "bouncing_logo": "Bouncing Logo",
    "tilemap_scroller": "Tilemap Scroller",
    "rpg_movement": "RPG Movement",
}


def run_demo_game(name):
    if name not in DEMOS:
        print(f"Unknown demo: {name}. Choose from: {', '.join(DEMOS)}")
        return
    eng_fn, update_fn, render_fn = DEMOS[name]
    from trinary.display.framebuffer import Framebuffer
    from trinary.ui.game_window import GameWindow
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet("QMainWindow { background-color: #111; }")
    fb = Framebuffer()
    eng = eng_fn(fb)
    set_engine(eng)
    title = _GAME_TITLES.get(name, name.title())
    kwargs = {"target_fps": 30, "title": f"Trinary — {title}"}
    if name == "snake":
        kwargs["pixel_size"] = 8
    w = GameWindow(eng,
                   update_fn=lambda: update_fn(eng.state),
                   render_fn=lambda: render_fn(eng.state),
                   **kwargs)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "pong"
    run_demo_game(name)

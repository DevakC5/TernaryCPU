"""Greenberg-Hastings 3-State Cellular Automaton (excitable media).

Simulates spiraling chemical waves on the Trinary Fantasy Console's 64x64
framebuffer.  Each pixel is a trit: 0=Resting(black), 1=Refractory(dark gray),
2=Excited(white).

Usage:
    python -m trinary.demo_automaton
    python -m trinary.demo_games automaton
"""

import random
from trinary.sdk.api import cls, pixel, Engine, Runtime, set_engine
from trinary.memory import Memory

WIDTH = 64
HEIGHT = 64

# 9-color palette (only 0/1/2 used):
#   0 = Black      — Resting
#   1 = Dark Gray  — Refractory
#   2 = White      — Excited


def demo_automaton(fb):
    eng = Engine(fb)
    mem = Memory(10000)
    eng.memory = mem

    grid = [0] * (WIDTH * HEIGHT)

    cx, cy = WIDTH // 2, HEIGHT // 2
    half = 10
    for y in range(max(0, cy - half), min(HEIGHT, cy + half)):
        row = y * WIDTH
        for x in range(max(0, cx - half), min(WIDTH, cx + half)):
            grid[row + x] = random.randint(0, 2)

    eng.state = {"grid": grid, "memory": mem}
    return eng


def _automaton_update(state):
    g = state["grid"]
    nxt = [0] * (WIDTH * HEIGHT)

    for y in range(HEIGHT):
        row = y * WIDTH
        y_up = y - 1
        y_dn = y + 1
        for x in range(WIDTH):
            i = row + x
            v = g[i]

            if v == 0:
                exc = False
                if y_up >= 0 and g[y_up * WIDTH + x] == 2:
                    exc = True
                elif y_dn < HEIGHT and g[y_dn * WIDTH + x] == 2:
                    exc = True
                elif x > 0 and g[row + x - 1] == 2:
                    exc = True
                elif x < WIDTH - 1 and g[row + x + 1] == 2:
                    exc = True
                nxt[i] = 2 if exc else 0
            elif v == 2:
                nxt[i] = 1
            else:
                nxt[i] = 0

    state["grid"] = nxt


def _automaton_render(state):
    g = state["grid"]
    cls(0)
    for y in range(HEIGHT):
        row = y * WIDTH
        for x in range(WIDTH):
            c = g[row + x]
            if c:
                pixel(x, y, c)


if __name__ == "__main__":
    from trinary.display.framebuffer import Framebuffer
    from trinary.ui.game_window import GameWindow
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet("QMainWindow { background-color: #111; }")

    fb = Framebuffer()
    eng = demo_automaton(fb)
    set_engine(eng)

    w = GameWindow(eng,
                   update_fn=lambda: _automaton_update(eng.state),
                   render_fn=lambda: _automaton_render(eng.state),
                   target_fps=30,
                   title="Trinary — Greenberg-Hastings Automaton")
    w.show()
    sys.exit(app.exec())

from trinary.display.constants import DISPLAY_WIDTH, DISPLAY_HEIGHT, VRAM_BASE
from trinary.display.framebuffer import Framebuffer
from trinary.conversion import decimal_to_ternary as d2t


def demo_pixel_test(fb):
    for i in range(min(DISPLAY_WIDTH, DISPLAY_HEIGHT)):
        fb.set_pixel(i, i, 2)
        fb.set_pixel(DISPLAY_WIDTH - 1 - i, i, 1)


def demo_color_bars(fb):
    for y in range(DISPLAY_HEIGHT):
        for x in range(DISPLAY_WIDTH):
            fb.set_pixel(x, y, (x * 9) // DISPLAY_WIDTH)


def demo_moving_pixel(fb):
    import time
    for t in range(DISPLAY_WIDTH):
        fb.clear()
        fb.set_pixel(t, DISPLAY_HEIGHT // 2, 2)
        time.sleep(0.01)


def demo_bouncing_box(fb):
    import time
    size = 8
    dx, dy = 1, 1
    x, y = 0, 0
    for _ in range(200):
        fb.clear()
        for by in range(size):
            for bx in range(size):
                fb.set_pixel(x + bx, y + by, 3)
                fb.set_pixel(x + bx + 1, y + by + 3, 4)
        x += dx
        y += dy
        if x + size >= DISPLAY_WIDTH or x < 0:
            dx = -dx
        if y + size >= DISPLAY_HEIGHT or y < 0:
            dy = -dy
        time.sleep(0.02)


def demo_noise(fb):
    import random
    rng = random.Random(42)
    for y in range(DISPLAY_HEIGHT):
        for x in range(DISPLAY_WIDTH):
            fb.set_pixel(x, y, rng.randint(0, 8))


def demo_terminal_text(fb):
    text = "HELLO TERNARY WORLD 64x64"
    for i, ch in enumerate(text):
        x = (i * 6) % DISPLAY_WIDTH
        y = (i * 6) // DISPLAY_WIDTH * 8
        for by in range(8):
            for bx in range(6):
                fb.set_pixel(x + bx, y + by, (i % 8) + 1)


def run_graphics_demos():
    fb = Framebuffer()
    print("Running graphics demos on framebuffer...")
    demo_pixel_test(fb)
    print("  pixel_test OK")
    demo_color_bars(fb)
    print("  color_bars OK")
    demo_noise(fb)
    print("  noise OK")
    demo_terminal_text(fb)
    print("  terminal_text OK")
    print("All graphics demos passed.")


if __name__ == "__main__":
    run_graphics_demos()

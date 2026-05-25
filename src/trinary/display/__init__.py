from trinary.display.text_display import DisplayMemoryMap, PixelDisplay, DISPLAY_START, DISPLAY_END, DISPLAY_SIZE
from trinary.display.constants import VRAM_BASE, DISPLAY_WIDTH, DISPLAY_HEIGHT, VRAM_SIZE, KEYBOARD_ADDR, KEYBOARD_STATE_ADDR
from trinary.display.palette import PALETTE, RGB_COLORS, COLOR_NAMES
from trinary.display.framebuffer import Framebuffer
from trinary.display.keyboard import KeyboardMapper
from trinary.display.display_controller import DisplayController

try:
    from trinary.display.display_widget import DisplayWidget
except ImportError:
    class DisplayWidget:
        def __init__(self, *a, **kw): raise ImportError("DisplayWidget requires PyQt6")

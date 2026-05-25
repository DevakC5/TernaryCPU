from trinary.display.constants import KEYBOARD_ADDR, KEYBOARD_STATE_ADDR


class KeyboardMapper:
    def __init__(self, memory):
        self.memory = memory

    def write_key(self, key_code):
        from trinary.conversion import decimal_to_ternary as d2t
        try:
            self.memory.store(KEYBOARD_ADDR, d2t(key_code))
            self.memory.store(KEYBOARD_STATE_ADDR, d2t(1))
        except ValueError:
            pass

    def clear_key(self):
        from trinary.conversion import decimal_to_ternary as d2t
        try:
            self.memory.store(KEYBOARD_STATE_ADDR, d2t(0))
        except ValueError:
            pass

    def read_key(self):
        from trinary.conversion import ternary_to_decimal
        raw = self.memory.load(KEYBOARD_ADDR)
        return ternary_to_decimal(raw)

    def is_key_pressed(self):
        from trinary.conversion import ternary_to_decimal
        raw = self.memory.load(KEYBOARD_STATE_ADDR)
        return ternary_to_decimal(raw) != 0

    def map_qt_key(self, qt_key, text):
        from PyQt6.QtCore import Qt
        mapping = {
            Qt.Key.Key_W: ord("w"),
            Qt.Key.Key_A: ord("a"),
            Qt.Key.Key_S: ord("s"),
            Qt.Key.Key_D: ord("d"),
            Qt.Key.Key_Up: 0x1B | (ord("A") << 8),
            Qt.Key.Key_Down: 0x1B | (ord("B") << 8),
            Qt.Key.Key_Left: 0x1B | (ord("D") << 8),
            Qt.Key.Key_Right: 0x1B | (ord("C") << 8),
            Qt.Key.Key_Space: ord(" "),
            Qt.Key.Key_Return: ord("\n"),
            Qt.Key.Key_Escape: 27,
        }
        if qt_key in mapping:
            return mapping[qt_key]
        if text and 32 <= ord(text) <= 126:
            return ord(text)
        return None

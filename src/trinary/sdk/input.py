from trinary.conversion import ternary_to_decimal


class Input:
    def __init__(self):
        self._state = {}
        self._old_state = {}

    def _read_memory(self, memory):
        from trinary.display.constants import KEYBOARD_ADDR
        raw = memory.load(KEYBOARD_ADDR)
        return ternary_to_decimal(raw)

    def poll(self, memory):
        self._old_state.clear()
        self._old_state.update(self._state)
        self._state.clear()
        code = self._read_memory(memory)
        key_map = {
            ord("w"): "UP", ord("W"): "UP",
            ord("a"): "LEFT", ord("A"): "LEFT",
            ord("s"): "DOWN", ord("S"): "DOWN",
            ord("d"): "RIGHT", ord("D"): "RIGHT",
            ord("z"): "A", ord("Z"): "A",
            ord("x"): "B", ord("X"): "B",
            10: "START", 13: "START",
            32: "SELECT",
        }
        _arrow_map = {
            0x1B | (ord("A") << 8): "UP",
            0x1B | (ord("B") << 8): "DOWN",
            0x1B | (ord("C") << 8): "RIGHT",
            0x1B | (ord("D") << 8): "LEFT",
        }
        key_map.update(_arrow_map)
        if code in key_map:
            self._state[key_map[code]] = True

    def btn(self, name):
        return self._state.get(name.upper(), False)

    def btnp(self, name):
        n = name.upper()
        return self._state.get(n, False) and not self._old_state.get(n, False)

    def clear(self):
        self._state.clear()
        self._old_state.clear()

    def pressed(self, name):
        return self.btnp(name)


_global_input = Input()


def btn(name):
    return _global_input.btn(name)


def btnp(name):
    return _global_input.btnp(name)


def poll(memory):
    _global_input.poll(memory)

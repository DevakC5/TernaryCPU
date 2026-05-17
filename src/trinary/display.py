"""Memory-mapped display system for the ternary computer.

Reserved memory region 200-255 acts as video RAM.
Values stored as ternary-encoded ASCII codes.
The UI reads this region and renders characters on a terminal-like screen.
"""

DISPLAY_START = 200
DISPLAY_END = 255
DISPLAY_SIZE = DISPLAY_END - DISPLAY_START + 1


class DisplayMemoryMap:
    """Backend for memory-mapped text display.

    Reads ternary-encoded ASCII values from a reserved RAM region
    and converts them to displayable characters. Zero-values render
    as spaces. Non-printable codes render as '.'.
    """

    def read_display(self, memory):
        """Read the display buffer from memory.

        Args:
            memory: Memory object with .load(addr) method.

        Returns:
            list: Character strings, one per display cell.
        """
        from trinary.conversion import ternary_to_decimal

        chars = []
        for addr in range(DISPLAY_START, DISPLAY_END + 1):
            raw = memory.load(addr)
            code = ternary_to_decimal(raw)
            if code == 0:
                chars.append(" ")
            elif 32 <= code <= 126:
                chars.append(chr(code))
            else:
                chars.append(".")
        return chars

    def write_text(self, memory, text, offset=0):
        """Write a text string into display memory.

        Each character is converted to its ASCII code, then stored
        as a ternary string at the corresponding display address.

        Args:
            memory: Memory object with .store(addr, value) method.
            text (str): Text to display.
            offset (int): Starting position within the display buffer.
        """
        from trinary.conversion import decimal_to_ternary as d2t

        for i, ch in enumerate(text):
            addr = DISPLAY_START + offset + i
            if addr > DISPLAY_END:
                break
            code = d2t(ord(ch))
            memory.store(addr, code)

    def clear(self, memory):
        """Clear the display buffer (set all cells to space/"0")."""
        from trinary.conversion import decimal_to_ternary as d2t
        for addr in range(DISPLAY_START, DISPLAY_END + 1):
            memory.store(addr, "0")

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from trinary.display import DisplayMemoryMap, DISPLAY_START, DISPLAY_END, DISPLAY_SIZE


COLS = 8
ROWS = DISPLAY_SIZE // COLS


class ScreenView(QTextEdit):
    """Terminal-like display widget for memory-mapped video RAM.

    Reads display memory region (addresses 200-255) from the CPU's RAM
    and renders characters as a fixed-grid terminal.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont("Courier New", 16)
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        self.setFont(font)
        self.setReadOnly(True)
        self.setFixedHeight(180)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #00ff88;
                border: 1px solid #00ff88;
                font-family: "Courier New", monospace;
                font-size: 16px;
            }
        """)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._display = DisplayMemoryMap()

    def refresh(self, memory):
        """Refresh the screen from CPU memory.

        Args:
            memory: Memory object with .load(addr) method.
        """
        chars = self._display.read_display(memory)
        lines = []
        for r in range(ROWS):
            row_chars = chars[r * COLS:(r + 1) * COLS]
            lines.append("".join(row_chars))
        self.setPlainText("\n".join(lines))

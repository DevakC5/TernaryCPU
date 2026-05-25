from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, pyqtSignal

from trinary.display import PixelDisplay, Framebuffer, PALETTE


PIXEL_SIZE = 12
PALETTE_QT = {i: QColor(*rgb) for i, rgb in PALETTE.items()}


class ScreenView(QWidget):
    key_pressed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._display = PixelDisplay()
        w = PixelDisplay.WIDTH * PIXEL_SIZE
        h = PixelDisplay.HEIGHT * PIXEL_SIZE
        self.setFixedSize(w, h)
        self.setStyleSheet("background-color: #0a0a0a;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._px_size = PIXEL_SIZE

    def display(self):
        return self._display

    def clear(self):
        self._display.clear()
        self.update()

    def set_display_source(self, source):
        self._display = source
        w = source.width * self._px_size
        h = source.height * self._px_size
        self.setFixedSize(w, h)
        self.update()

    def refresh(self, memory=None):
        self.update()

    def keyPressEvent(self, event):
        text = event.text()
        if text and 32 <= ord(text) <= 126:
            self.key_pressed.emit(ord(text))
        super().keyPressEvent(event)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setPen(Qt.PenStyle.NoPen)
        buffer = self._display.get_buffer()
        height = len(buffer)
        width = len(buffer[0]) if height else 0
        for y in range(height):
            for x in range(width):
                val = buffer[y][x]
                if val < 0 or val > 8:
                    val = 0
                color = PALETTE_QT.get(val, PALETTE_QT[0])
                qp.setBrush(color)
                qp.drawRect(x * self._px_size, y * self._px_size, self._px_size, self._px_size)

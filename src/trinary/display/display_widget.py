from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from trinary.display.constants import DISPLAY_WIDTH, DISPLAY_HEIGHT
from trinary.display.palette import PALETTE

PIXEL_SCALE = 8
SCANLINE_ALPHA = 20


class DisplayWidget(QWidget):
    key_pressed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        w = DISPLAY_WIDTH * PIXEL_SCALE
        h = DISPLAY_HEIGHT * PIXEL_SCALE
        self.setFixedSize(w, h)
        self.setStyleSheet("background-color: #000;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._pixels = [[0] * DISPLAY_WIDTH for _ in range(DISPLAY_HEIGHT)]
        self._scanlines = True
        self._dark_aesthetic = True

        self._auto_refresh = QTimer(self)
        self._auto_refresh.setInterval(33)
        self._auto_refresh.timeout.connect(self.update)

        self._fps_counter = 0
        self._fps_timer = QTimer(self)
        self._fps_timer.setInterval(1000)
        self._fps_timer.timeout.connect(self._reset_fps)
        self._frame_count = 0

    def set_pixels(self, buffer):
        self._pixels = buffer
        self._frame_count += 1

    def start_auto_refresh(self):
        self._auto_refresh.start()
        self._fps_timer.start()

    def stop_auto_refresh(self):
        self._auto_refresh.stop()
        self._fps_timer.stop()

    def toggle_scanlines(self, enabled):
        self._scanlines = enabled

    def fps(self):
        return self._fps_counter

    def _reset_fps(self):
        self._fps_counter = self._frame_count
        self._frame_count = 0

    def keyPressEvent(self, event):
        text = event.text()
        if text and 32 <= ord(text) <= 126:
            self.key_pressed.emit(ord(text))
        super().keyPressEvent(event)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setPen(Qt.PenStyle.NoPen)
        qp.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

        scale = PIXEL_SCALE
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                val = self._pixels[y][x]
                if val < 0 or val > 8:
                    val = 0
                r, g, b = PALETTE.get(val, (0, 0, 0))
                qp.setBrush(QColor(r, g, b))
                qp.drawRect(x * scale, y * scale, scale, scale)
                if self._scanlines:
                    qp.setBrush(QColor(0, 0, 0, SCANLINE_ALPHA))
                    qp.drawRect(x * scale, y * scale, scale, 1)

        if self._dark_aesthetic:
            qp.setPen(QColor(30, 30, 30, 40))
            for x in range(0, DISPLAY_WIDTH * scale, scale):
                qp.drawLine(x, 0, x, DISPLAY_HEIGHT * scale)

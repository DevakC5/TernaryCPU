from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from trinary.conversion import decimal_to_ternary
from trinary.display.constants import KEYBOARD_ADDR
from trinary.ui.screen_view import ScreenView


class GameWindow(QMainWindow):
    def __init__(self, engine, update_fn, render_fn, target_fps=30, title="Trinary Game", pixel_size=None):
        super().__init__()
        self.engine = engine
        self._update_fn = update_fn
        self._render_fn = render_fn
        self._target_fps = target_fps
        self._frame_count = 0

        self.setWindowTitle(title)
        self.setStyleSheet("background-color: #111; color: #ccc;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.screen_view = ScreenView()
        if pixel_size is not None:
            self.screen_view._px_size = pixel_size
        self.screen_view.set_display_source(engine.fb)
        layout.addWidget(self.screen_view, alignment=Qt.AlignmentFlag.AlignCenter)

        self.fps_label = QLabel("")
        self.fps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fps_label.setStyleSheet("color: #555; font-size: 10px; padding: 2px;")
        layout.addWidget(self.fps_label)

        self._timer = QTimer(self)
        self._timer.setInterval(int(1000 / target_fps))
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        self._fps_timer = QTimer(self)
        self._fps_timer.setInterval(1000)
        self._fps_timer.timeout.connect(self._show_fps)
        self._fps_timer.start()

        self._fps_count = 0
        self.screen_view.key_pressed.connect(self._on_key)

        self.engine.init()
        self._resize_to_screen()

    def _resize_to_screen(self):
        w = self.screen_view.width()
        h = self.screen_view.height()
        self.resize(w + 20, h + 60)

    def _tick(self):
        if self._update_fn:
            self._update_fn()
        self.engine.update()
        if self._render_fn:
            self._render_fn()
        self.engine.render()
        self.screen_view.update()
        self._frame_count += 1
        self._fps_count += 1

    def _show_fps(self):
        self.fps_label.setText(f"{self._fps_count} FPS")
        self._fps_count = 0

    def _on_key(self, ascii_code):
        mem = self.engine.memory
        if mem:
            mem.store(KEYBOARD_ADDR, decimal_to_ternary(ascii_code))

    def closeEvent(self, event):
        self._timer.stop()
        self._fps_timer.stop()
        self.engine.shutdown()
        event.accept()

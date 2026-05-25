"""Waveform Viewer — GTKWave-style signal traces for hardware signals.

Displays digital signal waveforms for:
- clock, PC, SP, halt, interrupt, bus, DMA, cache, branch
Features zoom, scroll, and signal filtering.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QSlider
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush


SIGNAL_COLORS = {
    "clk": QColor("#00ff88"),
    "pc": QColor("#ffcc00"),
    "sp": QColor("#ff8844"),
    "halted": QColor("#ff4444"),
    "cache_hit": QColor("#00ff88"),
    "branch_taken": QColor("#8888ff"),
    "int": QColor("#ff4488"),
    "dma": QColor("#ff8844"),
    "bus": QColor("#44aaff"),
}

SIGNAL_GROUPS = {
    "Control": ["clk", "pc", "sp", "halted"],
    "Memory": ["cache_hit"],
    "Branch": ["branch_taken"],
    "System": ["int", "dma", "bus"],
}


class WaveformCanvas(QWidget):
    """The scrollable waveform canvas with signal traces."""

    COL_W = 20
    ROW_H = 28
    LABEL_W = 80

    def __init__(self, parent=None):
        super().__init__(parent)
        self._signals = {}
        self._max_cycles = 0
        self._zoom = 1.0
        self._offset = 0
        self.setMinimumHeight(200)

    def set_signals(self, signals, max_cycles):
        self._signals = signals
        self._max_cycles = max_cycles
        self.update()

    def set_zoom(self, factor):
        self._zoom = max(0.4, min(5.0, factor))
        self.update()

    def set_offset(self, offset):
        self._offset = max(0, offset)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        col_w = int(self.COL_W * self._zoom)

        p.fillRect(0, 0, w, self.height(), QColor("#0a0a1a"))

        # Grid lines
        p.setPen(QPen(QColor("#0f3460"), 1))
        for ci in range(0, self._max_cycles, 2):
            cx = self.LABEL_W + ci * col_w
            p.drawLine(cx, 0, cx, self.height())

        sig_names = list(self._signals.keys())
        for ri, name in enumerate(sig_names):
            y = ri * self.ROW_H
            values = self._signals.get(name, [])

            # Signal label
            p.setPen(TEXT_COLOR_W)
            p.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
            p.drawText(int(2), int(y), int(self.LABEL_W - 4), self.ROW_H,
                       int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), name)

            # Draw waveform trace
            start = self._offset
            cycles_to_show = (w - self.LABEL_W) // col_w + 1
            if not values:
                cycles_to_show = 0

            for ci in range(cycles_to_show + 1):
                cx = self.LABEL_W + ci * col_w
                idx = start + ci
                val = values[idx] if idx < len(values) else 0

                color = SIGNAL_COLORS.get(name, QColor("#00ff88"))
                mid_y = y + self.ROW_H // 2

                if name == "clk":
                    # Clock: draw as square wave
                    half_w = col_w // 2
                    if val:
                        p.setPen(QPen(color, 2))
                        p.drawLine(cx, mid_y - 6, cx + half_w, mid_y - 6)
                        p.drawLine(cx + half_w, mid_y - 6, cx + half_w, mid_y + 6)
                        p.drawLine(cx + half_w, mid_y + 6, cx + col_w, mid_y + 6)
                    else:
                        p.setPen(QPen(QColor("#333"), 1))
                        p.drawLine(cx, mid_y, cx + col_w, mid_y)
                else:
                    # Digital signal: high/low
                    if val:
                        p.setPen(QPen(color, 2))
                        p.drawLine(cx, mid_y - 4, cx + col_w, mid_y - 4)
                    else:
                        p.setPen(QPen(QColor("#333"), 1))
                        p.drawLine(cx, mid_y, cx + col_w, mid_y)

        self.setMinimumHeight(len(sig_names) * self.ROW_H + 10)
        p.end()


TEXT_COLOR_W = QColor("#e0e0e0")


class WaveformWidget(QWidget):
    """GTKWave-style signal viewer for hardware signals."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #0a0a1a; border: 1px solid #0f3460; border-radius: 4px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        header = QHBoxLayout()
        title = QLabel("Signal Waveform")
        title.setStyleSheet("color: #00ff88; font: 10px Courier New bold;")
        header.addWidget(title)
        header.addStretch()

        header.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(40, 500)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.valueChanged.connect(self._on_zoom)
        header.addWidget(self.zoom_slider)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: #0a0a1a; border: 1px solid #0f3460;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.canvas = WaveformCanvas()
        scroll.setWidget(self.canvas)
        layout.addWidget(scroll)

        self.setLayout(layout)

    def _on_zoom(self, val):
        self.canvas.set_zoom(val / 100.0)

    def update_waveform(self, signals, max_cycles):
        self.canvas.set_signals(signals, max_cycles)

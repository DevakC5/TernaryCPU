"""Execution Timeline — cycle-by-cycle waveform-style view.

Similar to logic analyzer / GTKWave displays.
One row per instruction, columns are clock cycles.
Features zoom, scroll, hover tooltips, stage colors.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QSlider, QToolTip,
)
from PyQt6.QtCore import Qt, QRectF, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath


STAGE_COLORS_QT = {
    "IF": QColor("#004488"),
    "ID": QColor("#006644"),
    "EX": QColor("#884400"),
    "MEM": QColor("#440088"),
    "WB": QColor("#008844"),
}
BUBBLE_COLOR_TL = QColor("#1a1a2e")
STALL_COLOR_TL = QColor("#882222")
GRID_COLOR = QColor("#0f3460")
TEXT_COLOR = QColor("#e0e0e0")
HOVER_GLOW = QColor("#00ff88")


class TimelineCanvas(QWidget):
    """The scrollable timeline canvas rendered with QPainter."""

    CELL_W = 24
    ROW_H = 22
    HEADER_H = 30

    def __init__(self, parent=None):
        super().__init__(parent)
        self._traces = []
        self._max_cycles = 0
        self._zoom = 1.0
        self._offset = 0
        self._hover_cycle = -1
        self._hover_row = -1
        self.setMinimumHeight(200)
        self.setMouseTracking(True)

    def set_traces(self, traces, max_cycles):
        self._traces = list(traces)
        self._max_cycles = max_cycles
        self.update()

    def set_zoom(self, factor):
        self._zoom = max(0.4, min(5.0, factor))
        self.update()

    def set_offset(self, offset):
        self._offset = max(0, offset)
        self.update()

    def _cell_at_pos(self, pos):
        cell_w = int(self.CELL_W * self._zoom)
        if pos.x() < 80:
            return -1, -1
        cycle = self._offset + (pos.x() - 80) // cell_w
        row = (pos.y() - self.HEADER_H) // self.ROW_H
        return cycle, row

    def mouseMoveEvent(self, event):
        cycle, row = self._cell_at_pos(event.pos())
        if cycle != self._hover_cycle or row != self._hover_row:
            self._hover_cycle = cycle
            self._hover_row = row
            self.update()
            if 0 <= row < len(self._traces) and cycle >= 0:
                trace = self._traces[row]
                stages = trace.get("stages", [])
                stage = stages[cycle] if cycle < len(stages) else "---"
                name = trace.get("name", f"I{row}")
                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    f"{name} @ cycle {cycle}: {stage}",
                    self,
                )
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._hover_cycle = -1
        self._hover_row = -1
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        cell_w = int(self.CELL_W * self._zoom)

        p.fillRect(0, 0, w, h, QColor("#0a0a1a"))

        cycles_to_show = min(self._max_cycles, w // cell_w + 2)
        start_cycle = self._offset

        p.setPen(QPen(TEXT_COLOR, 1))
        p.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        for ci in range(cycles_to_show + 1):
            cx = 80 + ci * cell_w
            p.drawText(int(cx), 2, int(cell_w), self.HEADER_H - 4,
                       int(Qt.AlignmentFlag.AlignCenter),
                       str(start_cycle + ci))

        p.setPen(QPen(GRID_COLOR, 1))
        for ci in range(cycles_to_show + 1):
            cx = 80 + ci * cell_w
            p.drawLine(cx, self.HEADER_H, cx, h)

        for ri, trace in enumerate(self._traces):
            y = self.HEADER_H + ri * self.ROW_H
            p.setPen(TEXT_COLOR)
            p.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
            p.drawText(int(4), int(y), 74, self.ROW_H,
                       int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                       trace.get("name", f"I{ri}"))

            stages = trace.get("stages", [])
            for ci in range(start_cycle, start_cycle + cycles_to_show):
                if ci < len(stages):
                    stage = stages[ci]
                else:
                    stage = "---"
                cx = 80 + (ci - start_cycle) * cell_w
                color = STAGE_COLORS_QT.get(stage, BUBBLE_COLOR_TL)
                if stage == "STALL":
                    color = STALL_COLOR_TL

                is_hover = (ci == self._hover_cycle and ri == self._hover_row)
                if is_hover:
                    p.setPen(QPen(HOVER_GLOW, 2))
                else:
                    p.setPen(QPen(QColor("#333"), 1))

                p.fillRect(int(cx), int(y), int(cell_w), self.ROW_H, color)
                p.drawRect(int(cx), int(y), int(cell_w), self.ROW_H)

                if ci < len(stages) and stage not in ("---", "STALL"):
                    p.setPen(QColor("#ffffff"))
                    p.setFont(QFont("Courier New", 6))
                    p.drawText(int(cx + 1), int(y + 2), int(cell_w - 2), self.ROW_H - 4,
                               int(Qt.AlignmentFlag.AlignCenter), stage)

        self.setMinimumHeight(self.HEADER_H + len(self._traces) * self.ROW_H + 10)
        p.end()


class ExecutionTimelineWidget(QWidget):
    """Cycle-by-cycle execution timeline with zoom and scroll."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #0a0a1a; border: 1px solid #0f3460; border-radius: 4px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        header = QHBoxLayout()
        title = QLabel("Execution Timeline")
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

        self.cycle_label = QLabel("")
        self.cycle_label.setStyleSheet("color: #888; font: 9px Courier New;")
        header.addWidget(self.cycle_label)

        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: #0a0a1a; border: 1px solid #0f3460;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.canvas = TimelineCanvas()
        scroll.setWidget(self.canvas)
        layout.addWidget(scroll)

        self.setLayout(layout)

    def _on_zoom(self, val):
        self.canvas.set_zoom(val / 100.0)

    def update_timeline(self, execution_history, current_cycle):
        if not execution_history:
            return
        max_cycles = max(current_cycle, 20)
        self.canvas.set_traces(execution_history, max_cycles)
        self.cycle_label.setText(f"Cycles: {current_cycle}")

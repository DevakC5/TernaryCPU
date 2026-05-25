"""Bus Monitor — animated data flow and bandwidth display."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush


BG_DARK = QColor("#0a0a1a")
TEXT_COLOR_BM = QColor("#e0e0e0")
BUS_ACTIVE = QColor("#004488")
BUS_IDLE = QColor("#1a1a2e")
CPU_COLOR = QColor("#00ff88")
DMA_COLOR = QColor("#ff8844")
ACCEL_COLOR = QColor("#8888ff")


class BusMonitorWidget(QWidget):
    """Real-time bus monitor showing transfers, contention, and bandwidth."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        stats = QHBoxLayout()
        self.transfer_label = QLabel("Transfers: 0")
        self.pending_label = QLabel("Pending: 0")
        self.util_label = QLabel("Util: 0%")
        for lbl in (self.transfer_label, self.pending_label, self.util_label):
            lbl.setStyleSheet("color: #00ff88; font: 9px Courier New;")
            stats.addWidget(lbl)
        stats.addStretch()
        layout.addLayout(stats)

        bw_row = QHBoxLayout()
        bw_row.addWidget(QLabel("Bandwidth:"))
        self.bw_bar = QProgressBar()
        self.bw_bar.setRange(0, 100)
        self.bw_bar.setValue(0)
        self.bw_bar.setFixedHeight(16)
        self.bw_bar.setStyleSheet(
            "QProgressBar { background: #1a1a2e; border: 1px solid #0f3460; text-align: center; color: #e0e0e0; font: 8px Courier New; }"
            "QProgressBar::chunk { background: #004488; }"
        )
        bw_row.addWidget(self.bw_bar, 1)
        layout.addLayout(bw_row)

        self.diagram = BusDiagram()
        layout.addWidget(self.diagram, 1)

        self.setLayout(layout)

    def update_bus(self, snap):
        self.transfer_label.setText(f"Transfers: {snap.transfers}")
        self.pending_label.setText(f"Pending: {snap.pending}")
        util_pct = int(snap.utilization * 100)
        self.util_label.setText(f"Util: {util_pct}%")
        self.bw_bar.setValue(util_pct)
        self.diagram.update_bus(snap)


class BusDiagram(QWidget):
    """Animated bus topology diagram showing sources."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._transfers = 0
        self._utilization = 0.0
        self.setMinimumHeight(60)

    def update_bus(self, snap):
        self._transfers = snap.transfers
        self._utilization = snap.utilization
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, BG_DARK)

        cx, cy = w // 2, h // 2

        p.setPen(QPen(QColor("#0f3460"), 2))
        p.setBrush(QBrush(BUS_ACTIVE if self._utilization > 0 else BUS_IDLE))
        p.drawRect(cx - 30, cy - 12, 60, 24)
        p.setPen(TEXT_COLOR_BM)
        p.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        p.drawText(int(cx - 30), int(cy - 12), 60, 24,
                   int(Qt.AlignmentFlag.AlignCenter), "BUS")

        sources = [
            ("CPU", CPU_COLOR, cx - 100, cy - 40),
            ("DMA", DMA_COLOR, cx + 60, cy - 40),
            ("VRAM", QColor("#88ff88"), cx - 100, cy + 20),
            ("ACCEL", ACCEL_COLOR, cx + 60, cy + 20),
        ]

        for name, color, sx, sy in sources:
            p.setPen(QPen(color, 1))
            p.setBrush(QBrush(color.darker(200)))
            p.drawRoundedRect(int(sx), int(sy), 36, 20, 4, 4)
            p.setPen(TEXT_COLOR_BM)
            p.setFont(QFont("Courier New", 7))
            p.drawText(int(sx), int(sy), 36, 20,
                       int(Qt.AlignmentFlag.AlignCenter), name)
            p.setPen(QPen(color, 1, Qt.PenStyle.DashLine))
            p.drawLine(int(sx + 36), int(sy + 10), int(cx - 30), int(cy))

        p.end()

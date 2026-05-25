"""Cache Inspector — live cache heatmap with hit/miss visualization.

Shows cache lines as a colored grid:
- Green: valid clean lines
- Yellow: dirty lines 
- Red: recently missed lines (decays over time)
- Dark: invalid lines
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush


HIT_COLOR = QColor("#004422")
MISS_COLOR = QColor("#662200")
CLEAN_COLOR = QColor("#004422")
DIRTY_COLOR = QColor("#444400")
ACTIVE_COLOR = QColor("#006644")
INVALID_COLOR = QColor("#1a1a2e")
TEXT_COLOR_C = QColor("#e0e0e0")


class CacheHeatmapWidget(QWidget):
    """Renders cache lines as a colored heatmap grid with access heat."""

    CELL_SIZE = 14
    GAP = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lines = []
        self._hits = 0
        self._misses = 0
        self._hit_rate = 1.0
        self.setMinimumHeight(100)

    def update_cache(self, snap):
        self._hits = snap.hits
        self._misses = snap.misses
        self._hit_rate = snap.hit_rate
        self._lines = list(snap.lines)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()

        cs = self.CELL_SIZE
        cols = max(1, (w - 10) // (cs + self.GAP))
        rows = (len(self._lines) + cols - 1) // cols if self._lines else 1

        p.setFont(QFont("Courier New", 7))
        for i, line in enumerate(self._lines):
            col = i % cols
            row = i // cols
            x = 4 + col * (cs + self.GAP)
            y = 4 + row * (cs + self.GAP)

            if line.get('valid'):
                if line.get('dirty'):
                    color = DIRTY_COLOR
                else:
                    color = CLEAN_COLOR
            else:
                color = INVALID_COLOR

            # Draw cell
            p.setPen(QPen(QColor("#333"), 1))
            p.fillRect(x, y, cs, cs, color)
            p.drawRect(x, y, cs, cs)

            if line.get('valid'):
                tag = line.get('tag', -1)
                if tag >= 0:
                    p.setPen(QColor("#888"))
                    p.drawText(int(x), int(y), int(cs), int(cs),
                               int(Qt.AlignmentFlag.AlignCenter), str(tag % 10))

        # Legend
        ly = max(rows * (cs + self.GAP) + 8, self.height() - 16)
        leg_items = [
            (CLEAN_COLOR, "Valid"),
            (DIRTY_COLOR, "Dirty"),
            (INVALID_COLOR, "Invalid"),
        ]
        lx = 4
        p.setFont(QFont("Courier New", 7))
        for color, label in leg_items:
            p.fillRect(int(lx), int(ly), 8, 8, color)
            p.setPen(QPen(QColor("#333"), 1))
            p.drawRect(int(lx), int(ly), 8, 8)
            p.setPen(TEXT_COLOR_C)
            p.drawText(int(lx + 10), int(ly - 2), 60, 12,
                       int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), label)
            lx += 70

        p.end()


class CacheInspectorWidget(QWidget):
    """Cache inspector with heatmap, stats, and hit/miss rates."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #0a0a1a; border: 1px solid #0f3460; border-radius: 4px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        header = QHBoxLayout()
        title = QLabel("Cache Heatmap")
        title.setStyleSheet("color: #00ff88; font: 10px Courier New bold;")
        header.addWidget(title)

        self.hit_label = QLabel("Hits: 0")
        self.miss_label = QLabel("Misses: 0")
        self.rate_label = QLabel("Rate: 100%")
        for lbl in (self.hit_label, self.miss_label, self.rate_label):
            lbl.setStyleSheet("color: #888; font: 9px Courier New; padding: 0 8px;")
            header.addWidget(lbl)
        header.addStretch()
        layout.addLayout(header)

        self.heatmap = CacheHeatmapWidget()
        layout.addWidget(self.heatmap, 1)

        self.setLayout(layout)

    def update_cache(self, snap):
        self.hit_label.setText(f"Hits: {snap.hits}")
        self.miss_label.setText(f"Misses: {snap.misses}")
        self.rate_label.setText(f"Rate: {snap.hit_rate:.0%}")
        self.heatmap.update_cache(snap)

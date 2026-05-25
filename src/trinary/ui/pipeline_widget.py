"""Pipeline Visualizer — live animated 5-stage pipeline viewer."""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush


STAGE_COLORS = {
    "IF": QColor("#004488"),
    "ID": QColor("#006644"),
    "EX": QColor("#884400"),
    "MEM": QColor("#440088"),
    "WB": QColor("#008844"),
}
STAGE_ORDER = ["IF", "ID", "EX", "MEM", "WB"]
BUBBLE_COLOR = QColor("#1a1a2e")
STALL_COLOR = QColor("#882222")
FLUSH_COLOR = QColor("#cc4400")
TEXT_COLOR = QColor("#e0e0e0")
ARROW_COLOR = QColor("#0f3460")
FORWARD_COLOR = QColor("#00ff88")
HAZARD_COLOR = QColor("#ff4488")


class PipelineStageWidget(QWidget):
    """Single pipeline stage box with painted content."""

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.label = ""
        self.bubble = True
        self.stalled = False
        self.flushing = False
        self.hazard = ""
        self.setMinimumSize(110, 64)
        self.setMaximumHeight(72)

    def update_state(self, label="", bubble=True, stalled=False, flushing=False, hazard=""):
        self.label = label
        self.bubble = bubble
        self.stalled = stalled
        self.flushing = flushing
        self.hazard = hazard
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        color = STAGE_COLORS.get(self.name, QColor("#333"))
        if self.flushing:
            color = FLUSH_COLOR
        elif self.stalled:
            color = STALL_COLOR
        elif self.bubble:
            color = BUBBLE_COLOR

        p.setPen(QPen(QColor("#0f3460"), 2))
        p.setBrush(QBrush(color))
        p.drawRoundedRect(2, 2, w - 4, h - 4, 8, 8)

        name_color = QColor("#00ff88") if not self.bubble else QColor("#555")
        p.setPen(name_color)
        name_font = QFont("Courier New", 10, QFont.Weight.Bold)
        p.setFont(name_font)
        p.drawText(int(4), int(4), int(w - 8), 20,
                   int(Qt.AlignmentFlag.AlignCenter), self.name)

        if not self.bubble:
            p.setPen(TEXT_COLOR)
            label_font = QFont("Courier New", 8)
            p.setFont(label_font)
            clip = self.label if len(self.label) < 20 else self.label[:17] + "..."
            p.drawText(int(4), 22, int(w - 8), h - 30,
                       int(Qt.AlignmentFlag.AlignCenter), clip)

        if self.stalled:
            p.setPen(QColor("#ff6666"))
            p.setFont(QFont("Courier New", 7, QFont.Weight.Bold))
            p.drawText(int(4), h - 18, int(w - 8), 14,
                       int(Qt.AlignmentFlag.AlignCenter), "STALL")

        if self.flushing:
            p.setPen(QColor("#ffcc00"))
            p.setFont(QFont("Courier New", 7, QFont.Weight.Bold))
            p.drawText(int(4), h - 18, int(w - 8), 14,
                       int(Qt.AlignmentFlag.AlignCenter), "FLUSH")

        if self.hazard:
            p.setPen(HAZARD_COLOR)
            p.setFont(QFont("Courier New", 6, QFont.Weight.Bold))
            p.drawText(int(4), 42, int(w - 8), 10,
                       int(Qt.AlignmentFlag.AlignCenter), self.hazard)

        p.end()


class ArrowWidget(QWidget):
    """Arrow between pipeline stages with optional forwarding highlight."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(20)
        self.setMaximumWidth(20)
        self._forwarding = False

    def set_forwarding(self, active):
        self._forwarding = active
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = FORWARD_COLOR if self._forwarding else ARROW_COLOR
        p.setPen(QPen(color, 2))
        h = self.height() // 2
        w = self.width()
        p.drawLine(0, h, w - 8, h)
        p.drawLine(w - 8, h - 5, w, h)
        p.drawLine(w - 8, h + 5, w, h)
        p.end()


class PipelineVisualizer(QWidget):
    """Horizontal 5-stage pipeline diagram with live updates."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.setStyleSheet("background: #0a0a1a; border: 1px solid #0f3460; border-radius: 4px;")

        outer = QVBoxLayout()
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(2)

        header = QHBoxLayout()
        title = QLabel("Pipeline  IF \u2192 ID \u2192 EX \u2192 MEM \u2192 WB")
        title.setStyleSheet("color: #00ff88; font: 10px Courier New bold; padding: 2px 0;")
        header.addWidget(title)
        header.addStretch()
        self.info_label = QLabel("idle")
        self.info_label.setStyleSheet("color: #888; font: 9px Courier New;")
        header.addWidget(self.info_label)
        outer.addLayout(header)

        stage_row = QHBoxLayout()
        stage_row.setContentsMargins(4, 0, 4, 0)
        stage_row.setSpacing(0)

        self.stages = {}
        self.arrows = []
        for i, name in enumerate(STAGE_ORDER):
            if i > 0:
                arrow = ArrowWidget()
                self.arrows.append(arrow)
                stage_row.addWidget(arrow)
            sw = PipelineStageWidget(name)
            self.stages[name] = sw
            stage_row.addWidget(sw)

        outer.addLayout(stage_row)
        outer.addStretch()
        self.setLayout(outer)

    def update_pipeline(self, snap):
        for name in STAGE_ORDER:
            s = self.stages[name]
            nl = name.lower()
            label = getattr(snap, f"{nl}_stage", "---")
            bubble = getattr(snap, f"{nl}_bubble", True)
            stalled = getattr(snap, f"{nl}_stalled", False)
            s.update_state(label, bubble=bubble, stalled=stalled)

        self.info_label.setText(
            f"retired:{snap.total_instructions} "
            f"stalls:{snap.stall_cycles} "
            f"flushes:{snap.flush_count}"
        )

    def set_forwarding(self, stage_pairs):
        for arrow in self.arrows:
            arrow.set_forwarding(False)
        for pair in stage_pairs:
            idx = STAGE_ORDER.index(pair[1]) - 1
            if 0 <= idx < len(self.arrows):
                self.arrows[idx].set_forwarding(True)

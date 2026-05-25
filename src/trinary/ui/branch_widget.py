"""Branch Predictor Visualizer — state machines, accuracy, history."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush


PREDICT_TAKEN_COLOR = QColor("#004422")
PREDICT_NOT_TAKEN_COLOR = QColor("#442200")
MISPREDICT_COLOR = QColor("#882222")
ACCURACY_HIGH = QColor("#00ff88")
ACCURACY_LOW = QColor("#ff4444")
TEXT_COLOR_B = QColor("#e0e0e0")


class BranchPredictorWidget(QWidget):
    """Visualize branch predictor state, accuracy, and history."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #0a0a1a; border: 1px solid #0f3460; border-radius: 4px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        header = QHBoxLayout()
        title = QLabel("Branch Predictor")
        title.setStyleSheet("color: #00ff88; font: 10px Courier New bold;")
        header.addWidget(title)

        self.mode_label = QLabel("Mode: two_bit")
        self.pred_label = QLabel("Predictions: 0")
        self.mispred_label = QLabel("Mispredicts: 0")
        self.acc_label = QLabel("Accuracy: 100%")
        for lbl in (self.mode_label, self.pred_label, self.mispred_label, self.acc_label):
            lbl.setStyleSheet("color: #888; font: 9px Courier New; padding: 0 6px;")
            header.addWidget(lbl)
        header.addStretch()
        layout.addLayout(header)

        self.state_display = QLabel(
            "2-bit Saturating Counter:  [00] Strong NT → [01] Weak NT → [10] Weak T → [11] Strong T"
        )
        self.state_display.setStyleSheet("color: #555; font: 8px Courier New; padding: 2px 4px;")
        layout.addWidget(self.state_display)

        self.canvas = BranchAccuracyCanvas()
        layout.addWidget(self.canvas, 1)

        self.setLayout(layout)

    def update_branch(self, snap):
        self.mode_label.setText(f"Mode: {snap.mode}")
        self.pred_label.setText(f"Predictions: {snap.predictions}")
        self.mispred_label.setText(f"Mispredicts: {snap.mispredictions}")
        acc_pct = snap.accuracy * 100
        acc_str = f"Accuracy: {acc_pct:.1f}%"
        self.acc_label.setText(acc_str)
        color = ACCURACY_HIGH if acc_pct >= 80 else ACCURACY_LOW
        self.acc_label.setStyleSheet(f"color: {color.name()}; font: 9px Courier New; padding: 0 6px;")
        self.canvas.update_accuracy(snap.accuracy)


class BranchAccuracyCanvas(QWidget):
    """Accuracy bar with color coding and percentage text."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._accuracy = 1.0
        self.setMinimumHeight(30)

    def update_accuracy(self, acc):
        self._accuracy = acc
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, QColor("#0a0a1a"))

        bar_w = int(w * self._accuracy)
        color = ACCURACY_HIGH if self._accuracy >= 0.8 else ACCURACY_LOW
        p.fillRect(2, 6, bar_w - 4, h - 12, color)

        p.setPen(QPen(QColor("#0f3460"), 1))
        p.drawRect(2, 6, w - 4, h - 12)

        p.setPen(TEXT_COLOR_B)
        p.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        p.drawText(int(2), 6, int(w - 4), h - 12,
                   int(Qt.AlignmentFlag.AlignCenter), f"{self._accuracy:.0%}")
        p.end()

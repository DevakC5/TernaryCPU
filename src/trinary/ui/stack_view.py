from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt


class StackView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.indicator = QLabel("SP → 255  (empty)")
        self.indicator.setProperty("cssClass", "value")
        self.indicator.setStyleSheet("color: #00ff88; font-weight: bold; font-size: 11px;")
        layout.addWidget(self.indicator)

        self._list = QListWidget()
        self._list.setMaximumHeight(120)
        layout.addWidget(self._list)
        self.setLayout(layout)

    def update_view(self, memory, sp, stack_base=255, stack_min=128):
        self._list.clear()
        if sp < stack_base:
            self.indicator.setText(f"SP → {sp}  ▼  {stack_base - sp} items")
        else:
            self.indicator.setText(f"SP → {sp}  (empty)")
        for addr in range(sp + 1, stack_base + 1):
            val = memory.load(addr)
            item = QListWidgetItem(f"[{addr:03d}] {val}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            if addr == sp + 1:
                f = item.font()
                f.setBold(True)
                item.setFont(f)
            self._list.addItem(item)
        if sp >= stack_base:
            self._list.addItem("(no data pushed)")

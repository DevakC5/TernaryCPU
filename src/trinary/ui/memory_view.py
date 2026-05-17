from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


WRITE_COLOR = QColor("#004422")
READ_COLOR = QColor("#002244")


class MemoryView(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Address", "Value"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._populated = False
        self._written = set()
        self._read = set()

    def populate(self, size=256):
        self.setRowCount(size)
        for addr in range(size):
            addr_item = QTableWidgetItem(f"{addr:03d}")
            addr_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(addr, 0, addr_item)
            val_item = QTableWidgetItem("0")
            val_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(addr, 1, val_item)
        self._populated = True

    def mark_write(self, addr):
        self._written.add(addr)

    def mark_read(self, addr):
        self._read.add(addr)

    def update_view(self, memory, highlight_addr=None):
        if not self._populated:
            self.populate()
        for addr in range(self.rowCount()):
            val = memory.load(addr)
            item = self.item(addr, 1)
            if item is None:
                continue
            item.setText(val)
            if addr in self._written:
                item.setBackground(WRITE_COLOR)
            elif addr in self._read:
                item.setBackground(READ_COLOR)
            elif addr == highlight_addr:
                item.setBackground(QColor("#003322"))
            else:
                item.setBackground(QColor("transparent"))

    def clear_marks(self):
        self._written.clear()
        self._read.clear()

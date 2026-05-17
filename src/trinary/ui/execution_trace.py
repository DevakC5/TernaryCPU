from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


HIGHLIGHT_BG = QColor("#003322")


class ExecutionTrace(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["#", "PC", "Instruction", "Registers", "Flags"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def clear_trace(self):
        self.setRowCount(0)

    def add_entry(self, step_num, pc, instruction, registers, flags):
        row = self.rowCount()
        self.insertRow(row)
        self.setItem(row, 0, QTableWidgetItem(str(step_num)))
        self.setItem(row, 1, QTableWidgetItem(str(pc)))
        self.setItem(row, 2, QTableWidgetItem(instruction))

        reg_str = " ".join(f"{k}={v}" for k, v in registers.items())
        self.setItem(row, 3, QTableWidgetItem(reg_str))

        active = [k for k, v in flags.items() if v]
        self.setItem(row, 4, QTableWidgetItem(" ".join(active) if active else ""))

        for col in range(5):
            self.item(row, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        for col in range(5):
            for r in range(self.rowCount() - 1):
                self.item(r, col).setBackground(QColor("transparent"))
        for col in range(5):
            self.item(row, col).setBackground(HIGHLIGHT_BG)

        self.scrollToBottom()

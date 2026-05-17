from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

TRANSPARENT = QColor("transparent")
HIGHLIGHT_BG = QColor("#003322")


class MachineCodeView(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Addr", "Assembly", "Machine Code"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def update_view(self, program, machine_code_list, highlight_addr=None):
        self.setRowCount(0)
        count = max(len(program), len(machine_code_list))
        if count == 0:
            return
        self.setRowCount(count)
        for i in range(count):
            addr_item = QTableWidgetItem(str(i))
            addr_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(i, 0, addr_item)

            asm = program[i] if i < len(program) else ""
            self.setItem(i, 1, QTableWidgetItem(asm))

            mc = machine_code_list[i] if i < len(machine_code_list) else ""
            mc_item = QTableWidgetItem(mc)
            mc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(i, 2, mc_item)

            bg = HIGHLIGHT_BG if i == highlight_addr else TRANSPARENT
            for col in range(3):
                self.item(i, col).setBackground(bg)

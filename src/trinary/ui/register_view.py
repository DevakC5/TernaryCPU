from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QColor


FLASH_COLOR = "#00ffcc"


class RegisterView(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Registers", parent)
        self._prev_regs = {}
        layout = QVBoxLayout()

        reg_layout = QHBoxLayout()
        self.reg_labels = {}
        for reg in ("R0", "R1", "R2", "R3"):
            lbl = QLabel("0")
            lbl.setProperty("cssClass", "value")
            lbl.setMinimumWidth(60)
            self.reg_labels[reg] = lbl
            reg_layout.addWidget(QLabel(f"{reg}:"))
            reg_layout.addWidget(lbl)
        reg_layout.addStretch()
        layout.addLayout(reg_layout)

        pc_layout = QHBoxLayout()
        self.pc_label = QLabel("0")
        self.pc_label.setProperty("cssClass", "value")
        pc_layout.addWidget(QLabel("PC:"))
        pc_layout.addWidget(self.pc_label)
        pc_layout.addStretch()
        layout.addLayout(pc_layout)

        sp_layout = QHBoxLayout()
        self.sp_label = QLabel("255")
        self.sp_label.setProperty("cssClass", "value")
        sp_layout.addWidget(QLabel("SP:"))
        sp_layout.addWidget(self.sp_label)
        sp_layout.addStretch()
        layout.addLayout(sp_layout)

        flag_layout = QHBoxLayout()
        self.flag_labels = {}
        for flag in ("ZERO", "EQUAL", "GREATER", "LESS"):
            lbl = QLabel(f"{flag[0]}")
            lbl.setProperty("cssClass", "flag_inactive")
            lbl.setToolTip(flag)
            self.flag_labels[flag] = lbl
            flag_layout.addWidget(lbl)
        flag_layout.addStretch()
        layout.addLayout(flag_layout)

        self.setLayout(layout)

    def update_view(self, registers, pc, sp, flags):
        for name, val in registers.items():
            lbl = self.reg_labels[name]
            lbl.setText(val)
            changed = self._prev_regs.get(name) is not None and self._prev_regs[name] != val
            if changed:
                lbl.setStyleSheet(f"color: {FLASH_COLOR}; font-weight: bold;")
            else:
                lbl.setStyleSheet("")
        self._prev_regs = dict(registers)
        self.pc_label.setText(str(pc))
        self.sp_label.setText(str(sp))
        for name, active in flags.items():
            lbl = self.flag_labels[name]
            lbl.setProperty("cssClass", "flag_active" if active else "flag_inactive")
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

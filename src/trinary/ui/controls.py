from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QComboBox, QLabel

from trinary.ui.demos import DEMOS


class Controls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        layout.addWidget(QLabel("Demo:"))
        self.demo_selector = QComboBox()
        for name in DEMOS:
            self.demo_selector.addItem(name)
        self.demo_selector.setCurrentIndex(0)
        layout.addWidget(self.demo_selector)

        layout.addSpacing(12)

        self.assemble_btn = QPushButton("Assemble")
        self.assemble_btn.setProperty("cssClass", "assemble")

        self.run_btn = QPushButton("Run")
        self.run_btn.setProperty("cssClass", "run")

        self.step_btn = QPushButton("Step Into")
        self.step_btn.setProperty("cssClass", "step")

        self.step_over_btn = QPushButton("Step Over")
        self.step_over_btn.setProperty("cssClass", "step")

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setProperty("cssClass", "reset")

        layout.addWidget(self.assemble_btn)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.step_btn)
        layout.addWidget(self.step_over_btn)
        layout.addWidget(self.reset_btn)

        layout.addSpacing(8)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setProperty("cssClass", "reset")

        self.continue_btn = QPushButton("Continue")
        self.continue_btn.setProperty("cssClass", "run")

        layout.addWidget(self.pause_btn)
        layout.addWidget(self.continue_btn)

        layout.addSpacing(12)

        self.boot_os_btn = QPushButton("Boot TernaryOS")
        self.boot_os_btn.setProperty("cssClass", "run")
        layout.addWidget(self.boot_os_btn)

        layout.addSpacing(12)

        self.cycle_label = QLabel("Cycles: 0")
        self.cycle_label.setProperty("cssClass", "value")
        layout.addWidget(self.cycle_label)

        layout.addStretch()

        self.setLayout(layout)

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

        self.step_btn = QPushButton("Step")
        self.step_btn.setProperty("cssClass", "step")

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setProperty("cssClass", "reset")

        layout.addWidget(self.assemble_btn)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.step_btn)
        layout.addWidget(self.reset_btn)
        layout.addStretch()

        self.setLayout(layout)

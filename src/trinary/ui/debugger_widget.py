"""Interactive Debugger — cycle stepping, breakpoints, watchpoints."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QCheckBox, QGroupBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal


class DebuggerController(QWidget):
    """Advanced debugger controls for cycle/instruction stepping.

    Signals:
        step_cycle: Request single-cycle step.
        step_instruction: Request single-instruction step.
        run_continue: Request continuous execution.
        pause: Request pause.
        reset: Request CPU reset.
    """

    step_cycle = pyqtSignal()
    step_instruction = pyqtSignal()
    run_continue = pyqtSignal()
    pause = pyqtSignal()
    reset = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        self.step_cycle_btn = QPushButton("Step Cycle")
        self.step_instr_btn = QPushButton("Step Instr")
        self.continue_btn = QPushButton("▶ Continue")
        self.pause_btn = QPushButton("⏸ Pause")
        self.reset_btn = QPushButton("⟲ Reset")

        for btn, css, sig in [
            (self.step_cycle_btn, "step", self.step_cycle),
            (self.step_instr_btn, "step", self.step_instruction),
            (self.continue_btn, "run", self.run_continue),
            (self.pause_btn, "reset", self.pause),
            (self.reset_btn, "reset", self.reset),
        ]:
            btn.setStyleSheet(f"background: #0f3460; color: #e0e0e0; "
                              f"border: 1px solid #1a1a2e; border-radius: 4px; "
                              f"padding: 4px 10px; font: 9px Courier New bold; min-width: 60px;")
            btn.clicked.connect(sig.emit)
            btn_row.addWidget(btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        self.speed_slider.setFixedWidth(120)
        speed_row.addWidget(self.speed_slider)
        self.speed_label = QLabel("50%")
        self.speed_label.setStyleSheet("color: #888; font: 8px Courier New;")
        speed_row.addWidget(self.speed_label)
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(f"{v}%"))
        speed_row.addStretch()
        layout.addLayout(speed_row)

        opts_row = QHBoxLayout()
        self.breakpoint_cb = QCheckBox("Breakpoints")
        self.watch_cb = QCheckBox("Watchpoints")
        self.trace_cb = QCheckBox("Trace")
        self.trace_cb.setChecked(True)
        for cb in (self.breakpoint_cb, self.watch_cb, self.trace_cb):
            cb.setStyleSheet("color: #888; font: 8px Courier New;")
            opts_row.addWidget(cb)
        opts_row.addStretch()
        layout.addLayout(opts_row)

        self.setLayout(layout)

    @property
    def speed_multiplier(self):
        return self.speed_slider.value() / 50.0

    @property
    def tracing_enabled(self):
        return self.trace_cb.isChecked()

    @property
    def breakpoints_enabled(self):
        return self.breakpoint_cb.isChecked()

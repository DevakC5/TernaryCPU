"""Hardware Inspector — collapsible panels for all hardware state."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QGridLayout, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt


STYLE_GROUP = """
QGroupBox {
    color: #00ff88;
    border: 1px solid #0f3460;
    border-radius: 4px;
    margin-top: 8px;
    font: 9px Courier New bold;
    padding-top: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
"""
STYLE_VALUE = "color: #00ff88; font: 9px Courier New;"
STYLE_LABEL = "color: #888; font: 9px Courier New;"


class InfoRow(QWidget):
    """A key: value row for the inspector."""

    def __init__(self, key, value="---", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 1, 4, 1)
        self.key_label = QLabel(key)
        self.key_label.setStyleSheet(STYLE_LABEL)
        self.key_label.setFixedWidth(120)
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(STYLE_VALUE)
        layout.addWidget(self.key_label)
        layout.addWidget(self.value_label, 1)
        self.setLayout(layout)

    def update_value(self, value):
        self.value_label.setText(str(value))


class InspectorSection(QGroupBox):
    """A collapsible inspector section."""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(STYLE_GROUP)
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(6, 4, 6, 4)
        self._layout.setSpacing(1)
        self.setLayout(self._layout)
        self._rows = {}

    def add_row(self, key, value="---"):
        row = InfoRow(key, value)
        self._layout.addWidget(row)
        self._rows[key] = row
        return row

    def update_row(self, key, value):
        if key in self._rows:
            self._rows[key].update_value(value)

    def clear_rows(self):
        self._rows.clear()
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class HardwareInspectorWidget(QWidget):
    """Complete hardware inspector with all state panels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        self._inner = QVBoxLayout(container)
        self._inner.setSpacing(2)

        self.reg_section = InspectorSection("Registers")
        for reg in ["R0", "R1", "R2", "R3", "PC", "SP"]:
            self.reg_section.add_row(reg, "0")
        self.flags_section = InspectorSection("Flags")
        for flag in ["ZERO", "EQUAL", "GREATER", "LESS"]:
            self.flags_section.add_row(flag, "False")

        self.pipeline_section = InspectorSection("Pipeline")
        for s in ["IF", "ID", "EX", "MEM", "WB"]:
            self.pipeline_section.add_row(s, "---")
        self.pipeline_section.add_row("Stalls", "0")
        self.pipeline_section.add_row("Flushes", "0")

        self.cache_section = InspectorSection("Cache")
        self.cache_section.add_row("Hits", "0")
        self.cache_section.add_row("Misses", "0")
        self.cache_section.add_row("Hit Rate", "100%")

        self.branch_section = InspectorSection("Branch Predictor")
        self.branch_section.add_row("Mode", "two_bit")
        self.branch_section.add_row("Accuracy", "100%")
        self.branch_section.add_row("Predictions", "0")
        self.branch_section.add_row("Mispredicts", "0")

        self.bus_section = InspectorSection("Bus")
        self.bus_section.add_row("Transfers", "0")
        self.bus_section.add_row("Utilization", "0%")

        self.dma_section = InspectorSection("DMA")
        self.dma_section.add_row("Active", "False")
        self.dma_section.add_row("Progress", "100%")
        self.dma_section.add_row("Completed", "0")

        self.int_section = InspectorSection("Interrupts")
        self.int_section.add_row("Pending", "0")
        self.int_section.add_row("In ISR", "False")

        self.profiler_section = InspectorSection("Profiler")
        self.profiler_section.add_row("Cycles", "0")
        self.profiler_section.add_row("Instructions", "0")
        self.profiler_section.add_row("CPI", "0.0")
        self.profiler_section.add_row("IPC", "0.0")
        self.profiler_section.add_row("Total Stalls", "0")

        for sec in [self.reg_section, self.flags_section,
                     self.pipeline_section, self.cache_section,
                     self.branch_section, self.bus_section,
                     self.dma_section, self.int_section,
                     self.profiler_section]:
            self._inner.addWidget(sec)
        self._inner.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def update_all(self, snap):
        for reg in ["R0", "R1", "R2", "R3"]:
            val = snap.registers.get(reg, "0")
            self.reg_section.update_row(reg, val)
        self.reg_section.update_row("PC", str(snap.pc))
        self.reg_section.update_row("SP", str(snap.sp))

        for flag in ["ZERO", "EQUAL", "GREATER", "LESS"]:
            val = snap.flags.get(flag, False)
            self.flags_section.update_row(flag, str(val))

        p = snap.pipeline
        self.pipeline_section.update_row("IF", p.if_stage)
        self.pipeline_section.update_row("ID", p.id_stage)
        self.pipeline_section.update_row("EX", p.ex_stage)
        self.pipeline_section.update_row("MEM", p.mem_stage)
        self.pipeline_section.update_row("WB", p.wb_stage)
        self.pipeline_section.update_row("Stalls", str(p.stall_cycles))
        self.pipeline_section.update_row("Flushes", str(p.flush_count))

        c = snap.cache
        self.cache_section.update_row("Hits", str(c.hits))
        self.cache_section.update_row("Misses", str(c.misses))
        self.cache_section.update_row("Hit Rate", f"{c.hit_rate:.0%}")

        b = snap.branch
        self.branch_section.update_row("Mode", b.mode)
        self.branch_section.update_row("Accuracy", f"{b.accuracy:.0%}")
        self.branch_section.update_row("Predictions", str(b.predictions))
        self.branch_section.update_row("Mispredicts", str(b.mispredictions))

        bus = snap.bus
        self.bus_section.update_row("Transfers", str(bus.transfers))
        self.bus_section.update_row("Utilization", f"{bus.utilization:.0%}")

        d = snap.dma
        self.dma_section.update_row("Active", str(d.active))
        self.dma_section.update_row("Progress", f"{d.progress:.0%}")
        self.dma_section.update_row("Completed", str(d.completed_transfers))

        ic = snap.interrupt
        self.int_section.update_row("Pending", str(ic.pending))
        self.int_section.update_row("In ISR", str(ic.in_isr))

        pr = snap.profiler
        self.profiler_section.update_row("Cycles", str(pr.cycles))
        self.profiler_section.update_row("Instructions", str(pr.instructions_retired))
        self.profiler_section.update_row("CPI", f"{pr.cpi:.3f}")
        self.profiler_section.update_row("IPC", f"{pr.ipc:.3f}")
        self.profiler_section.update_row("Total Stalls", str(pr.total_stalls))

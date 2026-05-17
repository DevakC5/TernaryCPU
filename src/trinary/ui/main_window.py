from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QStatusBar, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt

from trinary.cpu import CPU
from trinary.machine import Machine

from trinary.ui.assembler_editor import AssemblerEditor
from trinary.ui.controls import Controls
from trinary.ui.register_view import RegisterView
from trinary.ui.memory_view import MemoryView
from trinary.ui.stack_view import StackView
from trinary.ui.screen_view import ScreenView
from trinary.ui.execution_trace import ExecutionTrace
from trinary.ui.machine_code_view import MachineCodeView
from trinary.ui.demos import DEMOS


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TernaryVM — Visual Ternary Computer Simulator")
        self.resize(1100, 750)

        self.cpu = CPU()
        self.machine = Machine()
        self.program = []
        self.machine_code = []
        self.labels = {}
        self.step_count = 0
        self.assembled = False

        self._prev_mem = {}

        self._build_ui()
        self._connect_signals()
        self._update_views()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        self.controls = Controls()
        main_layout.addWidget(self.controls)

        self.banner_label = QLabel("")
        self.banner_label.setProperty("cssClass", "banner")
        self.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner_label.setMaximumHeight(32)
        main_layout.addWidget(self.banner_label)

        mid_splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

        asm_group = QGroupBox("Assembly Editor")
        asm_layout = QVBoxLayout(asm_group)
        self.assembler_editor = AssemblerEditor()
        asm_layout.addWidget(self.assembler_editor)
        left_layout.addWidget(asm_group)

        mc_group = QGroupBox("Machine Code")
        mc_layout = QVBoxLayout(mc_group)
        self.machine_code_view = MachineCodeView()
        mc_layout.addWidget(self.machine_code_view)
        left_layout.addWidget(mc_group)
        mid_splitter.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        self.register_view = RegisterView()
        right_layout.addWidget(self.register_view)

        mem_group = QGroupBox("Memory")
        mem_layout = QVBoxLayout(mem_group)
        self.memory_view = MemoryView()
        self.memory_view.populate()
        mem_layout.addWidget(self.memory_view)
        right_layout.addWidget(mem_group)

        stack_group = QGroupBox("Stack")
        stack_layout = QVBoxLayout(stack_group)
        self.stack_view = StackView()
        stack_layout.addWidget(self.stack_view)
        right_layout.addWidget(stack_group)

        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout(display_group)
        self.screen_view = ScreenView()
        display_layout.addWidget(self.screen_view)
        right_layout.addWidget(display_group)
        mid_splitter.addWidget(right_panel)

        mid_splitter.setSizes([500, 600])
        main_layout.addWidget(mid_splitter)

        trace_group = QGroupBox("Execution Trace")
        trace_layout = QVBoxLayout(trace_group)
        self.execution_trace = ExecutionTrace()
        trace_layout.addWidget(self.execution_trace)
        main_layout.addWidget(trace_group)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready — write assembly and click Run or Step")

    def _connect_signals(self):
        self.controls.demo_selector.currentTextChanged.connect(self._on_demo_selected)
        self.controls.assemble_btn.clicked.connect(self._on_assemble)
        self.controls.run_btn.clicked.connect(self._on_run)
        self.controls.step_btn.clicked.connect(self._on_step)
        self.controls.reset_btn.clicked.connect(self._on_reset)

    def _on_demo_selected(self, name):
        source = DEMOS.get(name)
        if source:
            self.assembler_editor.setPlainText(source.strip())
            self._on_reset()

    def _assemble_source(self):
        source = self.assembler_editor.get_source()
        try:
            self.machine_code, self.program, self.labels = self.machine.assemble(source)
            self.cpu.load_program(self.program)
            self.assembled = True
            self.step_count = 0
            self.execution_trace.clear_trace()
            self.memory_view.clear_marks()
            self._prev_mem = {}
            self.banner_label.setText("")
            self.assembler_editor.clear_highlight()
            return True
        except Exception as e:
            QMessageBox.warning(self, "Assembly Error", str(e))
            return False

    def _on_assemble(self):
        if self._assemble_source():
            self.machine_code_view.update_view(self.program, self.machine_code)
            self._update_views()
            self.status_bar.showMessage(
                f"Assembled OK — {len(self.program)} instructions, "
                f"{len(self.labels)} labels"
            )

    def _on_run(self):
        if not self.assembled:
            if not self._assemble_source():
                return
            self.machine_code_view.update_view(self.program, self.machine_code)
        if self.cpu.halted:
            self.status_bar.showMessage("CPU is halted — click Reset to start over")
            return
        while not self.cpu.halted and self.cpu.pc < len(self.cpu.program):
            self._do_step(add_trace=True)
        self._update_views()
        self.status_bar.showMessage(
            f"Execution finished — {self.step_count} steps total, "
            f"PC={self.cpu.pc}, halted={self.cpu.halted}"
        )

    def _on_step(self):
        if not self.assembled:
            if not self._assemble_source():
                return
            self.machine_code_view.update_view(self.program, self.machine_code)
        if self.cpu.halted:
            self.status_bar.showMessage("CPU is halted — click Reset to start over")
            return
        if self.cpu.pc >= len(self.cpu.program):
            self.cpu.halted = True
            self._update_views()
            self.status_bar.showMessage("Program ended — click Reset to start over")
            return
        self._do_step(add_trace=True)
        self._update_views()
        state = "halted" if self.cpu.halted else "running"
        self.status_bar.showMessage(
            f"Step {self.step_count} — PC={self.cpu.pc}, {state}"
        )

    def _on_reset(self):
        self.cpu.reset()
        if self.program:
            self.cpu.load_program(self.program)
        self.step_count = 0
        self.execution_trace.clear_trace()
        self.memory_view.clear_marks()
        self._prev_mem = {}
        self._update_views()
        self.machine_code_view.update_view(self.program, self.machine_code)
        self.banner_label.setText("")
        self.assembler_editor.clear_highlight()
        self.screen_view.refresh(self.cpu.memory)
        self.status_bar.showMessage("Reset — ready to run")

    def _snapshot_memory(self):
        return dict(self.cpu.memory.data)

    def _do_step(self, add_trace=False):
        old_pc = self.cpu.pc
        old_regs = dict(self.cpu.registers.dump())
        old_flags = dict(self.cpu.flags)
        instr = (
            self.cpu.program[self.cpu.pc]
            if self.cpu.pc < len(self.cpu.program)
            else "???"
        )
        before = self._snapshot_memory()
        self.cpu.step()
        after = self._snapshot_memory()
        self.step_count += 1
        for addr in range(self.cpu.memory.size):
            if before.get(addr) != after.get(addr):
                self.memory_view.mark_write(addr)
        if add_trace:
            self.execution_trace.add_entry(
                self.step_count, old_pc, instr, old_regs, old_flags
            )

    def _update_views(self):
        pc = self.cpu.pc
        self.register_view.update_view(
            self.cpu.registers.dump(),
            pc,
            self.cpu.sp,
            self.cpu.flags,
        )
        self.memory_view.update_view(self.cpu.memory, highlight_addr=pc)
        self.stack_view.update_view(self.cpu.memory, self.cpu.sp)
        self.machine_code_view.update_view(
            self.program, self.machine_code, highlight_addr=pc
        )
        self.assembler_editor.highlight_line(pc)
        if pc < len(self.program):
            instr = self.program[pc]
            self.banner_label.setText(f"▶  EXECUTING:  {instr}")
        else:
            self.banner_label.setText("")
        self.screen_view.refresh(self.cpu.memory)

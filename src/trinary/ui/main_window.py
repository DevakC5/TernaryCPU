"""Main Window — dual-mode UI: Simple (classic) and Architecture Visualization.

Architecture Mode provides a full educational computer architecture workstation
with pipeline visualizer, execution timeline, cache heatmap, branch predictor,
bus monitor, waveform viewer, hardware inspector, and performance dashboard.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QStatusBar, QMessageBox, QLabel, QPushButton,
    QApplication, QStackedWidget, QTabWidget, QComboBox,
    QToolBar, QCheckBox, QSlider,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from trinary.cpu import CPU
from trinary.machine import Machine
from trinary.memory import Memory

from trinary.ui.assembler_editor import AssemblerEditor
from trinary.ui.controls import Controls
from trinary.ui.register_view import RegisterView
from trinary.ui.memory_view import MemoryView
from trinary.ui.stack_view import StackView
from trinary.ui.screen_view import ScreenView
from trinary.ui.execution_trace import ExecutionTrace
from trinary.ui.machine_code_view import MachineCodeView
from trinary.ui.demos import DEMOS
from trinary.display import DisplayMemoryMap, PixelDisplay, Framebuffer
from trinary.os import Kernel

# Architecture visualization widgets
from trinary.ui.pipeline_widget import PipelineVisualizer
from trinary.ui.timeline_widget import ExecutionTimelineWidget
from trinary.ui.cache_widget import CacheInspectorWidget
from trinary.ui.branch_widget import BranchPredictorWidget
from trinary.ui.bus_widget import BusMonitorWidget
from trinary.ui.waveform_widget import WaveformWidget
from trinary.ui.inspector_widget import HardwareInspectorWidget
from trinary.ui.debugger_widget import DebuggerController
from trinary.ui.performance_widget import PerformanceDashboardWidget
from trinary.ui.viz_engine import VisualizationEngine


class MainWindow(QMainWindow):
    """Main window with dual-mode: Simple (classic) and Architecture Visualization."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TernaryVM — Visual Ternary Computer Simulator")
        self.resize(1400, 900)

        # CPU and machine state
        self.cpu = CPU()
        self.machine = Machine()
        self.program = []
        self.machine_code = []
        self.labels = {}
        self.step_count = 0
        self.assembled = False
        self._pause_requested = False

        self._prev_mem = {}
        self._os_kernel = None
        self._os_fb = Framebuffer()
        self._os_mode = False

        # Visualization engine
        self.viz_engine = VisualizationEngine()
        self._architecture_mode = False
        self._execution_history = []

        self._build_ui()
        self._connect_signals()
        self._update_views()

    def _build_ui(self):
        self._build_simple_mode()
        self._build_architecture_mode()

        self.mode_stack = QStackedWidget()
        self.mode_stack.addWidget(self._simple_page)
        self.mode_stack.addWidget(self._arch_page)
        self.setCentralWidget(self.mode_stack)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "Simple Mode (Classic)",
            "Architecture Visualization",
        ])
        self.mode_selector.currentIndexChanged.connect(self._on_mode_changed)

        self.controls = Controls()
        self.debugger = DebuggerController()

        toolbar = QToolBar("Controls")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("QToolBar { background: #0a0a1a; border: none; padding: 2px; }")
        toolbar.addWidget(self.mode_selector)
        toolbar.addSeparator()
        toolbar.addWidget(self.controls)
        self.addToolBar(toolbar)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.banner_label = QLabel("")
        self.banner_label.setProperty("cssClass", "banner")
        self.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner_label.setMaximumHeight(32)
        self.status_bar.addPermanentWidget(self.banner_label)

        self.status_bar.showMessage("Ready — write assembly and click Run or Step")

    def _build_simple_mode(self):
        """Build the classic simple debug layout."""
        self._simple_page = QWidget()
        layout = QVBoxLayout(self._simple_page)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

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
        pixel_btn_row = QHBoxLayout()
        for label, method in [
            ("Diagonal", "_on_pixel_diagonal"),
            ("Checkerboard", "_on_pixel_checkerboard"),
            ("Smiley", "_on_pixel_smiley"),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(24)
            btn.clicked.connect(getattr(self, method))
            pixel_btn_row.addWidget(btn)
        pixel_btn_row.addStretch()
        display_layout.addLayout(pixel_btn_row)
        right_layout.addWidget(display_group)
        mid_splitter.addWidget(right_panel)

        mid_splitter.setSizes([500, 600])
        layout.addWidget(mid_splitter)

        trace_group = QGroupBox("Execution Trace")
        trace_layout = QVBoxLayout(trace_group)
        self.execution_trace = ExecutionTrace()
        trace_layout.addWidget(self.execution_trace)
        layout.addWidget(trace_group)

    def _build_architecture_mode(self):
        """Build the full architecture visualization layout."""
        self._arch_page = QWidget()
        layout = QVBoxLayout(self._arch_page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Pipeline visualizer (top)
        self.pipeline_viz = PipelineVisualizer()
        layout.addWidget(self.pipeline_viz)

        # Middle: Timeline + Waveform tabs
        mid_splitter = QSplitter(Qt.Orientation.Horizontal)
        mid_tabs = QTabWidget()
        mid_tabs.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #0f3460; background: #0a0a1a; }"
            "QTabBar::tab { background: #16213e; color: #888; padding: 6px 16px; margin: 1px; }"
            "QTabBar::tab:selected { background: #0f3460; color: #00ff88; }"
        )

        self.timeline_widget = ExecutionTimelineWidget()
        mid_tabs.addTab(self.timeline_widget, "Execution Timeline")

        self.waveform_widget = WaveformWidget()
        mid_tabs.addTab(self.waveform_widget, "Signal Waveform")

        mid_splitter.addWidget(mid_tabs)

        # Right: Inspector + Performance
        right_tabs = QTabWidget()
        right_tabs.setStyleSheet(mid_tabs.styleSheet())

        self.inspector_widget = HardwareInspectorWidget()
        right_tabs.addTab(self.inspector_widget, "Hardware Inspector")

        self.performance_widget = PerformanceDashboardWidget()
        right_tabs.addTab(self.performance_widget, "Performance")

        mid_splitter.addWidget(right_tabs)
        mid_splitter.setSizes([700, 350])
        layout.addWidget(mid_splitter, 1)

        # Bottom: Cache + Branch + Bus in tabs
        bottom_tabs = QTabWidget()
        bottom_tabs.setStyleSheet(mid_tabs.styleSheet())

        self.cache_widget = CacheInspectorWidget()
        bottom_tabs.addTab(self.cache_widget, "Cache (D$)")

        self.cache_icache_widget = CacheInspectorWidget()
        bottom_tabs.addTab(self.cache_icache_widget, "Cache (I$)")

        self.branch_widget = BranchPredictorWidget()
        bottom_tabs.addTab(self.branch_widget, "Branch Predictor")

        self.bus_widget = BusMonitorWidget()
        bottom_tabs.addTab(self.bus_widget, "Bus Monitor")

        layout.addWidget(bottom_tabs)

    def _connect_signals(self):
        self.controls.demo_selector.currentTextChanged.connect(self._on_demo_selected)
        self.controls.assemble_btn.clicked.connect(self._on_assemble)
        self.controls.run_btn.clicked.connect(self._on_run)
        self.controls.step_btn.clicked.connect(self._on_step)
        self.controls.step_over_btn.clicked.connect(self._on_step_over)
        self.controls.reset_btn.clicked.connect(self._on_reset)
        self.controls.pause_btn.clicked.connect(self._on_pause)
        self.controls.continue_btn.clicked.connect(self._on_continue)
        self.controls.boot_os_btn.clicked.connect(self._on_boot_os)

        # Debugger controller signals
        self.debugger.step_cycle.connect(self._on_step)
        self.debugger.step_instruction.connect(self._on_step)
        self.debugger.run_continue.connect(self._on_continue)
        self.debugger.pause.connect(self._on_pause)
        self.debugger.reset.connect(self._on_reset)

        self.screen_view.key_pressed.connect(self._on_key_pressed)

    def _on_mode_changed(self, index):
        self._architecture_mode = (index == 1)
        self.mode_stack.setCurrentIndex(index)
        if self._architecture_mode:
            self._ensure_realistic_cpu()
        self._update_views()

    def _ensure_realistic_cpu(self):
        if not hasattr(self.cpu, 'pipeline') or not self.cpu.realistic_timing:
            self.cpu = CPU(realistic_timing=True)
            if self.program:
                self.cpu.load_program(self.program)

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
            self.viz_engine.clear()
            self._execution_history.clear()
            if hasattr(self, 'execution_trace'):
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
        self._run_loop(run_to_halt=True)

    def _on_continue(self):
        if not self.assembled or self.cpu.halted:
            return
        self._run_loop(run_to_halt=True)

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
        self._update_cycle_display()
        state = "halted" if self.cpu.halted else "running"
        self.status_bar.showMessage(
            f"Step {self.step_count} — PC={self.cpu.pc}, cycles={self.cpu.cycles}, {state}"
        )

    def _on_step_over(self):
        if not self.assembled:
            if not self._assemble_source():
                return
            self.machine_code_view.update_view(self.program, self.machine_code)
        if self.cpu.halted or self.cpu.pc >= len(self.cpu.program):
            return
        instr = self.cpu.program[self.cpu.pc]
        opcode = instr.split()[0] if instr else ""
        if opcode == "CALL":
            target_pc = self.cpu.pc + 1
            while not self.cpu.halted and self.cpu.pc < len(self.cpu.program):
                self._do_step(add_trace=True)
                if self.cpu.pc == target_pc:
                    break
                QApplication.processEvents()
        else:
            if self.cpu.pc >= len(self.cpu.program):
                return
            self._do_step(add_trace=True)
        self._update_views()
        self._update_cycle_display()
        self.status_bar.showMessage(
            f"Step Over — PC={self.cpu.pc}, cycles={self.cpu.cycles}"
        )

    def _on_boot_os(self):
        self._os_fb.clear()
        self._os_kernel = Kernel(self._os_fb, self.cpu)
        self._os_kernel.boot()
        self._os_mode = True
        self._os_tick_count = 0
        self.status_bar.showMessage("TernaryOS booted — type commands in the Display area")
        if hasattr(self, 'screen_view'):
            self.screen_view.set_display_source(self._os_fb)
            self.screen_view.update()

    def _on_pause(self):
        self._pause_requested = True

    def _on_reset(self):
        self.cpu.reset()
        if self.program:
            self.cpu.load_program(self.program)
        self.step_count = 0
        self._pause_requested = False
        self.viz_engine.clear()
        self._execution_history.clear()
        if hasattr(self, 'execution_trace'):
            self.execution_trace.clear_trace()
        self.memory_view.clear_marks()
        self._prev_mem = {}
        DisplayMemoryMap().clear(self.cpu.memory)
        if hasattr(self, 'screen_view'):
            self.screen_view.clear()
        from trinary.conversion import decimal_to_ternary as d2t
        self.cpu.memory.store(260, d2t(0))
        self._update_views()
        self.machine_code_view.update_view(self.program, self.machine_code)
        self.banner_label.setText("")
        self.assembler_editor.clear_highlight()
        self._update_cycle_display()
        self.status_bar.showMessage("Reset — ready to run")

    def _run_loop(self, run_to_halt=True):
        self._pause_requested = False
        breakpoints = self.assembler_editor.get_breakpoints()
        while not self.cpu.halted and self.cpu.pc < len(self.cpu.program):
            if self._pause_requested:
                self.status_bar.showMessage(
                    f"Paused at PC={self.cpu.pc} — {self.cpu.cycles} cycles"
                )
                break
            self._do_step(add_trace=True)
            if run_to_halt and self.cpu.pc in breakpoints:
                self._update_views()
                self._update_cycle_display()
                self.status_bar.showMessage(
                    f"Breakpoint hit at PC={self.cpu.pc} — {self.cpu.cycles} cycles"
                )
                return
            QApplication.processEvents()
        self._update_views()
        self._update_cycle_display()
        if self.cpu.halted:
            self.status_bar.showMessage(
                f"Execution finished — {self.step_count} instr, "
                f"{self.cpu.cycles} cycles, "
                f"PC={self.cpu.pc}"
            )

    def _pixel_demo(self, name):
        if not hasattr(self, 'screen_view'):
            return
        self.screen_view.clear()
        p = self.screen_view.display()
        if name == "diagonal":
            p.draw_line(0, 0, 26, 26, 2)
            p.draw_line(26, 0, 0, 26, 1)
        elif name == "checkerboard":
            for by in range(0, 27, 3):
                for bx in range(0, 27, 3):
                    val = 1 if ((bx // 3) + (by // 3)) % 2 == 0 else 0
                    for dy in range(3):
                        for dx in range(3):
                            p.set_pixel(bx + dx, by + dy, val)
        elif name == "smiley":
            for y in range(27):
                for x in range(27):
                    p.set_pixel(x, y, 0)
            for ey in (8, 9):
                for ex in (8, 9):
                    p.set_pixel(ex, ey, 2)
            for ey in (8, 9):
                for ex in (18, 19):
                    p.set_pixel(ex, ey, 2)
            for x in range(7, 21):
                y = 16
                p.set_pixel(x, y, 2)
            for x in range(9, 19):
                p.set_pixel(x, 17, 2)
            for x in range(11, 17):
                p.set_pixel(x, 18, 2)
            p.set_pixel(13, 19, 2)
        self.screen_view.refresh()
        self.status_bar.showMessage(f"Pixel demo: {name}")

    def _on_pixel_diagonal(self):
        self._pixel_demo("diagonal")

    def _on_pixel_checkerboard(self):
        self._pixel_demo("checkerboard")

    def _on_pixel_smiley(self):
        self._pixel_demo("smiley")

    def _on_key_pressed(self, ascii_code):
        from trinary.conversion import decimal_to_ternary as d2t
        key_addr = 260
        if self._os_mode and self._os_kernel and self._os_kernel.running:
            self.cpu.memory.store(key_addr, d2t(ascii_code))
        else:
            try:
                self.cpu.memory.store(key_addr, d2t(ascii_code))
                self.memory_view.mark_write(key_addr)
            except ValueError:
                pass
        self.status_bar.showMessage(f"KB: '{chr(ascii_code)}' ({ascii_code})")

    def _snapshot_memory(self):
        return dict(self.cpu.memory.data)

    def _update_cycle_display(self):
        cyc = self.cpu.cycles
        ipc = self.step_count / cyc if cyc else 0
        self.controls.cycle_label.setText(f"Cycles: {cyc}  IPC: {ipc:.3f}")

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
            if hasattr(self, 'execution_trace'):
                self.execution_trace.add_entry(
                    self.step_count, old_pc, instr, old_regs, old_flags
                )
            self._update_viz(instr)

    def _update_viz(self, instr):
        """Update architecture visualization widgets from CPU state."""
        if not self._architecture_mode:
            return

        snap = self.viz_engine.capture(self.cpu)

        # Pipeline
        self.pipeline_viz.update_pipeline(snap.pipeline)

        # Cache
        self.cache_widget.update_cache(snap.cache)
        self.cache_icache_widget.update_cache(snap.cache_icache)

        # Branch
        self.branch_widget.update_branch(snap.branch)

        # Bus
        self.bus_widget.update_bus(snap.bus)

        # Inspector
        self.inspector_widget.update_all(snap)

        # Performance
        self.performance_widget.update_performance(snap)

        # Build execution history for timeline
        self._update_execution_history(instr)
        self.timeline_widget.update_timeline(self._execution_history, snap.clock_cycle)

        # Build signal data for waveform
        signal_data = self._build_signal_data(snap)
        self.waveform_widget.update_waveform(signal_data, snap.clock_cycle)

    def _update_execution_history(self, instr):
        """Build per-instruction stage trace for the timeline view."""
        if not hasattr(self.cpu, 'pipeline'):
            return
        pipe = self.cpu.pipeline
        stages = []
        for s in pipe.stages:
            if s.bubble:
                stages.append("---")
            elif s.stalled:
                stages.append("STALL")
            else:
                stages.append(s.name)
        entry = {
            "name": instr.strip().split()[0] if instr.strip() else "NOP",
            "stages": stages,
        }
        self._execution_history.append(entry)
        if len(self._execution_history) > 100:
            self._execution_history = self._execution_history[-50:]

    def _build_signal_data(self, snap):
        """Build signal waveforms from snapshot data."""
        clock_cycle = snap.clock_cycle
        signals = {
            "clk": [1 if i % 2 == 0 else 0 for i in range(max(1, clock_cycle + 1))],
            "pc": [1 if snap.pc > 0 else 0 for _ in range(max(1, clock_cycle + 1))],
            "sp": [1 if snap.sp != 255 else 0 for _ in range(max(1, clock_cycle + 1))],
            "halted": [1 if snap.halted else 0 for _ in range(max(1, clock_cycle + 1))],
            "cache_hit": [1 for _ in range(max(1, clock_cycle + 1))],
            "branch_taken": [0 for _ in range(max(1, clock_cycle + 1))],
            "int": [1 if snap.interrupt.pending > 0 else 0 for _ in range(max(1, clock_cycle + 1))],
            "dma": [1 if snap.dma.active else 0 for _ in range(max(1, clock_cycle + 1))],
            "bus": [1 if snap.bus.utilization > 0.5 else 0 for _ in range(max(1, clock_cycle + 1))],
        }
        return signals

    def _update_views(self):
        pc = self.cpu.pc
        if self._os_mode and self._os_kernel and self._os_kernel.running:
            self._os_kernel.tick()

        if hasattr(self, 'register_view'):
            self.register_view.update_view(
                self.cpu.registers.dump(),
                pc,
                self.cpu.sp,
                self.cpu.flags,
            )
        if hasattr(self, 'memory_view'):
            self.memory_view.update_view(self.cpu.memory, highlight_addr=pc)
        if hasattr(self, 'stack_view'):
            self.stack_view.update_view(self.cpu.memory, self.cpu.sp)
        if hasattr(self, 'machine_code_view'):
            self.machine_code_view.update_view(
                self.program, self.machine_code, highlight_addr=pc
            )
        if hasattr(self, 'assembler_editor'):
            self.assembler_editor.highlight_line(pc)
        if pc < len(self.program):
            instr = self.program[pc]
            self.banner_label.setText(f"\u25b6  EXECUTING:  {instr}")
        else:
            self.banner_label.setText("")
        if hasattr(self, 'screen_view'):
            self.screen_view.refresh()

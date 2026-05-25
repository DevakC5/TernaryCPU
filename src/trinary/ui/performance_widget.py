"""Performance Dashboard — live CPI/IPC/stall charts with time-series history."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath


CHART_BG = QColor("#0a0a1a")
BAR_COLORS = {
    "cpi": QColor("#ff8844"),
    "ipc": QColor("#00ff88"),
    "stalls": QColor("#ff4444"),
    "cache": QColor("#4488ff"),
    "branch": QColor("#8888ff"),
}
PLOT_COLORS = {
    "cpi": QColor("#ff8844"),
    "ipc": QColor("#00ff88"),
    "stalls": QColor("#ff4444"),
    "cache": QColor("#4488ff"),
}


class MiniBarChart(QWidget):
    """Small horizontal bar chart for a single metric."""

    def __init__(self, label="", color=QColor("#00ff88"), parent=None):
        super().__init__(parent)
        self.label = label
        self.color = color
        self._value = 0.0
        self._max_val = 10.0
        self.setMinimumHeight(24)

    def set_value(self, val, max_val=None):
        self._value = val
        if max_val is not None:
            self._max_val = max_val
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, CHART_BG)

        p.setPen(QPen(QColor("#0f3460"), 1))
        p.drawRect(0, 2, w - 1, h - 4)

        frac = min(1.0, self._value / max(0.01, self._max_val))
        bar_w = int((w - 4) * frac)
        if bar_w > 0:
            p.fillRect(2, 4, bar_w, h - 8, self.color)

        p.setPen(QColor("#e0e0e0"))
        p.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        p.drawText(int(0), 0, int(w), int(h),
                   int(Qt.AlignmentFlag.AlignCenter),
                   f"{self.label}: {self._value:.3f}")
        p.end()


class TimeSeriesChart(QWidget):
    """Live-updating line chart for time-series performance data."""

    def __init__(self, label="", color=QColor("#00ff88"), max_points=80, parent=None):
        super().__init__(parent)
        self.label = label
        self.color = color
        self.max_points = max_points
        self._data = []
        self.setMinimumHeight(80)
        self.setMinimumWidth(200)

    def add_point(self, value):
        self._data.append(value)
        if len(self._data) > self.max_points:
            self._data = self._data[-self.max_points:]
        self.update()

    def clear(self):
        self._data.clear()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, CHART_BG)

        # Border
        p.setPen(QPen(QColor("#0f3460"), 1))
        p.drawRect(0, 0, w - 1, h - 1)

        # Label
        p.setPen(QColor("#888"))
        p.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        p.drawText(int(4), 2, int(w - 8), 16,
                   int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), self.label)

        if len(self._data) < 2:
            p.setPen(QColor("#555"))
            p.setFont(QFont("Courier New", 7))
            p.drawText(int(0), 0, int(w), int(h),
                       int(Qt.AlignmentFlag.AlignCenter), "waiting for data...")
            p.end()
            return

        # Compute plot area
        margin = 4
        plot_x = margin
        plot_y = 20
        plot_w = w - 2 * margin
        plot_h = h - plot_y - margin

        # Find min/max
        min_val = min(self._data)
        max_val = max(self._data)
        if max_val - min_val < 0.001:
            max_val = min_val + 0.1
            min_val = max(0, min_val - 0.05)

        # Grid lines
        p.setPen(QPen(QColor("#0f3460"), 1))
        for i in range(1, 5):
            gy = plot_y + (plot_h * i) // 5
            p.drawLine(plot_x, gy, plot_x + plot_w, gy)

        # Draw line chart
        path = QPainterPath()
        n = len(self._data)
        for i, val in enumerate(self._data):
            x = plot_x + (i / max(n - 1, 1)) * plot_w
            y = plot_y + plot_h - ((val - min_val) / max(max_val - min_val, 0.001)) * plot_h
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        p.setPen(QPen(self.color, 2))
        p.setBrush(QBrush())
        p.drawPath(path)

        # Draw dots
        dot_pen = QPen(self.color.lighter(120), 1)
        for i, val in enumerate(self._data):
            x = plot_x + (i / max(n - 1, 1)) * plot_w
            y = plot_y + plot_h - ((val - min_val) / max(max_val - min_val, 0.001)) * plot_h
            p.setPen(dot_pen)
            p.setBrush(QBrush(self.color))
            p.drawEllipse(int(x) - 2, int(y) - 2, 4, 4)

        # Current value
        last_val = self._data[-1]
        p.setPen(self.color)
        p.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        p.drawText(int(plot_x), int(plot_y + plot_h - 14), int(plot_w), 12,
                   int(Qt.AlignmentFlag.AlignRight), f"{last_val:.3f}")

        p.end()


class PerformanceDashboardWidget(QWidget):
    """Live performance dashboard with bar charts and time-series plots."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Bar charts row
        top = QHBoxLayout()
        self.cpi_chart = MiniBarChart("CPI", BAR_COLORS["cpi"])
        self.ipc_chart = MiniBarChart("IPC", BAR_COLORS["ipc"])
        for chart in (self.cpi_chart, self.ipc_chart):
            chart.setMinimumWidth(120)
            top.addWidget(chart)
        layout.addLayout(top)

        middle = QHBoxLayout()
        self.stall_chart = MiniBarChart("Stalls", BAR_COLORS["stalls"])
        self.cache_chart = MiniBarChart("Cache HR", BAR_COLORS["cache"])
        self.branch_chart = MiniBarChart("Branch Acc", BAR_COLORS["branch"])
        for chart in (self.stall_chart, self.cache_chart, self.branch_chart):
            chart.setMinimumWidth(80)
            middle.addWidget(chart)
        layout.addLayout(middle)

        # Time-series charts
        series_layout = QHBoxLayout()
        self.cpi_series = TimeSeriesChart("CPI over time", PLOT_COLORS["cpi"])
        self.ipc_series = TimeSeriesChart("IPC over time", PLOT_COLORS["ipc"])
        self.stall_series = TimeSeriesChart("Stalls over time", PLOT_COLORS["stalls"])
        for chart in (self.cpi_series, self.ipc_series, self.stall_series):
            series_layout.addWidget(chart)
        layout.addLayout(series_layout, 1)

        # Metrics grid
        grid = QGridLayout()
        grid.setSpacing(2)
        self.metrics = {}
        for i, (key, label, color) in enumerate([
            ("cycles", "Cycles", "#888"),
            ("instructions", "Instructions", "#00ff88"),
            ("cpi", "CPI", "#ff8844"),
            ("ipc", "IPC", "#00ff88"),
            ("stalls", "Total Stalls", "#ff4444"),
            ("cache_rate", "Cache HR", "#4488ff"),
            ("branch_acc", "Branch Acc", "#8888ff"),
            ("bus_util", "Bus Util", "#88ff88"),
        ]):
            lbl = QLabel(f"{label}: 0")
            lbl.setStyleSheet(
                f"color: {color}; font: 8px Courier New; padding: 2px 6px; "
                f"border: 1px solid #0f3460; border-radius: 2px;"
            )
            self.metrics[key] = lbl
            grid.addWidget(lbl, i // 4, i % 4)
        layout.addLayout(grid)

        self.setLayout(layout)

    def update_performance(self, snap):
        pr = snap.profiler
        self.cpi_chart.set_value(pr.cpi, max(5.0, pr.cpi * 2))
        self.ipc_chart.set_value(pr.ipc, max(1.0, pr.ipc * 2))

        total_stalls = pr.total_stalls
        self.stall_chart.set_value(total_stalls, max(10, total_stalls * 2))
        self.cache_chart.set_value(pr.cache_hit_rate, 1.0)
        self.branch_chart.set_value(pr.branch_accuracy, 1.0)

        self.cpi_series.add_point(pr.cpi)
        self.ipc_series.add_point(pr.ipc)
        self.stall_series.add_point(total_stalls)

        self.metrics["cycles"].setText(f"Cycles: {pr.cycles}")
        self.metrics["instructions"].setText(f"Instructions: {pr.instructions_retired}")
        self.metrics["cpi"].setText(f"CPI: {pr.cpi:.3f}")
        self.metrics["ipc"].setText(f"IPC: {pr.ipc:.3f}")
        self.metrics["stalls"].setText(f"Stalls: {total_stalls}")
        self.metrics["cache_rate"].setText(f"Cache HR: {pr.cache_hit_rate:.0%}")
        self.metrics["branch_acc"].setText(f"Branch Acc: {pr.branch_accuracy:.0%}")
        self.metrics["bus_util"].setText(f"Bus Util: {snap.bus.utilization:.0%}")

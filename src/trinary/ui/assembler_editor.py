import re

from PyQt6.QtWidgets import QTextEdit, QWidget
from PyQt6.QtGui import (
    QFont, QSyntaxHighlighter, QTextCharFormat, QColor,
    QTextCursor, QPainter, QPen, QBrush,
)
from PyQt6.QtCore import Qt, QRect, QSize


OPCODES_SET = {
    "LOAD", "MOV", "CLR",
    "ADD", "SUB", "MUL", "DIV", "AND", "OR", "NOT",
    "CMP", "JMP", "JZ", "JNZ",
    "PUSH", "POP", "CALL", "RET", "HALT"
}
REGISTERS_SET = {"R0", "R1", "R2", "R3"}


class AssemblerHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        opcode_fmt = QTextCharFormat()
        opcode_fmt.setForeground(QColor("#00ccff"))
        opcode_fmt.setFontWeight(QFont.Weight.Bold)
        self._rules = [
            (re.compile(r"\b(" + "|".join(sorted(OPCODES_SET)) + r")\b"), opcode_fmt)
        ]

        reg_fmt = QTextCharFormat()
        reg_fmt.setForeground(QColor("#ffcc00"))
        self._rules.append((re.compile(r"\b(R[0-3])\b"), reg_fmt))

        label_fmt = QTextCharFormat()
        label_fmt.setForeground(QColor("#cc88ff"))
        self._rules.append((re.compile(r"^[a-zA-Z_]\w*:"), label_fmt))

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#558855"))
        comment_fmt.setFontItalic(True)
        self._rules.append((re.compile(r";[^\n]*"), comment_fmt))
        self._rules.append((re.compile(r"#[^\n]*"), comment_fmt))

        number_fmt = QTextCharFormat()
        number_fmt.setForeground(QColor("#ffffff"))
        self._rules.append((re.compile(r"\b\d+\b"), number_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


DEFAULT_PROGRAM = """\
; Simple Demo Program
; Add two numbers and store result

start:
    LOAD R0 12
    LOAD R1 21
    ADD R0 R1
    MOV R2 R0
    HALT
"""


GUTTER_WIDTH = 28


class BreakpointArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor
        self.setFixedWidth(GUTTER_WIDTH)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(event.rect(), QColor("#1a1a2e"))
        qp.setPen(QPen(QColor("#0f3460"), 1))
        qp.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

        doc = self._editor.document()
        block = doc.begin()
        sb = self._editor.verticalScrollBar()
        offset_y = -sb.value() if sb else 0
        fm = qp.fontMetrics()
        bp = self._editor._breakpoints

        while block.isValid():
            y = doc.documentLayout().blockBoundingRect(block).top() + offset_y
            if y + fm.height() < 0:
                block = block.next()
                continue
            if y > self.height():
                break
            line = block.blockNumber()
            if line in bp:
                qp.setBrush(QBrush(QColor("#ff3333")))
                qp.setPen(Qt.PenStyle.NoPen)
                cx = (self.width() - 10) / 2
                cy = y + (fm.height() - 10) / 2
                qp.drawEllipse(QRect(int(cx), int(cy), 10, 10))
            block = block.next()

    def mousePressEvent(self, event):
        line = self._editor._line_at_y(event.position().toPoint().y())
        if line >= 0:
            self._editor.toggle_breakpoint(line)


class AssemblerEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont("Courier New", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(24)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setPlainText(DEFAULT_PROGRAM.strip())
        self.setViewportMargins(GUTTER_WIDTH, 0, 0, 0)
        self._highlighter = AssemblerHighlighter(self.document())
        self._last_highlight = -1
        self._breakpoints = set()
        self._breakpoint_area = BreakpointArea(self)
        self.document().blockCountChanged.connect(self._update_gutter)
        self.verticalScrollBar().valueChanged.connect(self._update_gutter)

    def _update_gutter(self):
        self._breakpoint_area.update()

    def _line_at_y(self, y):
        block = self.document().begin()
        sb = self.verticalScrollBar()
        offset_y = -sb.value() if sb else 0
        while block.isValid():
            rect = self.document().documentLayout().blockBoundingRect(block)
            block_top = rect.top() + offset_y
            block_bottom = rect.bottom() + offset_y
            if block_top <= y <= block_bottom:
                return block.blockNumber()
            block = block.next()
        return -1

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._breakpoint_area.setGeometry(
            QRect(cr.left(), cr.top(), GUTTER_WIDTH, cr.height())
        )

    def get_source(self):
        return self.toPlainText()

    def highlight_line(self, line_num):
        if line_num == self._last_highlight:
            return
        self._last_highlight = line_num
        self._update_gutter()
        cursor = QTextCursor(self.document().findBlockByLineNumber(line_num))
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def clear_highlight(self):
        self._last_highlight = -1
        self._update_gutter()
        self.moveCursor(QTextCursor.MoveOperation.Start)

    def toggle_breakpoint(self, line):
        if line in self._breakpoints:
            self._breakpoints.discard(line)
        else:
            self._breakpoints.add(line)
        self._update_gutter()

    def get_breakpoints(self):
        return set(self._breakpoints)

    def clear_breakpoints(self):
        self._breakpoints.clear()
        self._update_gutter()

    def has_breakpoint(self, line):
        return line in self._breakpoints

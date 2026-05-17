import re

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor
from PyQt6.QtCore import Qt


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


class AssemblerEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont("Courier New", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(24)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setPlainText(DEFAULT_PROGRAM.strip())
        self._highlighter = AssemblerHighlighter(self.document())
        self._last_highlight = -1

    def get_source(self):
        return self.toPlainText()

    def highlight_line(self, line_num):
        if line_num == self._last_highlight:
            return
        self._last_highlight = line_num
        cursor = QTextCursor(self.document().findBlockByLineNumber(line_num))
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def clear_highlight(self):
        self._last_highlight = -1
        self.moveCursor(QTextCursor.MoveOperation.Start)

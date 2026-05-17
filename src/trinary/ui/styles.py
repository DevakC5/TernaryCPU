DARK_STYLE = """
QMainWindow {
    background-color: #1a1a2e;
    color: #e0e0e0;
}
QTextEdit, QPlainTextEdit, QTableWidget, QListWidget {
    background-color: #16213e;
    color: #00ff88;
    border: 1px solid #0f3460;
    font-family: "Courier New", monospace;
    font-size: 12px;
}
QTableWidget {
    gridline-color: #0f3460;
}
QTableWidget::item {
    padding: 2px 6px;
}
QHeaderView::section {
    background-color: #0f3460;
    color: #e0e0e0;
    padding: 4px;
    border: 1px solid #1a1a2e;
    font-weight: bold;
}
QGroupBox {
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 4px;
    margin-top: 8px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QLabel {
    color: #e0e0e0;
}
QLabel[cssClass="value"] {
    color: #00ff88;
    font-family: "Courier New", monospace;
    font-size: 13px;
    font-weight: bold;
}
QLabel[cssClass="flag_active"] {
    color: #00ff88;
    font-weight: bold;
}
QLabel[cssClass="flag_inactive"] {
    color: #555;
}
QLabel[cssClass="banner"] {
    color: #00ffcc;
    font-family: "Courier New", monospace;
    font-size: 14px;
    font-weight: bold;
    background-color: #0a1628;
    border: 1px solid #00ff88;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton {
    background-color: #0f3460;
    color: #e0e0e0;
    border: 1px solid #1a1a2e;
    border-radius: 4px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: bold;
    min-width: 70px;
}
QPushButton:hover {
    background-color: #16213e;
    border-color: #00ff88;
}
QPushButton:pressed {
    background-color: #0a1628;
}
QPushButton:disabled {
    background-color: #2a2a3e;
    color: #666;
}
QPushButton[cssClass="run"] {
    background-color: #006633;
}
QPushButton[cssClass="run"]:hover {
    background-color: #008844;
}
QPushButton[cssClass="step"] {
    background-color: #004488;
}
QPushButton[cssClass="step"]:hover {
    background-color: #0055aa;
}
QPushButton[cssClass="reset"] {
    background-color: #882200;
}
QPushButton[cssClass="reset"]:hover {
    background-color: #aa3300;
}
QComboBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    min-width: 120px;
}
QComboBox::drop-down {
    border: none;
    background-color: #0f3460;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #e0e0e0;
    selection-background-color: #0f3460;
    font-size: 12px;
}
QScrollBar:vertical {
    background-color: #1a1a2e;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #0f3460;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QStatusBar {
    background-color: #0a0a1a;
    color: #888;
}
QSplitter::handle {
    background-color: #0f3460;
    width: 2px;
}
"""

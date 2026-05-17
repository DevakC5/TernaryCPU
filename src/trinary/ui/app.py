import sys
from PyQt6.QtWidgets import QApplication
from trinary.ui.styles import DARK_STYLE
from trinary.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

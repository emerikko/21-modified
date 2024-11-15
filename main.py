"""Запуск лаунчера игры"""

import sys

from PyQt6.QtWidgets import QApplication

from launcher import Launcher

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher()
    sys.exit(app.exec())

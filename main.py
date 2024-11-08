from PyQt6.QtWidgets import QApplication, QWidget
import sys
import traceback
from launcher import Launcher


def global_exception_handler(type, value, tb):
    print("Uncaught exception:")
    traceback.print_exception(type, value, tb)


sys.excepthook = global_exception_handler

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher()
    sys.exit(app.exec())

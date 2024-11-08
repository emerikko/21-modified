from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt


class Rules(QWidget):
    def __init__(self, screen_size, offset):
        super().__init__()
        self.rules = open("rules.txt", "r", encoding="utf-8")
        self.rules_description = self.rules.read()
        self.screen_size = screen_size
        self.offset = offset
        self.initUI()

    def initUI(self):
        area = self.screen_size[0] // 4, self.screen_size[1]
        shift = self.screen_size[1] // 50
        width = area[0] - self.offset
        height = area[1] // 2 - (self.offset + 30)
        font_size = (self.screen_size[0] + self.screen_size[1]) // 150

        self.setWindowTitle("Правила")
        self.setGeometry(self.offset, self.offset + 30, width, height)
        self.setMinimumSize(width, height)
        self.description = QLabel(self.rules_description, self)
        self.description.setGeometry(shift, shift, width, height)
        self.description.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.description.setStyleSheet(f"font-size: {font_size}px;")

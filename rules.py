from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt


class Rules(QWidget):
    def __init__(self, screen_size, offset, language, translations):
        super().__init__()
        self.language = language
        self.translations = translations
        self.screen_size = screen_size
        self.offset = offset
        self.initUI()

    def initUI(self):
        shift = self.screen_size[1] // 50
        width = self.screen_size[0] - self.offset - self.offset
        height = self.screen_size[1] - self.offset - self.offset - 60
        font_size = (self.screen_size[0] + self.screen_size[1]) // 150

        self.setWindowTitle(self.translations[self.language]["rules"])
        self.setGeometry(self.offset, self.offset + 30, width, height)
        self.description = QLabel(self.translations[self.language]["rules_text"], self)
        self.description.setGeometry(shift, shift, width, height)
        self.description.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.description.setStyleSheet(f"font-size: {font_size}px;")

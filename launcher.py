from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QMainWindow, QWidget, QLabel, QRadioButton, QButtonGroup, QFrame
from PyQt6.QtGui import QFont, QFontDatabase

import pyautogui
import json
from ctypes import windll
import sys
from os import listdir
from random import randint

from Game import DefaultGame
from rules import Rules


class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        translation_file = "translation.json"
        self.translations = json.load(open(translation_file, "r", encoding="utf-8"))["translations"]
        self.language = json.load(open(translation_file, "r", encoding="utf-8"))["language"]
        self.rules_window = None
        if sys.platform == "win32":
            self.scaleFactor = windll.shcore.GetScaleFactorForDevice(0) / 100
        else:
            self.scaleFactor = 1.0
        self.screen_size = int(pyautogui.size()[0] // self.scaleFactor), int(pyautogui.size()[1] // self.scaleFactor)
        self.offset = int(50 / self.scaleFactor * (self.screen_size[0] / 1920 + self.screen_size[1] / 1080) / 2)

        try:
            wins = open("wins.json", "r")
            self.wins = json.load(wins)
        except FileNotFoundError:
            wins = open("wins.json", "w")
            self.wins = {"player_1": 0, "player_2": 0}
            json.dump(self.wins, wins)
        self.initUI()

    def initUI(self):
        shift = (self.screen_size[0] + self.screen_size[1]) // 150
        width = self.screen_size[0] // 2 - 2 * self.offset
        height = self.screen_size[1] // 2 - (self.offset + 30)
        font_size = self.screen_size[1] // 50

        self.setStyleSheet("background-color:#1e1e1e; color: #747474;")
        self.setWindowTitle(self.translations[self.language]["launcher"])
        self.setGeometry(self.screen_size[0] // 4 + self.offset, self.offset + 30, width, height)
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)

        self.exit_button = QPushButton(self.translations[self.language]["exit"], self)
        self.exit_button.setGeometry(shift, height - (height // 8) - shift, width // 4, height // 8)
        self.exit_button.clicked.connect(self.closeEvent)
        self.exit_button.setEnabled(True)
        self.exit_button.setStyleSheet(f"background-color: #FF652F; font-size: {font_size}px; color: #272727;")

        self.reset_button = QPushButton(self.translations[self.language]["reset_stats"], self)
        self.reset_button.setGeometry(shift, height - 2 * shift - 2 * (height // 8), width // 4, height // 8)
        self.reset_button.clicked.connect(self.resetStats)
        self.reset_button.setEnabled(True)
        self.reset_button.setStyleSheet(f"font-size: {font_size}px;")

        self.rules_button = QPushButton(self.translations[self.language]["rules"], self)
        self.rules_button.setGeometry(width * 3 // 4 - shift, height * 3 // 4 - 2 * shift, width // 4, height // 8)
        self.rules_button.clicked.connect(self.showRules)
        self.rules_button.setEnabled(True)
        self.rules_button.setStyleSheet(f"font-size: {font_size}px;")

        self.start_button = QPushButton(self.translations[self.language]["play"], self)
        self.start_button.setGeometry(width * 3 // 4 - shift, height * 7 // 8 - shift, width // 4, height // 8)
        self.start_button.clicked.connect(self.startGame)
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet(f"background-color: #14A76C; font-size: {font_size}px; color: #272727;")

        self.line1 = QFrame(self)
        self.line1.setGeometry(width * 3 // 4 - shift - shift, 0, 3, height)
        self.line1.setFrameShape(QFrame.Shape.VLine)
        self.line1.setFrameShadow(QFrame.Shadow.Sunken)

        self.line2 = QFrame(self)
        self.line2.setGeometry(width // 3 - shift * 3 // 2, 0, 3, height)
        self.line2.setFrameShape(QFrame.Shape.VLine)
        self.line2.setFrameShadow(QFrame.Shadow.Sunken)

        self.stats_label = QLabel(self)
        self.stats_label.setGeometry(shift, shift, width * 7 // 32, height // 4)
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stats_label.setStyleSheet(f"font-size: {font_size}px;")

        self.stats_values = QLabel(self)
        self.stats_values.setGeometry(shift + width * 7 // 32, shift, 5 * shift, height // 4)
        self.stats_values.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stats_values.setStyleSheet(f"font-size: {font_size}px;")

        self.updateStats()

        self.mode_group = QButtonGroup(self)
        self.default_mode = QRadioButton(self.translations[self.language]["default_mode"], self)
        self.default_mode.setObjectName("0")
        self.default_mode.setGeometry(width * 3 // 4 - shift, shift, width // 4, height // 8)
        self.default_mode.setStyleSheet(f"font-size: {font_size}px;")
        self.mode_group.addButton(self.default_mode)
        self.special_mode = QRadioButton(self.translations[self.language]["special_mode"], self)
        self.special_mode.setObjectName("1")
        self.special_mode.setGeometry(width * 3 // 4 - shift, shift + height // 8, width // 4, height // 8)
        self.special_mode.setStyleSheet(f"font-size: {font_size}px;")
        self.mode_group.addButton(self.special_mode)
        self.mode_group.buttonToggled.connect(self.setMode)

        self.player_group = QButtonGroup(self)
        self.player_mode = QRadioButton(self.translations[self.language]["with_player"], self)
        self.player_mode.setObjectName("0")
        self.player_mode.setGeometry(width * 3 // 4 - shift, shift + height * 2 // 8, width // 4, height // 8)
        self.player_mode.setStyleSheet(f"font-size: {font_size}px;")
        self.player_group.addButton(self.player_mode)
        self.player_group.buttonToggled.connect(self.setMode)

        self.language_group = QButtonGroup(self)
        self.russian = QRadioButton("Русский", self)
        self.russian.setObjectName("0")
        self.russian.setGeometry(width * 3 // 4 - shift, shift + height * 3 // 8, width // 4, height // 8)
        self.russian.setStyleSheet(f"font-size: {font_size}px;")
        self.language_group.addButton(self.russian)

        self.english = QRadioButton("English", self)
        self.english.setObjectName("1")
        self.english.setGeometry(width * 3 // 4 - shift, shift + height * 4 // 8, width // 4, height // 8)
        self.english.setStyleSheet(f"font-size: {font_size}px;")
        self.language_group.addButton(self.english)
        self.language_group.buttonToggled.connect(self.updateLanguage)

        self.show()

    def setMode(self):
        if self.mode_group.checkedButton() is not None and self.player_group.checkedButton() is not None:
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)

    def closeEvent(self, event):
        wins = open("wins.json", "w")
        json.dump(self.wins, wins)
        wins.close()
        self.closeRules()
        self.close()

    def updateStats(self):
        wins = open("wins.json", "r")
        self.stats_label.setText(f"{self.translations[self.language]['wins_of_player']} 1:\n"
                                 f"{self.translations[self.language]['wins_of_player']} 2:\n")
        self.wins = json.load(wins)
        wins.close()
        self.stats_values.setText(f"{self.wins['player_1']}\n"
                                  f"{self.wins['player_2']}\n")

    def updateLanguage(self):
        if self.language_group.checkedButton().text() == "Русский":
            self.language = "ru"
            json.dump({"language": "ru", "translations": self.translations}, open("translation.json", "w", encoding="utf-8"))
        elif self.language_group.checkedButton().text() == "English":
            self.language = "en"
            json.dump({"language": "en", "translations": self.translations}, open("translation.json", "w", encoding="utf-8"))

    def showRules(self):
        self.rules_window = Rules(self.screen_size, self.offset, self.language, self.translations)
        self.rules_window.show()

    def closeRules(self):
        if self.rules_window is not None:
            self.rules_window.close()

    def resetStats(self):
        wins = open("wins.json", "w")
        self.wins = {"player_1": 0, "player_2": 0, "bot": 0}
        json.dump(self.wins, wins)
        wins.close()
        self.updateStats()

    def startGame(self):
        if self.player_group.checkedButton().objectName() == "0":
            self.game_window = DefaultGame(self.screen_size, self.offset,
                                           self.player_group.checkedButton().objectName(), self.language, self.translations)
        elif self.player_group.checkedButton().objectName() == "1":
            pass
        self.game_window.show()
        self.close()

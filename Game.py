from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QMainWindow, QWidget, QLabel
import random
import json

from numba.core.typing.dictdecl import infer_getattr


class ValueCard(QWidget):
    def __init__(self, screen_size: set, offset: int, value: int, player: int, language,
                 translations, hidden: bool = False):
        super().__init__()
        self.language = language
        self.translations = translations
        self.label = QLabel(self)
        self.value = value
        self.hidden = hidden
        self.player = player
        self.screen_size = screen_size
        self.offset = offset
        self.opened = False
        self.font_size = (self.screen_size[0] + self.screen_size[1]) // 200
        self.initUI()

    def initUI(self):
        width = self.screen_size[0] // 8 - self.offset // 4
        height = self.screen_size[1] // 3 - (self.offset + 30)
        shift = (self.width() // 50 + self.height() // 50) // 2

        self.setWindowTitle(f"{self.translations[self.language]['card_of_player']} {self.player + 1}")
        self.resize(width, height)
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)

        if self.hidden:
            self.visibilityBtn = QPushButton(self)
            self.visibilityBtn.setGeometry(shift, shift, width // 2 - 3 // 2 * shift, height - 2 * shift)
            self.visibilityBtn.setText('\n'.join(list(self.translations[self.language]['show'])))
            self.visibilityBtn.clicked.connect(self.changeValueVisibility)
            self.visibilityBtn.setStyleSheet(f"background-color: #A23326; font-size: {self.font_size}px;")

        self.label.setGeometry(width // 2 + shift // 2, 0, width // 2 - 3 // 2 * shift, height)
        self.label.setStyleSheet(f"font-size: {self.font_size * 3}px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setText(str(self.value))
        if self.hidden:
            self.label.hide()

    def changeValueVisibility(self):
        if self.label.isVisible():
            self.label.hide()
            self.visibilityBtn.setText('\n'.join(list(self.translations[self.language]['show'])))
            self.visibilityBtn.setStyleSheet(f"background-color: #A23326; font-size: {self.font_size}px;")
        else:
            self.label.show()
            self.visibilityBtn.setText('\n'.join(list(self.translations[self.language]['hide'])))
            self.visibilityBtn.setStyleSheet(f"background-color: #5CDB95; font-size: {self.font_size}px; "
                                             f"color: black;")

    def closeEvent(self, event):
        self.hideCard()

    def openCard(self, opened_amount):
        self.opened = True
        self.move(self.offset + (self.width() + self.offset) * opened_amount, self.offset + self.screen_size[1] // 2)
        self.show()

    def hideCard(self):
        self.opened = False
        self.close()


class DefaultGame(QMainWindow):
    def __init__(self, screen_size, offset, player_mode, language, translations):
        super().__init__()
        self.language = language
        self.translations = translations
        self.player_turn = 0
        self.screen_size = screen_size
        self.offset = offset
        self.value_cards = []
        self.pl1_cards = []
        self.pl2_cards = []
        self.value_stack = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.action_buttons = {
            "take_card": None,
            "end_turn": None,
            "exit": None
        }
        self.skipped = 0
        random.shuffle(self.value_stack)
        self.player_mode = player_mode
        self.startGame()
        self.showCards(self.player_turn)
        self.initUI()

    def initUI(self):
        width = self.screen_size[0] - 2 * self.offset
        height = self.screen_size[1] // 2 - (self.offset + 30)
        shift = (width // 50 + height // 50) // 2
        font_size = (self.screen_size[0] + self.screen_size[1]) // 100

        self.infoLabel1 = QLabel(f"{self.translations[self.language]['turn_of_player']} {self.player_turn + 1}", self)
        self.infoLabel1.setGeometry(shift, shift, width - shift - shift, (height - shift - shift) // 8)
        self.infoLabel1.setStyleSheet(f"font-size: {font_size}px;")

        self.infoLabel2 = QLabel(
            f"{self.translations[self.language]['amount_of_cards']} {self.player_turn % 2 + 2}: "
            f"{len([card for card in self.value_cards if card.player == (self.player_turn + 1) % 2])}",
            self)
        self.infoLabel2.setGeometry(shift, shift + (height - shift - shift) // 8,
                                    width - shift - shift, (height - shift - shift) // 8)


        self.actionButton1 = QPushButton(self)
        self.actionButton1.setGeometry(width // 2,
                                       shift + (height - shift - shift) * 3 // 4,
                                       (width - shift - shift - shift) // 4, (height - shift - shift) // 4)
        self.actionButton1.setStyleSheet(f"font-size: {font_size}px; color: #ffffff;")

        self.actionButton2 = QPushButton(self)
        self.actionButton2.setGeometry(shift + (width - shift - shift) * 3 // 4,
                                       shift + (height - shift - shift) * 3 // 4,
                                       (width - shift - shift - shift) // 4, (height - shift - shift) // 4)
        self.actionButton2.setStyleSheet(f"font-size: {font_size}px; color: #ffffff;")

        self.actionButton3 = QPushButton(self)
        self.actionButton3.setGeometry(shift + (width - shift - shift) * 3 // 4,
                                       (height - shift - shift) // 2,
                                       (width - shift - shift - shift) // 4, (height - shift - shift) // 4)
        self.actionButton3.setStyleSheet(f"background-color: #A23326; font-size: {font_size}px; color: #272727;")

        self.action_buttons["take_card"] = self.actionButton1
        self.action_buttons["end_turn"] = self.actionButton2
        self.action_buttons["exit"] = self.actionButton3

        self.actionButton1.setText(f"{self.translations[self.language]['take_card']}")
        self.actionButton1.clicked.connect(self.summonValueCard)

        self.actionButton2.setText(f"{self.translations[self.language]['end_turn']}")
        self.actionButton2.clicked.connect(self.switchTurn)

        self.actionButton3.setText(f"{self.translations[self.language]['exit']}")
        self.actionButton3.clicked.connect(self.closeEvent)
        self.actionButton3.setVisible(False)

        self.setWindowTitle(f"21 {self.translations[self.language]['point']}")
        self.setGeometry(self.offset, self.offset + 30, width, height)
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)
        self.show()

    def closeEvent(self, event):
        self.closeCards(True)
        self.close()

    def switchTurn(self):
        self.closeCards(True)
        self.player_turn = (self.player_turn + 1) % 2
        self.showCards(self.player_turn)
        print(self.skipped)
        if self.skipped >= 1:
            self.endGame()
        if len(self.value_stack) != 0:
            self.action_buttons["take_card"].setEnabled(True)
        self.skipped += 1
        self.infoLabel1.setText(f"{self.translation[language]['end_turn']} {self.player_turn + 1}")
        self.infoLabel2.setText(
            f"{self.translations[self.language]['amount_of_cards']} {self.player_turn % 2 + 2}: "
            f"{len([card for card in self.value_cards if card.player == (self.player_turn + 1) % 2])}")

    def startGame(self):
        for i in range(4):
            value = self.value_stack.pop()
            self.value_cards.append(ValueCard(self.screen_size, self.offset, value, i % 2, self.language,
                 self.translations, True))

    def endGame(self):
        points = {0: 0, 1: 0}
        for card in self.value_cards:
            points[card.player] += card.value
        if points[self.player_turn] > 21:
            winner = (self.player_turn + 1) % 2
            self.infoLabel1.setText(f"{self.translations[self.language]['player']} {self.player_turn + 1} "
                                    f"{self.translations[self.language]['lost']}")
        else:
            if points[0] > points[1]:
                winner = 0
            elif points[0] < points[1]:
                winner = 1
            else:
                winner = None
                self.infoLabel1.setText(f"Ничья")

        if winner is not None:
            self.infoLabel1.setText(f"{self.translations[self.language]['player']} {winner + 1} "
                                    f"{self.translations[self.language]['won'].lower()}")

        self.actionButton3.setVisible(True)
        self.actionButton1.setEnabled(False)
        self.actionButton2.setEnabled(False)
        self.action_buttons["end_turn"].setVisible(True)

    def closeCards(self, all=False):
        opened = [card.opened for card in self.value_cards].count(True)
        if not all:
            player = int(self.sender().objectName())
            for card in self.value_cards:
                if card.player == player and card.opened:
                    card.hideCard()
                    opened -= 1
        else:
            for card in self.value_cards:
                if card.opened:
                    card.hideCard()
                    opened -= 1

    def showCards(self, player):
        opened = [card.opened for card in self.value_cards].count(True)
        for card in self.value_cards:
            if card.player == player and not card.opened:
                card.openCard(opened)
                opened += 1

    def summonValueCard(self):
        value = self.value_stack.pop()
        self.value_cards.append(ValueCard(self.screen_size, self.offset, value,
                                          self.player_turn, self.language, self.translations,True))
        self.showCards(self.player_turn)
        self.action_buttons["take_card"].setEnabled(False)
        points = {0: 0, 1: 0}
        for card in self.value_cards:
            points[card.player] += card.value
        if points[self.player_turn] > 21:
            self.endGame()

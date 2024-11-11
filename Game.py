from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QMainWindow, QWidget, QLabel
import random


class ValueCard(QWidget):
    def __init__(self, screen_size: set, offset: int, value: int, player: int, hidden: bool = False):
        super().__init__()
        self.label = QLabel(self)
        self.value = value
        self.hidden = hidden
        self.player = player
        self.screen_size = screen_size
        self.offset = offset
        self.opened = False
        self.font_size = (self.screen_size[0] + self.screen_size[1]) // 150
        self.initUI()

    def initUI(self):
        width = self.screen_size[0] // 8 - self.offset // 4
        height = self.screen_size[1] // 4 - (self.offset + 30)
        shift = (self.width() // 50 + self.height() // 50) // 2

        self.setWindowTitle(f"Карта игрока {self.player + 1}")
        self.resize(width, height)
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)

        if self.hidden:
            self.visibilityBtn = QPushButton(self)
            self.visibilityBtn.setGeometry(shift, shift, width // 2 - 3 // 2 * shift, height - 2 * shift)
            self.visibilityBtn.setText("П\nО\nК\nА\nЗ\nА\nТ\nЬ")
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
            self.visibilityBtn.setText("П\nО\nК\nА\nЗ\nА\nТ\nЬ")
            self.visibilityBtn.setStyleSheet(f"background-color: #A23326; font-size: {self.font_size}px;")
        else:
            self.label.show()
            self.visibilityBtn.setText("С\nК\nР\nЫ\nТ\nЬ")
            self.visibilityBtn.setStyleSheet(f"background-color: #5CDB95; font-size: {self.font_size}px; "
                                             f"color: black;")

    def closeEvent(self, event):
        self.hideCard()

    def openCard(self, opened_amount):
        self.opened = True
        print(self.hidden)
        self.move(self.offset + (self.width() + self.offset) * opened_amount, self.offset + self.screen_size[1] // 2)
        self.show()

    def hideCard(self):
        self.opened = False
        self.close()


class DefaultGame(QMainWindow):
    def __init__(self, screen_size, offset, player_mode):
        super().__init__()
        self.player_turn = 0
        self.screen_size = screen_size
        self.offset = offset
        self.value_cards = []
        self.pl1_cards = []
        self.pl2_cards = []
        self.value_stack = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.action_buttons = {
            "take_card": None,
            "end_turn": None
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
        font_size = (self.screen_size[0] + self.screen_size[1]) // 150

        self.turnLabel = QLabel(f"Ход игрока {self.player_turn + 1}", self)
        self.turnLabel.setGeometry(shift, shift, (width - shift - shift) // 4, (height - shift - shift) // 8)
        self.turnLabel.setStyleSheet(f"font-size: {font_size * 2}px;")

        self.actionButton1 = QPushButton(self)
        self.actionButton1.setGeometry(width // 2,
                                       shift + (height - shift - shift) * 3 // 4,
                                       (width - shift - shift - shift) // 4, (height - shift - shift) // 4)
        self.actionButton2 = QPushButton(self)
        self.actionButton2.setGeometry(shift + (width - shift - shift) * 3 // 4,
                                       shift + (height - shift - shift) * 3 // 4,
                                       (width - shift - shift - shift) // 4, (height - shift - shift) // 4)

        self.action_buttons["take_card"] = self.actionButton1
        self.action_buttons["end_turn"] = self.actionButton2

        self.actionButton1.setText("Взять карту")
        self.actionButton1.clicked.connect(self.summonValueCard)

        self.actionButton2.setText("Закончить ход")
        self.actionButton2.clicked.connect(self.switch_turn)

        self.setWindowTitle("21 очко")
        self.setGeometry(self.offset, self.offset + 30, width, height)
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)
        self.show()

    def closeEvent(self, event):
        self.closeCards(True)
        self.close()

    def switch_turn(self):
        self.closeCards(True)
        self.player_turn = (self.player_turn + 1) % 2
        self.showCards(self.player_turn)
        if self.skipped != 2:
            self.endGame()
        if len(self.value_stack) != 0:
            self.action_buttons["take_card"].setEnabled(True)

    def startGame(self):
        for i in range(4):
            value = self.value_stack.pop()
            self.value_cards.append(ValueCard(self.screen_size, self.offset, value, i % 2, True))

    def endGame(self):
        points = {0: 0, 1: 0}
        for card in self.value_cards:
            points[card.player] += card.value
        print('end')

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
        self.value_cards.append(ValueCard(self.screen_size, self.offset, value, self.player_turn, True))
        self.showCards(self.player_turn)
        self.action_buttons["take_card"].setEnabled(False)
        points = {0: 0, 1: 0}
        for card in self.value_cards:
            points[card.player] += card.value
        if points[self.player_turn] > 21:
            self.endGame()
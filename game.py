from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QMainWindow, QWidget, QLabel
import random


class Game(QMainWindow):
    def __init__(self, screen_size, offset, game_mode, player_mode):
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
        random.shuffle(self.value_stack)
        self.game_mode = game_mode
        self.player_mode = player_mode
        self.begin_game()
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

        self.setWindowTitle("21 очко")
        self.setGeometry(self.offset, self.offset + 30, width, height)
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)
        self.show()

    def closeEvent(self, event):
        self.closeCards(True)
        self.close()

    def closeCards(self, all=False):
        opened = [card.opened for card in self.value_cards].count(True)
        if not all:
            player = int(self.sender().objectName())
            for card in self.value_cards:
                if card.player == player and card.opened:
                    card.closeCard()
                    opened -= 1
        else:
            for card in self.value_cards:
                if card.opened:
                    card.closeCard()
                    opened -= 1

    def showCards(self, player):
        opened = [card.opened for card in self.value_cards].count(True)
        print(opened)
        for card in self.value_cards:
            if card.player == player and not card.opened:
                card.openCard(opened)
                opened += 1

    def begin_game(self):
        self.summonValueCard(True)
        self.summonValueCard(True)
        self.summonValueCard()
        self.summonValueCard()

    def summonValueCard(self, hidden=False):
        value = self.value_stack.pop()
        self.value_cards.append(self.ValueCard(self.screen_size, self.offset, value, self.player_turn, hidden))
        if len(self.value_stack) == 0:
            self.action_buttons["take_card"].setEnabled(False)
        self.player_turn = (self.player_turn + 1) % 2

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
            self.closeCard()

        def openCard(self, opened_amount):
            self.opened = True
            self.move(self.offset + (self.width() + self.offset) * opened_amount, self.offset + self.screen_size[1] // 2)
            self.show()

        def closeCard(self):
            self.opened = False
            self.close()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    import traceback
    import pyautogui
    from ctypes import windll

    def global_exception_handler(exc_type, exc_value, exc_traceback):
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        exit(1)

    sys.excepthook = global_exception_handler

    if sys.platform == "win32":
        scaleFactor = windll.shcore.GetScaleFactorForDevice(0) / 100
    else:
        scaleFactor = 1.0
    screen_size = int(pyautogui.size()[0] // scaleFactor), int(pyautogui.size()[1] // scaleFactor)

    app = QApplication(sys.argv)
    game = Game(screen_size, int(50 // scaleFactor), 0, 0)
    sys.exit(app.exec())

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QMainWindow, QWidget, QLabel
from random import shuffle
import json


class ValueCard(QWidget):
    def __init__(self, screen_size: set, offset: int, value: int, player_id: int, language,
                 translations, is_hidden: bool = False):
        super().__init__()
        self.language = language
        self.translations = translations
        self.value = value
        self.is_hidden = is_hidden
        self.player_id = player_id
        self.screen_size = screen_size
        self.offset = offset
        self.is_opened = False
        self.font_size = (self.screen_size[0] + self.screen_size[1]) // 200
        self.initUI()

    def initUI(self):
        card_width = self.screen_size[0] // 8 - self.offset // 4
        card_height = self.screen_size[1] // 3 - (self.offset + 30)
        shift = (self.width() // 50 + self.height() // 50) // 2

        self.setWindowTitle(f"{self.translations[self.language]['card_of_player']} {self.player_id + 1}")
        self.resize(card_width, card_height)
        self.setMaximumSize(card_width, card_height)
        self.setMinimumSize(card_width, card_height)

        if self.is_hidden:
            # Создать кнопку для отображения/скрывания значения карты
            self.visibilityBtn = QPushButton(self)
            self.visibilityBtn.setGeometry(shift, shift, card_width // 2 - 3 // 2 * shift, card_height - 2 * shift)
            self.visibilityBtn.setText('\n'.join(list(self.translations[self.language]['show'])))
            self.visibilityBtn.clicked.connect(self.changeValueVisibility)
            self.visibilityBtn.setStyleSheet(f"background-color: #A23326; font-size: {self.font_size}px;")

        # Создать лейбл для отображения значения карты
        self.value_label = QLabel(self)
        self.value_label.setGeometry(card_width // 2 + shift // 2, 0, card_width // 2 - 3 // 2 * shift, card_height)
        self.value_label.setStyleSheet(f"font-size: {self.font_size * 3}px;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setText(str(self.value))
        if self.is_hidden:
            self.value_label.hide()

    def changeValueVisibility(self):
        if self.value_label.isVisible():
            self.setValueVisibility(False)
        else:
            self.setValueVisibility(True)

    def setValueVisibility(self, status: bool):
        if status:
            self.value_label.show()
            self.visibilityBtn.setText('\n'.join(list(self.translations[self.language]['hide'])))
            self.visibilityBtn.setStyleSheet(f"background-color: #5CDB95; font-size: {self.font_size}px; "
                                             f"color: black;")
        else:
            self.value_label.hide()
            self.visibilityBtn.setText('\n'.join(list(self.translations[self.language]['show'])))
            self.visibilityBtn.setStyleSheet(f"background-color: #A23326; font-size: {self.font_size}px;")

    def closeEvent(self, event):
        self.hideCard()

    def openCard(self, opened_amount):
        self.is_opened = True
        self.move(self.offset + (self.width() + self.offset) * opened_amount, self.offset + self.screen_size[1] // 2)
        self.show()

    def hideCard(self):
        self.is_opened = False
        self.close()


class DefaultGame(QMainWindow):
    def __init__(self, screen_size, offset, player_mode, language, translations):
        super().__init__()
        self.language = language
        self.translations = translations
        self.current_player = 0
        self.screen_size = screen_size
        self.offset = offset
        self.value_cards = []
        self.player1_cards = []
        self.player2_cards = []
        self.winner = None
        self.stats_updated = False
        self.value_stack = [i for i in range(1, 11)]
        shuffle(self.value_stack)
        self.skipped = 0
        self.player_mode = player_mode
        self.start_game()
        self.show_cards(self.current_player)
        self.initUI()

    def initUI(self):
        width = self.screen_size[0] - 2 * self.offset
        height = self.screen_size[1] // 2 - (self.offset + 30)
        shift = (width // 50 + height // 50) // 2
        font_size = (self.screen_size[0] + self.screen_size[1]) // 100

        # Создаётся лейбл для отображения главной информации. (Текущий ход, победитель и т.п.)
        self.info_label1 = QLabel(f"{self.translations[self.language]['turn_of_player']} "
                                  f"{self.current_player + 1}", self)
        self.info_label1.setGeometry(shift, shift, width - shift - shift, (height - shift - shift) // 8)
        self.info_label1.setStyleSheet(f"font-size: {font_size}px;")

        # Создаётся лейбл для отображения главной информации. (Кол-во карты и т.п.)
        self.info_label2 = QLabel(
            f"{self.translations[self.language]['amount_of_cards']} {self.current_player % 2 + 2}: "
            f"{len([card for card in self.value_cards if card.player_id == (self.current_player + 1) % 2])}",
            self)
        self.info_label2.setGeometry(shift, shift + (height - shift - shift) // 8,
                                     width - shift - shift, (height - shift - shift) // 8)
        self.info_label2.setStyleSheet(f"font-size: {font_size // 2}px;")

        # Создаётся кнопку для взятия карты
        self.take_button = QPushButton(self)
        self.take_button.setGeometry(width // 2,
                                     shift + (height - shift - shift) * 3 // 4,
                                     (width - shift - shift - shift) // 4, (height - shift - shift) // 4)
        self.take_button.setStyleSheet(f"font-size: {font_size}px; color: #ffffff;")
        self.take_button.setText(f"{self.translations[self.language]['take_card']}")
        self.take_button.clicked.connect(self.take_value_card)

        # Создаётся кнопку для завершения хода
        self.end_button = QPushButton(self)
        self.end_button.setGeometry(shift + (width - shift - shift) * 3 // 4,
                                    shift + (height - shift - shift) * 3 // 4,
                                    (width - shift - shift - shift) // 4, (height - shift - shift) // 4)
        self.end_button.setStyleSheet(f"font-size: {font_size}px; color: #ffffff;")
        self.end_button.setText(f"{self.translations[self.language]['end_turn']}")
        self.end_button.clicked.connect(self.switch_turn)

        # Создаётся кнопку для выхода из игры
        self.exit_button = QPushButton(self)
        self.exit_button.setGeometry(shift + (width - shift - shift) * 3 // 4,
                                     (height - shift - shift) // 2,
                                     (width - shift - shift - shift) // 4, (height - shift - shift) // 4)
        self.exit_button.setStyleSheet(f"background-color: #A23326; font-size: {font_size}px; color: #272727;")
        self.exit_button.setText(f"{self.translations[self.language]['exit']}")
        self.exit_button.clicked.connect(self.closeEvent)
        self.exit_button.setVisible(False)

        self.setWindowTitle(f"21 {self.translations[self.language]['point']}")
        self.setGeometry(self.offset, self.offset + 30, width, height)
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)
        self.show()

    def closeEvent(self, event):
        self.close_cards(True)
        if self.winner is not None and not self.stats_updated:
            stats = json.load(open("stats.json", "r", encoding="utf-8"))
            stats[f"{self.winner}"] += 1
            json.dump(stats, open("stats.json", "w", encoding="utf-8"))
            self.stats_updated = True
        self.close()

    def switch_turn(self):
        self.close_cards(True)
        self.current_player = (self.current_player + 1) % 2
        self.show_cards(self.current_player)
        if len(self.value_stack) != 0:
            self.take_button.setEnabled(True)
        self.info_label1.setText(f"{self.translations[self.language]['end_turn']} {self.current_player + 1}")
        self.info_label2.setText(
            f"{self.translations[self.language]['amount_of_cards']} {(self.current_player + 1) % 2 + 1}: "
            f"{len([card for card in self.value_cards if card.player_id == (self.current_player + 1) % 2])}")
        if self.skipped >= 2:
            self.end_game()
        else:
            self.skipped += 1

    def start_game(self):
        for i in range(4):
            value = self.value_stack.pop()
            self.value_cards.append(ValueCard(self.screen_size, self.offset, value, i % 2, self.language,
                                              self.translations, True))

    def end_game(self):
        points = {0: 0, 1: 0}
        for card in self.value_cards:
            points[card.player_id] += card.value

        if points[self.current_player] > 21:
            self.winner = (self.current_player + 1) % 2
        else:
            if points[0] > points[1]:
                self.winner = 0
            elif points[0] < points[1]:
                self.winner = 1
            else:
                self.winner = None
                self.info_label1.setText(f"{self.translations[self.language]['draw']}")

        if self.winner is not None:
            self.info_label1.setText(f"{self.translations[self.language]['player']} {self.winner + 1} "
                                     f"{self.translations[self.language]['won'].lower()}")
        self.info_label2.setText(f"{self.translations[self.language]['cards_of_player']} 1: "
                                 f"{', '.join([str(card.value) for card in self.value_cards if card.player_id == 0])}; "
                                 f"{self.translations[self.language]['cards_of_player']} 2: "
                                 f"{', '.join([str(card.value) for card in self.value_cards if card.player_id == 1])}")

        self.close_cards(True)
        self.exit_button.setVisible(True)
        self.take_button.setEnabled(False)
        self.end_button.setEnabled(False)

    def close_cards(self, close_all=False):
        opened = [card.is_opened for card in self.value_cards].count(True)
        if not close_all:
            player_id = int(self.sender().objectName())
            for card in self.value_cards:
                if card.player_id == player_id and card.is_opened:
                    card.setValueVisibility(False)
                    card.hideCard()
                    opened -= 1
        else:
            for card in self.value_cards:
                if card.is_opened:
                    card.setValueVisibility(False)
                    card.hideCard()
                    opened -= 1
                if card.value_label.isVisible():
                    card.changeValueVisibility()

    def show_cards(self, player_id):
        opened = [card.is_opened for card in self.value_cards].count(True)
        for card in self.value_cards:
            if card.player_id == player_id and not card.is_opened:
                card.openCard(opened)
                opened += 1

    def take_value_card(self):
        value = self.value_stack.pop()
        self.skipped = 0
        self.value_cards.append(ValueCard(self.screen_size, self.offset, value,
                                          self.current_player, self.language, self.translations, True))
        self.show_cards(self.current_player)
        self.take_button.setEnabled(False)
        points = {0: 0, 1: 0}
        for card in self.value_cards:
            points[card.player_id] += card.value
        if points[self.current_player] > 21:
            self.end_game()

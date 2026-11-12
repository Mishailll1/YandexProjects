import sys
from PyQt6.QtWidgets import QWidget, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class GameTrack(QWidget):
    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_downloaded)
        self.initUI()
        self.setFixedSize(850, 600)
        self.setWindowTitle("GameTracker")

    def initUI(self):
        main1 = QVBoxLayout()
        tags_lay = QHBoxLayout()
        center_lay = QHBoxLayout()
        text_lay = QVBoxLayout()
        buttons_lay = QVBoxLayout()
        right_lay = QVBoxLayout()

        big_font = QFont()
        big_font.setPointSize(24)
        big_font.setBold(True)
        small_font = QFont()
        small_font.setPointSize(16)

        v1 = QVBoxLayout()
        v3 = QVBoxLayout()

        self.tags = QComboBox()
        self.tags.setFixedWidth(110)
        self.tags.addItem("Не начата")
        self.tags.addItem("Заброшено")
        self.tags.addItem("В процессе")
        self.tags.addItem("Пройдено!")
        self.tags.addItem("Платина!💎")

        self.add = QPushButton("Добавить игру")
        self.add_many = QPushButton("Добавить игры(TXT)")
        self.add_id = QPushButton("Добавить SteamID")
        self.refreshed = QPushButton("Обновить")
        self.delete_game = QPushButton("Удалить игру")

        self.delete_game.setStyleSheet("color: red;")

        buttons_lay.addWidget(self.add)
        buttons_lay.addWidget(self.add_many)
        buttons_lay.addWidget(self.add_id)

        tags_lay.addLayout(buttons_lay)
        tags_lay.addStretch(1)
        right_lay.addWidget(self.tags)
        right_lay.addWidget(self.refreshed)
        right_lay.addWidget(self.delete_game)
        tags_lay.addLayout(right_lay)

        self.NextBut = QPushButton("-->")
        self.PreviousBut = QPushButton("<--")

        self.status = QLabel("Не начата")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(small_font)

        self.header = QLabel()
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setMinimumSize(550, 350)
        self.header.setScaledContents(True)
        self.header.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        v1.addWidget(self.status)
        v1.addWidget(self.header)

        center_lay.addWidget(self.PreviousBut)
        center_lay.addStretch(1)
        center_lay.addLayout(v1)
        center_lay.addStretch(1)
        center_lay.addWidget(self.NextBut)

        self.name = QLabel("?")
        self.name.setFont(big_font)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hours = QLabel("0 ч.")
        self.hours.setFont(small_font)
        self.hours.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.achivements = QLabel(f"Достижений: 0/0")
        self.achivements.setFont(small_font)
        self.achivements.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_lay.addWidget(self.name)
        text_lay.addWidget(self.hours)
        text_lay.addWidget(self.achivements)

        main1.addLayout(tags_lay)
        main1.addStretch(1)
        main1.addLayout(center_lay)
        main1.addStretch(1)
        main1.addLayout(text_lay)

        self.setLayout(main1)

    def load_img(self, url):
        request = QNetworkRequest(QUrl(url))
        self.network_manager.get(request)

    def on_downloaded(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            img = reply.readAll()

            pixmap = QPixmap()
            pixmap.loadFromData(img)

            scaled_pixmap = pixmap.scaled(
                self.header.width(),
                self.header.height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.header.setPixmap(scaled_pixmap)
            self.header.setStyleSheet("background-color: transparent; border: none;")
        else:
            self.header.setText("Ошибка загрузки картинки")
            print(f"Ошибка: {reply.errorString()}")

        reply.deleteLater()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
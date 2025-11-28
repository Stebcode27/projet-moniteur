from PyQt5.QtWidgets import (
    QSplashScreen,
    QLabel,
    QVBoxLayout, QWidget
)
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtCore import Qt, QTimer, QSize

class SplachScreen(QSplashScreen):

    def __init__(self, duration, main_window):
        super().__init__(QPixmap(QSize(500,300)))

        main_layout = QVBoxLayout()

        self.duration = duration
        self.main_window = main_window

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.movie = QMovie("assets/radio.gif")

        if self.movie.isValid():
            self.movie_label = QLabel(self)
            self.movie_label.setMovie(self.movie)
            self.movie_label.setGeometry(0, 0, 500, 300)
            self.movie_label.setAlignment(Qt.AlignCenter)

            self.movie.start()
            main_layout.addWidget(self.movie_label)

            self.loadingLabel = QLabel("Chargement en cours...")
            self.loadingLabel.setAlignment(Qt.AlignCenter)
            self.loadingLabel.setStyleSheet("color: white; font-size: 14pt;")
            main_layout.addWidget(self.loadingLabel)

            container = QWidget(self)
            container.setLayout(main_layout)
            self.resize(QSize(500,300))
            container.setGeometry(self.rect())
        else:
            print("Erreur: Le fichier radio.gif n'a pas pu etre charge ou est invalide")

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.finish_splash)
        self.timer.start(self.duration)

        self.setStyleSheet("background-color: #1B211C; border: 0;")

    def finish_splash(self):
        """Affiche la fenetre et ferme l'écran de chargement"""
        self.main_window.showFullScreen()
        self.finish(self.main_window)

    def closeWindow(self):
        self.main_window.close()
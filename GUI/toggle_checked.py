import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ModernSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.state = False

        # Dimensions et couleurs
        self.setFixedSize(50, 28)
        self._bg_color_off = QColor("#333333")
        self._bg_color_on = QColor("#3d82f6")
        self._circle_color = QColor("white")

        # Position du cercle (animation entre 3 et 25)
        self._circle_pos = 3
        self._anim = QPropertyAnimation(self, b"circle_pos")
        self._anim.setDuration(300)  # 200ms pour la fluidité
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

    # Propriété pour l'animation
    @pyqtProperty(int)
    def circle_pos(self):
        return self._circle_pos

    @circle_pos.setter
    def circle_pos(self, pos):
        self._circle_pos = pos
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)

        # 1. Dessiner le fond (le rail)
        color = self._bg_color_on if self.isChecked() else self._bg_color_off
        p.setBrush(color)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)

        # 2. Dessiner le cercle blanc
        p.setBrush(self._circle_color)
        p.drawEllipse(self._circle_pos, 4, 20, 20)

    def nextCheckState(self):
        # Déclenche l'animation au clic
        super().nextCheckState()
        start = self._circle_pos
        end = self.width() - 24 if self.isChecked() else 4
        self.state = True if self.isChecked() else False
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

    def getstate(self):
        return self.state

# --- Mise en page pour imiter votre capture d'écran ---

class ExampleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paramètres")
        self.setStyleSheet("background-color: black; color: white; font-family: Segoe UI, Arial;")
        self.setFixedWidth(400)

        layout = QVBoxLayout()

        # Widget de sélection "Adaptive brightness"
        layout.addWidget(self.create_settings_row("Adaptive brightness"))

        # Widget de sélection "Eye comfort shield" avec sous-titre
        layout.addWidget(self.create_settings_row("Eye comfort shield", "Always on"))

        layout.addStretch()
        self.setLayout(layout)

    def create_settings_row(self, title, subtitle=None):
        frame = QFrame()
        frame.setStyleSheet("background-color: #1a1a1a; border-radius: 20px;")
        row_layout = QHBoxLayout(frame)
        row_layout.setContentsMargins(20, 15, 20, 15)

        # Texte (Vertical pour Titre + Sous-titre)
        text_layout = QVBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: 400;")
        text_layout.addWidget(lbl_title)

        if subtitle:
            lbl_sub = QLabel(subtitle)
            lbl_sub.setStyleSheet("color: #4a90e2; font-size: 13px;")  # Bleu clair
            text_layout.addWidget(lbl_sub)

        row_layout.addLayout(text_layout)
        row_layout.addStretch()

        # Le Switch
        sw = ModernSwitch()
        row_layout.addWidget(sw)

        return frame


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ExampleWindow()
    win.showFullScreen()
    sys.exit(app.exec_())

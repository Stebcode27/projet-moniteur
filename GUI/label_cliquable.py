from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
import sys
import os
# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

class LabelCliquable(QLabel):

    clique = pyqtSignal()

    def __init__(self, text=None):
        super().__init__()
        if text:
            self.setText(text)
        else:
            settings_icon_path = os.path.join(PROJECT_ROOT, 'assets', 'gear.png')
            pixmap = QPixmap(settings_icon_path)
            self.setPixmap(pixmap)
            self.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

    def mousePressEvent(self, ev):
        if ev.button()==Qt.LeftButton:
            self.clique.emit()

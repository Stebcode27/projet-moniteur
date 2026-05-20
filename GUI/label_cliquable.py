from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
import sys
import os
# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

def resource_path(relative_path):
    """ Récupère le chemin absolu vers la ressource, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Mode Production (.exe) : PyInstaller extrait tout directement dans sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)

    # Mode Développement (PyCharm) : On garde ta logique PROJECT_ROOT actuelle
    # 'dirname(__file__), ".."' permet de remonter au dossier racine du projet
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(PROJECT_ROOT, relative_path)

class LabelCliquable(QLabel):

    clique = pyqtSignal()

    def __init__(self, text=None):
        super().__init__()
        if text:
            self.setText(text)
        else:
            settings_icon_path = resource_path("assets/gear.png")
            pixmap = QPixmap(settings_icon_path)
            self.setPixmap(pixmap)
            self.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

    def mousePressEvent(self, ev):
        if ev.button()==Qt.LeftButton:
            self.clique.emit()

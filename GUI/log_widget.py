import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont, QTextCursor
from utilities.preferences import COLOR_THEME

class LogWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout(self)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)

        self.log.setStyleSheet("color: #00FF00; font-family: Courier New; font-weight: bold")

        self.log.setFont(QFont('Courier New', 10))
        self.log.setMaximumBlockCount(50)
        layout.addWidget(self.log)

    def ajouter_valeur(self):
        from datetime import datetime
        horodatage = datetime.now().strftime("%H:%M:%S")

        message = f"[{horodatage}] PNI: {self.parent.pression.systo}/{self.parent.pression.diasto} ({self.parent.pression.pam})]"
        self.log.appendPlainText(message)
        self.log.moveCursor(QTextCursor.End)
        self.log.setStyleSheet(f"background-color: {COLOR_THEME[self.parent.theme]['container-color']}; color: #00FF00; font-family: Courier New; font-weight: bold")
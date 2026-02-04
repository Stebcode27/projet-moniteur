import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont, QTextCursor
from utilities.preferences import COLOR_THEME

theme = COLOR_THEME['optimized']['container-color']

class LogWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        layout = QVBoxLayout(self)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)

        self.log.setStyleSheet(f"""
            background-color: {theme};
            color: #00FF00;
            font-family: Courier New;
        """)

        self.log.setFont(QFont('Courier New', 10))
        self.log.setMaximumBlockCount(100)
        layout.addWidget(self.log)

    def ajouter_valeur(self, status="Normal"):
        from datetime import datetime
        horodatage = datetime.now().strftime("%H:%M:%S")
        file = os.path.join(PROJECT_ROOT, 'datas', 'base_donnees.txt')
        bpm=''
        with open(file, 'r+') as f:
            line = f.readline()
            debut, fin = '<HR>', '</HR>'
            i, j = line.find(debut)+len(debut), line.find(fin)
            bpm = float(line[i:j].strip()) * 50
            bpm = f"{bpm:.2f}"

        message = f"[{horodatage}] ECG: {bpm} | Etat: {status}]"
        self.log.appendPlainText(message)
        self.log.moveCursor(QTextCursor.End)
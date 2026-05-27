import sys
import os
# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from PyQt5.QtGui import QTextCursor

def add_new_log_text(log_ref, text_to_add="", style=""):
    from datetime import datetime

    horodatage = datetime.now().strftime("%H:%M:%S")

    message = f"[{horodatage}] [{text_to_add}]"
    log_ref.appendPlainText(message)
    log_ref.moveCursor(QTextCursor.End)
    log_ref.setStyleSheet(style)
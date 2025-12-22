"""Ouverture du programme"""

import sys
import os

# Ajouter le dossier racine du projet au path
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from GUI.dashboard import Dashboard
from PyQt5.QtWidgets import QApplication

if __name__=='__main__':
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.showFullScreen()
    sys.exit(app.exec_())
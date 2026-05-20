"""Ouverture du programme"""
import sys
import os

# Ajouter le dossier racine du projet au path
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from GUI.dashboard import Dashboard
from GUI.splash_protocol import HandShakeThread, MonitorSplash
from PyQt5.QtWidgets import QApplication

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(PROJECT_ROOT, relative_path)

def main():
    dashboard = Dashboard()
    dashboard.showFullScreen()

if __name__=='__main__':
    app = QApplication(sys.argv)

    splash = MonitorSplash()
    splash.handshaker.connection_established.connect(main)
    splash.show()

    sys.exit(app.exec_())
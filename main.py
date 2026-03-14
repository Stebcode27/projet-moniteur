"""Ouverture du programme"""

import sys
import os

# Ajouter le dossier racine du projet au path
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from GUI.dashboard import Dashboard
from GUI.splash_protocol import HandShakeThread, MonitorSplash
from PyQt5.QtWidgets import QApplication

if __name__=='__main__':
    app = QApplication(sys.argv)

    splash = MonitorSplash()
    splash.show()

    def main():
        dashboard = Dashboard()
        dashboard.showFullScreen()
        splash.close()

    comm_protocol = HandShakeThread()
    comm_protocol.connection_established.connect(main)
    comm_protocol.progression.connect(splash.update_progress)
    comm_protocol.error_occured.connect(lambda msg: print(f"Alerte: {msg}"))
    comm_protocol.start()

    sys.exit(app.exec_())
import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from PyQt5.QtCore import QThread, pyqtSignal

class SurveillanceThread(QThread):
    # Signal envoyé lorsqu'une alerte est détectée ou modifiée
    # Envoie le nom du paramètre et un booléen (True si alerte)
    alerte_detectee = pyqtSignal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.running = True

    def run(self):
        while self.running:
            from utilities.preferences import PARAMS_SEUILS

            hr_alerte = not (PARAMS_SEUILS[0]['val_min'] <= self.parent.ecg.bpm <= PARAMS_SEUILS[0]['val_max'])
            self.alerte_detectee.emit("hr", hr_alerte)

            sat_alerte = not (PARAMS_SEUILS[1]['val_min'] <= self.parent.saturation.spo2_val < 100)
            self.alerte_detectee.emit("spo2", sat_alerte)

            resp_alerte = not (PARAMS_SEUILS[3]['val_min'] <= self.parent.respiration.rpm <= PARAMS_SEUILS[3]['val_max'])
            self.alerte_detectee.emit("resp", resp_alerte)

            temp_alerte = not (PARAMS_SEUILS[4]['val_min'] <= self.parent.temperature.temperature <= PARAMS_SEUILS[4]['val_max'])
            self.alerte_detectee.emit("temp", temp_alerte)

            self.msleep(10)

    def set_running(self, running):
        self.running = running

    def get_running(self):
        return self.running
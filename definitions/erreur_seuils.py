import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from PyQt5.QtCore import QThread, pyqtSignal

def resource_path(relative_path):
    """ Récupère le chemin absolu vers la ressource, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Mode Production (.exe) : PyInstaller extrait tout directement dans sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)

    # Mode Développement (PyCharm) : On garde ta logique PROJECT_ROOT actuelle
    # 'dirname(__file__), ".."' permet de remonter au dossier racine du projet
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(PROJECT_ROOT, relative_path)

class SurveillanceThread(QThread):
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

            temp_alerte = not (PARAMS_SEUILS[4]['val_min'] <= self.parent.temperature.temperature if not self.parent.simul_state else self.parent.temperature.value <= PARAMS_SEUILS[4]['val_max'])
            self.alerte_detectee.emit("temp", temp_alerte)

            self.msleep(10)

    def set_running(self, running):
        self.running = running

    def get_running(self):
        return self.running
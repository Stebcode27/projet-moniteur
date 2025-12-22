"""Definition de tous les seuils des paramètres pour la gestion des erreurs"""
import sys
import os

# Obtenir le chemin absolu du dossier racine du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QApplication, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from utilities.ecran import get_screen_dimensions

nbr_params = 5

ENUM_LIST_SEUILS = [5 for i in range(nbr_params)]

class ParamError(QDialog):

    def __init__(self, param_name='hr', details="rien à signaler", freq=500, parent=None):
        self.details = details
        self.param_name = param_name
        self.message = f"Le paramètre {self._get_name_param_(param_name)} n'est pas correct!"
        super().__init__(parent)

        self.state = True
        self.timer = QTimer(self)

        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close)
        self.timer.start(5000)

        self.details_lab = QLabel(self)
        self.details_lab.setText(self.details)
        self.details_lab.setAlignment(Qt.AlignCenter)

        self.buildBox()

        self.configure_text_color()

        self.buildUI()

    def _get_name_param_(self, param):
        if param=='hr':
            return "frequence respiratoire"
        elif param=='pni':
            return "pression artérielle"
        elif param=='temp':
            return "temperature"
        elif param=='resp':
            return "frequence respiratoire"
        else:
            return "saturation en oxygene"

    def cacher(self):
        if self.state:
            self.hide()
            self.state = False
        else:
            self.show()
            self.state = True

    def _set_message_(self, mess):
        self.message = mess
    def _get_param_value_(self):
        return self.param_value

    def configure_text_color(self):
        dict_params = {
           'hr': '#33FF57',
           'sat': '#FF500A',
           'pni': '#fbfbfb',
           'temp': "#2093FF",
           'resp': '#DFEE0A'
        }
        if self.param_name in dict_params:
            self.color = dict_params[self.param_name]

    def buildBox(self):
        screen_dims = get_screen_dimensions()
        largeur = screen_dims['width']
        hauteur = screen_dims['height']

        w_app = int(largeur * 0.4)#largeur 40%
        h_app = int(hauteur * 0.1)#hauteur 5%

        self.resize(w_app, h_app)

        x_pos = int(largeur * (1 - 0.3) - w_app)

        self.move(x_pos, 50)

    def buildUI(self):
        self.box_layout = QVBoxLayout()
        self.box_layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.details_lab.setStyleSheet("font-weight: normal; font-size: 12pt")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.label.setText(self.message)
        self.setStyleSheet(f"font-size: 15pt; font-weight: bold; background-color: {self.color}; font-family: roboto; padding: 20px;")
        self.box_layout.addWidget(self.label, stretch=2)
        self.box_layout.addStretch(1)
        self.box_layout.addWidget(self.details_lab, stretch=2)

        self.setLayout(self.box_layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    param = ParamError('temp')
    param.show()
    sys.exit(app.exec_())

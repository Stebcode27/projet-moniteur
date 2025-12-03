"""Definition de tous les seuils des paramètres pour la gestion des erreurs"""
import sys
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QApplication, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from utilities.ecran import get_screen_dimensions

nbr_params = 5

ENUM_LIST_SEUILS = [5 for i in range(nbr_params)]

class ParamError(QDialog):
    def __init__(self, param_name, parent=None):
        self.param_name = param_name
        self.message = f"Le paramètre {self.param_name} n'est pas correct!"
        super().__init__(parent)

        self.state = False

        self.buildBox()

        self.configure_text_color()

        self.buildUI()

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
           'temp': '#3020FF',
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

        self.move(x_pos, 5)

    def buildUI(self):
        self.box_layout = QVBoxLayout()
        self.box_layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.label.setText(self.message)
        self.setStyleSheet(f"font-size: 15pt; font-weight: bold; background-color: {self.color}; font-family: roboto; padding: 20px;")
        self.box_layout.addWidget(self.label, stretch=2)
        self.box_layout.addStretch(1)
        self.close_button = QPushButton(self)
        self.close_button.setStyleSheet('font-size: 12pt; padding: 5px')
        self.close_button.setText('Close')
        self.close_button.clicked.connect(self.close)
        self.box_layout.addWidget(self.close_button, stretch=1)

        self.setLayout(self.box_layout)

if __name__ == '__main__':
    app = QApplication([])
    param = ParamError('resp')
    param.show()
    sys.exit(app.exec_())

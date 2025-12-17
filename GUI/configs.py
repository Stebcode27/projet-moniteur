import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, 
                             QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, 
                             QComboBox, QDialogButtonBox, QGroupBox)
from PyQt5.QtCore import Qt

from utilities.ecran import get_screen_dimensions


class ConfigBox(QDialog):

    def __init__(self, parent=None):
        super(ConfigBox, self).__init__(parent)

        self.setWindowTitle("Configuration")

        self.buildUI()

    def buildUI(self):
        screen = get_screen_dimensions()
        largeur = screen['width']
        hauteur = screen['height']

        box_height = int(hauteur * 0.7)
        box_width = int(largeur * 0.4)

        self.resize(box_width, box_height)

        x_pos = int(largeur * (1 - 0.3) - box_width)
        y_pos = int(hauteur * (1 - 0.15) - box_height)

        self.move(x_pos, y_pos)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ConfigBox()
    win.show()
    sys.exit(app.exec_())
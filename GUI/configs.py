from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                             QFrame, QDialogButtonBox, QComboBox, QSlider, QLabel)
from PyQt5.QtCore import Qt
import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from utilities.ecran import get_screen_dimensions
from utilities.preferences import COLOR_THEME
from GUI.toggle_checked import ModernSwitch

THEME =  COLOR_THEME['solar']['app-color']


class ConfigBox(QDialog):

    def __init__(self, parent=None):
        super(ConfigBox, self).__init__(parent)

        self.setWindowTitle("Configuration")

        self.buildUI()

        style = """
            QDialog {
                background: qlineargradient(
                    x1:0, y1:1, x2:1, y2:0,
                    stop: 0 #FFFFFF,
                    stop: 0.5 #10440E13,
                    stop: 0.501 #10440E3D,
                    stop: 1 #FFFFFF
                );
            }
        """
        self.simul = False
        self.theme_selected = None
        self.components()

    def buildUI(self):
        screen = get_screen_dimensions()
        largeur = screen['width']
        hauteur = screen['height']

        box_height = int(hauteur * 0.5)
        box_width = int(largeur * 0.6)

        self.resize(box_width, box_height)

        x_pos = int(largeur * (1 - 0.2) - box_width)
        y_pos = int(hauteur * (1 - 0.25) - box_height)

        self.move(x_pos, y_pos)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def components(self):
        main_layout = QVBoxLayout()
        layout_tab = QHBoxLayout()
        gauche_lay = QVBoxLayout()
        droite_lay = QVBoxLayout()
        
        layout_tab.addStretch(1)

        gauche_lay.addWidget(self.create_settings_row('Simulation', subtitle='Lancer l\'état de simulation de l\'appareil'))
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(10)
        self.slider.setMaximum(25)
        self.slider.setValue(10)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.modifie_slide)
        gauche_lay.addWidget(self.create_settings_row_with_widget('Taille de Police', self.slider))
        gauche_lay.addStretch()
        
        self.theme = QComboBox()
        for th in COLOR_THEME.keys():
            self.theme.addItem(th)
        self.theme.setStyleSheet("padding: 5px; border-radius: 5px; border: 0.5px solid black; font-size: 12pt")
        droite_lay.addWidget(self.create_settings_row("Thème", widget=self.theme))
        droite_lay.addStretch()


        self.boutons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.boutons.accepted.connect(self.accept)
        self.boutons.rejected.connect(self.reject)

        layout_tab.addLayout(gauche_lay, stretch=2)
        layout_tab.addStretch(1)
        layout_tab.addLayout(droite_lay, stretch=2)
        layout_tab.addStretch(1)

        main_layout.addLayout(layout_tab)
        
        main_layout.addWidget(self.boutons, stretch=2, alignment=Qt.AlignBottom)
        self.setLayout(main_layout)
    
    def modifie_slide(self):
        self.slide_lab_val.setText(str(self.slider.value()))
        style="""
            QLabel{
                font-size: {self.slider.value()}pt
            }
        """
        self.setStyleSheet(style)

    def getThemeSelected(self):
        return self.theme.currentText()
    
    def create_settings_row(self, title, subtitle=None, widget=None):
        frame = QFrame()
        frame.setStyleSheet("background-color: #dddddd; border-radius: 20px;")
        row_layout = QHBoxLayout(frame)
        row_layout.setContentsMargins(20, 20, 20, 20)

        # Texte (Vertical pour Titre + Sous-titre)
        text_layout = QVBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 16pt; font-weight: 400;")
        text_layout.addWidget(lbl_title)

        if subtitle:
            lbl_sub = QLabel(subtitle)
            lbl_sub.setStyleSheet("color: #4a90e2; font-size: 10pt;")  # Bleu clair
            text_layout.addWidget(lbl_sub)

        row_layout.addLayout(text_layout)
        row_layout.addStretch()

        # Le Switch
        if not widget:
            sw = ModernSwitch()
            sw.clicked.connect(self.set_state)
            row_layout.addWidget(sw)
        else:
            row_layout.addWidget(widget)

        return frame
    
    def create_settings_row_with_widget(self, title, widget=None, subtitle=None):
        frame = QFrame()
        frame.setStyleSheet("background-color: #dddddd; border-radius: 20px;")
        row_layout = QHBoxLayout(frame)
        row_layout.setContentsMargins(20, 20, 20, 20)

        text_layout = QVBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 16pt; font-weight: 400;")
        text_layout.addWidget(lbl_title)

        if subtitle:
            lbl_sub = QLabel(subtitle)
            lbl_sub.setStyleSheet("color: #4a90e2; font-size: 10pt;")  # Bleu clair
            text_layout.addWidget(lbl_sub)

        row_layout.addLayout(text_layout)
        row_layout.addStretch()

        value_lay = QVBoxLayout()
        self.slide_lab_val = QLabel()
        self.slide_lab_val.setText(str(self.slider.minimum()))
        value_lay.addWidget(self.slide_lab_val)

        # Le Slider
        if widget:
            value_lay.addWidget(widget)
        row_layout.addLayout(value_lay)

        return frame

    def set_state(self):
        if self.simul:
            self.simul = False
        else:
            self.simul = True
    def get_state(self):
        return self.simul

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ConfigBox()
    win.show()
    sys.exit(app.exec_())
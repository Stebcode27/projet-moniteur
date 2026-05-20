from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                             QFrame, QDialogButtonBox, QComboBox, QSlider, QLabel, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from utilities.ecran import get_screen_dimensions
from utilities.preferences import COLOR_THEME
from GUI.toggle_checked import ModernSwitch

THEME =  COLOR_THEME['Solar']['app-color']

def resource_path(relative_path):
    """ Récupère le chemin absolu vers la ressource, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Mode Production (.exe) : PyInstaller extrait tout directement dans sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)

    # Mode Développement (PyCharm) : On garde ta logique PROJECT_ROOT actuelle
    # 'dirname(__file__), ".."' permet de remonter au dossier racine du projet
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(PROJECT_ROOT, relative_path)

class ConfigBox(QDialog):

    def __init__(self, parent=None, state=False):
        super(ConfigBox, self).__init__(parent)

        self.setWindowTitle("Configuration")

        self.buildUI()

        self.fichier_style = resource_path('utilities/style_config.qss')
        self.load_style()

        self.parent = parent

        self.simul = False
        self.theme_selected = None
        self.components()

    def buildUI(self):
        screen = get_screen_dimensions()
        largeur = screen['width']
        hauteur = screen['height']

        box_width = int(largeur * 0.5)
        box_height = int(hauteur * 0.4)

        self.resize(box_width, box_height)

        x_pos = int(largeur * (1 - 0.25) - box_width)
        y_pos = int(hauteur * (1 - 0.3) - box_height)

        self.move(x_pos, y_pos)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)

    def components(self):
        main_layout = QVBoxLayout()
        layout_tab = QHBoxLayout()
        gauche_lay = QVBoxLayout()
        droite_lay = QVBoxLayout()
        
        layout_tab.addStretch(1)

        gauche_lay.addWidget(self.create_settings_row('Simulation', subtitle='Lancer le Mode Démo'))
        gauche_lay.addStretch(1)
        
        self.theme = QComboBox()
        for th in COLOR_THEME.keys():
            self.theme.addItem(th)
        self.theme.setStyleSheet("background: white; padding: 10px; border-radius: 5px; border: 0.5px solid black; font-size: 13pt")
        droite_lay.addWidget(self.create_settings_row("Thème", subtitle="Selectionnez le theme \nqui vous convient le mieux", widget=self.theme))
        #droite_lay.addStretch()

        self.boutons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.boutons.accepted.connect(self.accept)
        self.boutons.rejected.connect(self.reject)

        layout_tab.addLayout(gauche_lay, stretch=2)
        layout_tab.addStretch(1)
        layout_tab.addLayout(droite_lay, stretch=2)
        layout_tab.addStretch(1)

        self.close_session_frame = QFrame(self)
        self.close_session_frame.setContentsMargins(0,0,0,0)
        button_close = QPushButton("Arreter la session en cours")
        button_close.setObjectName("close-btn")

        button_close.clicked.connect(self.verify_and_close)

        layout = QHBoxLayout(self.close_session_frame)
        layout.addStretch(1)
        layout.addWidget(button_close, stretch=3)
        layout.addStretch(1)

        main_layout.addLayout(layout_tab, stretch=2)

        main_layout.addStretch(2)

        main_layout.addWidget(self.close_session_frame, stretch=1)
        
        main_layout.addWidget(self.boutons, stretch=2, alignment=Qt.AlignBottom)
        self.setLayout(main_layout)

    def load_style(self):

        try:
            with open(self.fichier_style, 'r', encoding="utf-8") as f:
                style = f.read()

                self.setStyleSheet(style)
        except FileNotFoundError:
            print("Le fichier spécifié est introuvable")

    def verify_and_close(self):
        mess = QMessageBox()
        mess.setIcon(QMessageBox.Information)
        mess.setText("Voulez vous vraiment fermer la session en cours ?")
        mess.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        mess.setWindowTitle("Confirmation")
        mess.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        mess.setDefaultButton(QMessageBox.No)
        if mess.exec_() == QMessageBox.Yes:
            if self.parent:
                self.parent.close_monitor_session()

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
        lbl_title.setStyleSheet("font-size: 14pt; font-weight: 400;")
        text_layout.addWidget(lbl_title)

        if subtitle:
            lbl_sub = QLabel(subtitle)
            lbl_sub.setStyleSheet("color: #4a90e2; font-size: 10pt;")  # Bleu clair
            text_layout.addWidget(lbl_sub)

        row_layout.addLayout(text_layout)
        row_layout.addStretch()

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
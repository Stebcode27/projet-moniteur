import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog, QVBoxLayout, 
                             QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, 
                             QComboBox, QDialogButtonBox, QGroupBox, QLabel, QPushButton)
from PyQt5.QtCore import Qt
from utilities.ecran import get_screen_dimensions
from definitions.clavier_visuel import ClavierVisuel

class FenetrePatient(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Patient")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)

        self.buildScreen()
        main_layout = QVBoxLayout()
        
        self.groupe_identite = QGroupBox("Identité")
        self.groupe_identite.setStyleSheet('padding: 15px;')
        form_identite = QFormLayout()
        
        self.champ_nom = QLineEdit()
        #
        self.champ_nom.setPlaceholderText("ex: DOE John")
        self.champ_nom.setStyleSheet("padding: 5px; border-radius: 5px; border: 0.5px solid white;")
        
        self.champ_id = QLineEdit()
        self.champ_id.setPlaceholderText("ex: 123456")
        self.champ_id.setStyleSheet("padding: 5px; border-radius: 5px; border: 0.5px solid white;")
        
        self.champ_age = QSpinBox()
        self.champ_age.setRange(0, 120)
        self.champ_age.setSuffix(" ans")
        self.champ_age.setStyleSheet("border-radius: 5px; border: 0.5px solid white;")
        
        self.champ_sexe = QComboBox()
        self.champ_sexe.addItems(["Masculin", "Féminin", "Autre"])
        self.champ_sexe.setStyleSheet("padding: 5px; border-radius: 5px; border: 0.5px solid white;")

        self.champ_salle = QLineEdit()
        self.champ_salle.setPlaceholderText("ex: Salle 2")
        self.champ_salle.setStyleSheet("padding: 5px; border-radius: 5px; border: 0.5px solid white;")

        form_identite.addRow("Nom complet :", self.champ_nom)
        form_identite.addRow("ID Patient :", self.champ_id)
        form_identite.addRow("Âge :", self.champ_age)
        form_identite.addRow("Sexe :", self.champ_sexe)
        form_identite.addRow("Salle :", self.champ_salle)
        
        self.groupe_identite.setLayout(form_identite)
        main_layout.addWidget(self.groupe_identite, stretch=2)
        main_layout.addStretch()

        self.groupe_physique = QGroupBox("Données Physiques")
        self.groupe_physique.setStyleSheet('padding: 15px;')
        form_physique = QFormLayout()
        
        self.champ_poids = QDoubleSpinBox()
        self.champ_poids.setRange(0, 300)
        self.champ_poids.setSuffix(" kg")
        self.champ_poids.setStyleSheet("border-radius: 5px; border: 0.5px solid white;")
        
        self.champ_taille = QDoubleSpinBox()
        self.champ_taille.setRange(0, 2.50)
        self.champ_taille.setSingleStep(0.1)
        self.champ_taille.setSuffix(" m")
        self.champ_taille.setStyleSheet("border-radius: 5px; border: 0.5px solid white;")
        
        form_physique.addRow("Poids :", self.champ_poids)
        form_physique.addRow("Taille :", self.champ_taille)
        
        self.groupe_physique.setLayout(form_physique)
        main_layout.addWidget(self.groupe_physique)

        self.boutons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.boutons.accepted.connect(self.accept)
        self.boutons.rejected.connect(self.reject)
        
        main_layout.addWidget(self.boutons, stretch=2)
        self.setLayout(main_layout)

    def ouvrir_clavier(self, line_edit, event):
        if event.button() == Qt.LeftButton:
            clavier = ClavierVisuel(line_edit.text())
            pos = line_edit.mapToGlobal(line_edit.rect().bottomLeft())
            clavier.move(pos)
            clavier.exec_()

    def buildScreen(self):
        screen_dims = get_screen_dimensions()
        largeur = screen_dims['width']
        hauteur = screen_dims['height']

        w_app = int(largeur * 0.5)
        h_app = int(hauteur * 0.5)

        self.resize(w_app, h_app)

        x_pos = int(largeur * (1 - 0.25) - w_app)
        y_pos = int(hauteur * (1 - 0.25) - h_app)

        self.setStyleSheet(f"font-size: 10pt; background-color: #2b3245; color: white;")

        self.move(x_pos, y_pos)

    def get_data(self):
        return {
            "nom": self.champ_nom.text(),
            "id": self.champ_id.text(),
            "age": self.champ_age.value(),
            "sexe": self.champ_sexe.currentText(),
            "poids": self.champ_poids.value(),
            "taille": self.champ_taille.value(),
            "salle": self.champ_salle.text()
        }

if __name__ == "__main__":
    app = QApplication(sys.argv)
    patient = FenetrePatient()
    patient.show()
    sys.exit(app.exec_())

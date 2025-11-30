import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog, QVBoxLayout, 
                             QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, 
                             QComboBox, QDialogButtonBox, QGroupBox, QLabel, QPushButton)
from PyQt5.QtCore import Qt

class FenetrePatient(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Patient")
        self.resize(800, 500)
        
        main_layout = QVBoxLayout()
        
        self.groupe_identite = QGroupBox("Identité et Démographie")
        form_identite = QFormLayout()
        
        self.champ_nom = QLineEdit()
        self.champ_nom.setPlaceholderText("ex: DOE John")
        
        self.champ_id = QLineEdit()
        self.champ_id.setPlaceholderText("ex: 123456")
        
        self.champ_age = QSpinBox()
        self.champ_age.setRange(0, 120)
        self.champ_age.setSuffix(" ans")
        
        self.champ_sexe = QComboBox()
        self.champ_sexe.addItems(["Masculin", "Féminin", "Autre"])
        
        form_identite.addRow("Nom complet :", self.champ_nom)
        form_identite.addRow("ID Patient :", self.champ_id)
        form_identite.addRow("Âge :", self.champ_age)
        form_identite.addRow("Sexe :", self.champ_sexe)
        
        self.groupe_identite.setLayout(form_identite)
        main_layout.addWidget(self.groupe_identite)
        

        self.groupe_physique = QGroupBox("Données Physiques")
        form_physique = QFormLayout()
        
        self.champ_poids = QDoubleSpinBox()
        self.champ_poids.setRange(0, 300)
        self.champ_poids.setSuffix(" kg")
        
        self.champ_taille = QDoubleSpinBox()
        self.champ_taille.setRange(0, 2.50)
        self.champ_taille.setSingleStep(0.01)
        self.champ_taille.setSuffix(" m")
        
        form_physique.addRow("Poids :", self.champ_poids)
        form_physique.addRow("Taille :", self.champ_taille)
        
        self.groupe_physique.setLayout(form_physique)
        main_layout.addWidget(self.groupe_physique)

        self.boutons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.boutons.accepted.connect(self.accept)
        self.boutons.rejected.connect(self.reject)
        
        main_layout.addWidget(self.boutons)
        self.setLayout(main_layout)

    def get_data(self):
        return {
            "nom": self.champ_nom.text(),
            "id": self.champ_id.text(),
            "age": self.champ_age.value(),
            "sexe": self.champ_sexe.currentText(),
            "poids": self.champ_poids.value(),
            "taille": self.champ_taille.value()
        }

import sys

from PyQt5.QtWidgets import (QApplication, QComboBox, QLabel, QPushButton, QVBoxLayout, QWidget, QMainWindow, QLineEdit, QHBoxLayout,
                             QGroupBox,
                             QRadioButton,
                             )


class PatientInfosApp(QMainWindow):
    def __init__(self):
        super(PatientInfosApp, self).__init__()
        self.setGeometry(300, 300, 800, 550)
        self.initUI()

        self.style_edits = "font-size: 25px; border-radius: 5px; height: 50px; padding: 10px;"

        self.initStyles()

    def initUI(self):
        self.setWindowTitle("Patient Infos")
        self.setStyleSheet("font-family: Arial;")
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.layout_app = QHBoxLayout(self.centralwidget)
        self.layout_app.addStretch()
        self.layout_app.setContentsMargins(50, 100, 50, 100)

        self.group_box_names = QGroupBox("Patient")
        self.layout_names = QVBoxLayout(self.group_box_names)

        self.nom = QLineEdit(self)
        self.nom.setPlaceholderText("Nom du patient")
        self.prenom = QLineEdit(self)
        self.prenom.setPlaceholderText("Prenom du patient")
        self.age = QLineEdit(self)
        self.age.setPlaceholderText("Age du patient")

        self.layout_names.addWidget(self.nom, stretch=1)
        self.layout_names.addWidget(self.prenom, stretch=1)
        self.layout_names.addWidget(self.age, stretch=1)

        self.group_box_names.setLayout(self.layout_names)

        self.infos_perso = QVBoxLayout(self.centralwidget)
        self.infos_perso.addWidget(self.group_box_names, stretch=1)
        self.infos_perso.addStretch()

        self.infos_sup = QVBoxLayout(self.centralwidget)
        options = ["0-5 Kg", "6-20 Kg", "21-45 Kg", "46-90 Kg", "91-150 Kg"]
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(options)
        self.combo_box.setCurrentIndex(0)
        self.infos_sup.addWidget(self.combo_box)

        self.groupBox = QGroupBox("Sexe du patient", self)
        layout_radio = QHBoxLayout()
        self.masculin = QRadioButton("Masculin")
        self.feminin = QRadioButton("Feminin")
        layout_radio.addWidget(self.masculin)
        layout_radio.addWidget(self.feminin)

        self.groupBox.setLayout(layout_radio)
        self.infos_perso.addWidget(self.groupBox)

        self.layout_app.addLayout(self.infos_perso)
        self.infos_perso.addStretch()
        self.layout_app.addStretch()
        self.layout_app.addLayout(self.infos_sup)
        self.layout_app.addStretch()
        self.centralwidget.setLayout(self.layout_app)

    def initStyles(self):
        self.nom.setStyleSheet(self.style_edits)
        self.prenom.setStyleSheet(self.style_edits)
        self.combo_box.setStyleSheet(self.style_edits)
        self.age.setStyleSheet(self.style_edits)
        self.masculin.setStyleSheet(self.style_edits)
        self.feminin.setStyleSheet(self.style_edits)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    patient = PatientInfosApp()
    patient.show()
    sys.exit(app.exec_())
import sys
import os
# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QWidget, QPushButton, QMessageBox, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QHBoxLayout, QDialogButtonBox
from PyQt5.QtCore import Qt
from utilities.ecran import get_screen_dimensions

class AdmissionPatient(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Patients')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.layout = QVBoxLayout()
        self.resize(800, 600)

        self.patient_list = []

        self.top_widget = QWidget()
        main_layout = QVBoxLayout(self.top_widget)
        label_top = QLabel("Admission Patient")
        label_top.setStyleSheet("font-family: Arial; font-size: 16pt;")
        label_content = QLabel("Vous êtes sur le point de quitter l'examen actuel pour en commencer un nouveau, est ce bien ce que vous voulez ?")
        label_content.setContentsMargins(10,10,10,10)
        label_content.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(label_top)
        main_layout.addWidget(label_content)

        self.layout.addWidget(self.top_widget)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(['Nom', 'ID', 'Date', 'Salle', 'Service'])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0,250)

        self.get_list_next_patient()

        for patient in self.patient_list:
            self.add_item(patient['nom'], patient['id'], patient['date'], patient['salle'], patient['service'])

        self.layout.addWidget(self.tree)
        self.buildUI()

        self.boutons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.boutons.accepted.connect(self.accept)
        self.boutons.rejected.connect(self.reject)

        self.layout.addWidget(self.boutons)

        self.setLayout(self.layout)

    def get_list_next_patient(self):
        file_path = os.path.join(PROJECT_ROOT, 'datas', 'last_exams.txt')
        lines = None
        with open(file_path, 'r') as file:
            lines = file.readlines()
        for line in lines:
            datas = line.split('_')  # nom, id, date, salle, service
            last_pat = {
                'nom': datas[0],
                'id': datas[1],
                'date': datas[2],
                'salle': datas[3],
                'service': datas[4]
            }
            self.patient_list.append(last_pat)

    def buildUI(self):
        screen = get_screen_dimensions()
        largeur = screen['width']
        hauteur = screen['height']

        box_width = int(largeur * 0.5)
        box_height = int(hauteur * 0.5)

        self.resize(box_width, box_height)

        x_pos = int(largeur * (1 - 0.25) - box_width)
        y_pos = int(hauteur * (1 - 0.25) - box_height)

        self.move(x_pos, y_pos)

    def add_item(self, nom, id, date, salle, service):
        item = QTreeWidgetItem([nom, id, date, salle, service])
        self.tree.addTopLevelItem(item)


if __name__=='__main__':
    app = QApplication(sys.argv)
    adp = AdmissionPatient()
    adp.show()
    sys.exit(app.exec_())
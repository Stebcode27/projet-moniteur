import sys
import os
# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QWidget, QPushButton, QMessageBox, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QHBoxLayout, QDialogButtonBox
from PyQt5.QtCore import Qt, pyqtSignal
from utilities.ecran import get_screen_dimensions

def resource_path(relative_path):
    """ Récupère le chemin absolu vers la ressource, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Mode Production (.exe) : PyInstaller extrait tout directement dans sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)

    # Mode Développement (PyCharm) : On garde ta logique PROJECT_ROOT actuelle
    # 'dirname(__file__), ".."' permet de remonter au dossier racine du projet
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(PROJECT_ROOT, relative_path)

class AdmissionPatient(QDialog):

    admit = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle('Admission Patient')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.setMinimumSize(1000,600)
        #self.setMaximumSize(900,400)

        self.patient_list = []
        self.admettre_nouveau = False
        self.code = None

        self.top_widget = QWidget()
        main_layout = QVBoxLayout(self.top_widget)
        label_content = QLabel("Liste des derniers examens")
        label_content.setStyleSheet("font-size: 15pt")
        question = QLabel("Commencer une nouvelle session ? ")
        question.setStyleSheet("font-size: 12pt; font-weight: bold")

        explain = QLabel("Vous pouvez arrêter les processus en cours pour enregistrer un nouveau patient et commencer son monitoring")
        explain.setStyleSheet("font-size: 10pt; font-weight: normal")

        asking = QVBoxLayout()
        asking.addWidget(question, stretch=1)
        asking.addWidget(explain, stretch=2)
        main_layout.addWidget(label_content, stretch=1)


        self.tree = QTreeWidget()
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(['Nom', 'ID', 'Date', 'Salle', 'Service'])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0,150)
        self.tree.setColumnWidth(3, 75)
        self.tree.setColumnWidth(4, 125)

        self.get_list_next_patient()

        for patient in self.patient_list:
            self.add_item(patient['nom'], patient['id'], patient['date'], patient['salle'], patient['service'])


        self.boutons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.boutons.rejected.connect(self.reject)
        self.boutons.accepted.connect(self.confirmation)

        self.layout.addLayout(asking, stretch=1)

        self.layout.addWidget(self.top_widget, stretch=1)
        self.layout.addWidget(self.tree, stretch=2)
        self.layout.addWidget(self.boutons, stretch=1)

        self.setLayout(self.layout)

    def confirmation(self):
        messageBox = QMessageBox()
        messageBox.setText("Etes-vous sur de le faire ?\nCeci conduira à une suppression de l'ensemble des données actuelles")
        messageBox.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        messageBox.setWindowTitle("Confirmation")
        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        messageBox.setDefaultButton(QMessageBox.No)
        if messageBox.exec_() == QMessageBox.Yes:
            if self.parent.count_enregistrement > 0:
                self.admettre_nouveau = True
                self.admit.emit(self.admettre_nouveau)
                self.parent.reset_patient_session()
                self.accept()
            else:
                messagebox = QMessageBox()
                messagebox.setIcon(QMessageBox.Information)
                messagebox.setText("Enregistrez d'abord les données du patient actuel!")
                messagebox.setStandardButtons(QMessageBox.Yes)
                messagebox.setDefaultButton(QMessageBox.Yes)
                messagebox.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
                if messagebox.exec_() == QMessageBox.Yes:
                    self.parent.start_transfert()
                self.accept()
        else:
            self.admettre_nouveau = False
            self.admit.emit(self.admettre_nouveau)
            self.reject()

    def get_list_next_patient(self):
        file_path = resource_path("datas/last_exams.txt")
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

    def new_admission(self):
        print("Patient en cours d'admission")


if __name__=='__main__':
    app = QApplication(sys.argv)
    adp = AdmissionPatient()
    adp.show()
    sys.exit(app.exec_())
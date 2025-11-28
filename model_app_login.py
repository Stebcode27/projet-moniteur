from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout, QLabel, QSizePolicy, \
    QApplication
import json
import sys
import pyqtgraph as pg
from dashboard import Dashboard

class ModelApp(QMainWindow):

    def __init__(self, app):
        super(ModelApp, self).__init__()

        self.app = app
        app.aboutToQuit.connect(self.startApp)
        self.setWindowTitle("Moniteur")

        self.style_edits_good = "padding: 15px; font-size: 25px; color: #ffffff; border-radius: 5px; border: 0.5px solid white;"
        self.style_edits_bad = "padding: 15px; font-size: 25px; color: #ffffff; border-radius: 5px; border: 0.5px solid red;"

        self.initUI()
        self.stylesheet()

        #attributs de connexion
        self.state_login = False

    ###     Getters et Setters      ###
    def getstatelogin(self):
        return self.state_login

    def setstatelogin(self, state):
        self.state_login = state

    ###     Methodes de la classe   ###
    
    def initUI(self):
        """Initialisation de l'interface graphique de l'application"""
        lay = QHBoxLayout()
        layout = QVBoxLayout()

        layout.addStretch(2)

        lab_lay= QHBoxLayout()
        lab_lay.addStretch(3)
        self.label = QLabel(self)
        self.label.setText("Connexion")
        self.label.setStyleSheet("color : #ffffff; font-size : 50px;")
        lab_lay.addWidget(self.label, stretch=2)
        lab_lay.addStretch(3)
        layout.addLayout(lab_lay)

        layout.addStretch(1)

        lay.addStretch()
        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Utilisateur")
        layout.addWidget(self.nom)
        layout.addStretch(1)
        
        self.prenom = QLineEdit()
        self.prenom.setPlaceholderText("Mot de passe")
        layout.addWidget(self.prenom)
        layout.addStretch(1)

        but_layout = QHBoxLayout()

        but_layout.addStretch(1)
        self.button = QPushButton("Se Connecter")
        self.button.clicked.connect(self.login)
        size_policy = self.button.sizePolicy()
        size_policy.setHorizontalStretch(QSizePolicy.Expanding)
        self.button.setSizePolicy(size_policy)
        but_layout.addWidget(self.button, stretch=6)
        but_layout.addStretch(1)

        layout.addLayout(but_layout)
        layout.addStretch(3)
        lay.addLayout(layout)
        lay.addStretch()
        container = QWidget()
        container.setLayout(lay)
        self.setCentralWidget(container)

    def stylesheet(self):
        """Application des styles de la page et des champs"""
        self.setStyleSheet('background-color: #1B211C;')
        self.nom.setStyleSheet(self.style_edits_good)
        self.prenom.setStyleSheet(self.style_edits_good)
        self.button.setStyleSheet("padding: 15px; font-size: 30px; background-color: #0C77CF; color: white; border: none; border-radius: 15px; width: 5%;")

    def login(self):
        """Fonction de connexion et de verification des identifiants fournis"""
        nom = self.nom.text()
        prenom = self.prenom.text()
        if nom == "" or prenom == "":
            print("Erreur de nom")
        users = self.get_user_from_base()
        all_name = []
        for user in users['users']:
            all_name.append(user['nom'])
        all_mdp = []
        for mdp in users['users']:
            all_mdp.append(mdp['mdp'])

        n_state, m_state = False, False

        for n in all_name:
            if nom == n:
                n_state = True
                break

        for m in all_mdp:
            if prenom == m:
                m_state = True
                break

        if n_state and m_state:
            self.nom.setStyleSheet(self.style_edits_good)
            self.prenom.setStyleSheet(self.style_edits_good)
            self.setstatelogin(True)
            self.close()
        else:
            self.bad_id()
            self.shift()
            self.setstatelogin(False)

    def shift(self):
        self.nom.setText('')
        self.prenom.setText('')

    def get_user_from_base(self):
        """recuperation des utilisateurs sur la base de donnees"""
        file_name = "data.json"

        try:
            with open(file_name, 'r') as f:
                data_file = json.load(f)
        except FileNotFoundError:
            data_file = {"users":[]}
        except json.decoder.JSONDecodeError:
            return
        except Exception as e:
            data_file = {"users":[]}

        return data_file

    def bad_id(self):
        """Mauvais identifiants, modification du style des champs"""
        self.nom.setStyleSheet(self.style_edits_bad)
        self.prenom.setStyleSheet(self.style_edits_bad)

    def startApp(self):
        app = QApplication(sys.argv)
        dashboard = Dashboard()
        dashboard.showFullScreen()
        sys.exit(app.exec_())
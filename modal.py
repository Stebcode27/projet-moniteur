from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class CustomModal(QDialog):
    def __init__(self, parent=None, e_color="red"):
        super().__init__(parent)

        # 1. Configuration de la Fenêtre
        self.setWindowTitle("Erreur")
        # Rendre la boîte de dialogue modale :
        # C'est la ligne clé pour le comportement modal
        self.setModal(False)

        # 2. Créer la disposition et les widgets
        layout = QVBoxLayout(self)

        label = QLabel("Ceci est une boîte modale.\nInteragissez ici avant de continuer.")
        label.setStyleSheet(f"font-size: 14pt; padding: 10px; color: {e_color};")

        close_button = QPushButton("Fermer la Modale")
        close_button.setStyleSheet("color: white; font-size: 15px; padding: 10px;")
        close_button.clicked.connect(self.accept)  # Connecter à self.accept() pour fermer

        # 3. Ajouter les widgets à la disposition
        layout.addWidget(label)
        layout.addWidget(close_button)

        # Ajuster la taille de la modale en fonction de son contenu
        self.setLayout(layout)
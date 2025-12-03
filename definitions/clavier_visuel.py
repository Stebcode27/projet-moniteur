import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QPushButton,
                             QLineEdit, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal


class ClavierVisuel(QDialog):
    # Signal pour envoyer le texte construit à la fenêtre parente
    text_changed = pyqtSignal(str)

    def __init__(self, target_line_edit):
        super().__init__()
        self.setWindowTitle("Clavier Visuel")
        self.setWindowFlags(Qt.FramelessWindowHint)  # Optionnel: Sans barre de titre

        # Le champ de saisie que l'on est en train de remplir (dans la fenêtre fille)
        self.cible = target_line_edit
        self.buffer = self.cible.text()  # Buffer pour le texte en cours

        main_layout = QVBoxLayout()

        # Affichage du texte en cours de saisie
        self.display = QLineEdit(self.buffer)
        self.display.setReadOnly(True)
        main_layout.addWidget(self.display)

        # Création des touches
        self.touches = self._creer_touches()
        main_layout.addLayout(self.touches)

        self.setLayout(main_layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()  # Donne le focus à la fenêtre clavier

    def _creer_touches(self):
        layout = QGridLayout()
        # Clavier simplifié (peut être étendu)
        touches = [
            '1', '2', '3', 'A', 'B', 'C',
            '4', '5', '6', 'D', 'E', 'F',
            '7', '8', '9', 'G', 'H', 'I',
            '.', '0', '_', ' ', 'SUPPR', 'OK'
        ]

        self.btn_map = {}  # Pour retrouver les boutons

        positions = [(i, j) for i in range(4) for j in range(6)]

        for position, nom_touche in zip(positions, touches):
            bouton = QPushButton(nom_touche)
            bouton.setFixedSize(60, 40)

            # ⚠️ La connexion au signal standard n'est pas utilisée pour la navigation
            # On utilise uniquement le signal de clic direct pour gérer la souris ou le focus.
            if nom_touche == 'OK':
                bouton.clicked.connect(self.accepter_saisie)
            elif nom_touche == 'SUPPR':
                bouton.clicked.connect(self.supprimer_caractere)
            else:
                bouton.clicked.connect(lambda checked, t=nom_touche: self.ajouter_caractere(t))

            # Important: Activer la navigation au clavier pour chaque bouton
            bouton.setFocusPolicy(Qt.StrongFocus)
            layout.addWidget(bouton, *position)
            self.btn_map[nom_touche] = bouton

        return layout

    def ajouter_caractere(self, char):
        self.buffer += char
        self.display.setText(self.buffer)
        self.text_changed.emit(self.buffer)  # Mise à jour temps réel (optionnel)

    def supprimer_caractere(self):
        self.buffer = self.buffer[:-1]
        self.display.setText(self.buffer)
        self.text_changed.emit(self.buffer)

    def accepter_saisie(self):
        self.cible.setText(self.buffer)
        self.accept()  # Ferme le dialogue avec succès

    def keyPressEvent(self, event):
        key = event.key()
        current_widget = QApplication.focusWidget()  # Le widget qui a le focus (une touche du clavier)

        # Si le focus n'est pas sur un bouton du clavier, ignorer ou le ramener
        if not isinstance(current_widget, QPushButton):
            super().keyPressEvent(event)
            return

        if key == Qt.Key_Right:
            # Demande au système de déplacer le focus au prochain widget (droite)
            self.focusNextChild()
        elif key == Qt.Key_Left:
            # Demande au système de déplacer le focus au widget précédent (gauche)
            self.focusPreviousChild()
        elif key == Qt.Key_Enter or key == Qt.Key_Return:
            # Simule un clic sur la touche sélectionnée
            current_widget.click()
        elif key == Qt.Key_Tab:
            # Le comportement standard de Tabulation est de passer au champ suivant
            # dans la fenêtre parente, ce qui est le comportement souhaité.
            # Ici, nous le laissons se propager (ou vous pouvez simuler un 'OK')
            self.accepter_saisie()

        else:
            # Laisse les autres touches se comporter normalement (ou être ignorées)
            super().keyPressEvent(event)


### B. Gestion de la Navigation (Clavier physique/bouton)
"""
Ceci
est
la
partie
cruciale
pour
la
navigation
"Gauche/Droite/Entrée/Tabulation".

Nous
allons
surcharger
la
méthode
`keyPressEvent`
du
dialogue
pour
intercepter
les
touches.

```python"""


# Ajoutez cette méthode à la classe ClavierVisuel

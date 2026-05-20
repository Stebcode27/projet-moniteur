from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QPushButton,
                             QLineEdit, QVBoxLayout, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from utilities.ecran import get_screen_dimensions
import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

def resource_path(relative_path):
    """ Récupère le chemin absolu vers la ressource, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Mode Production (.exe) : PyInstaller extrait tout directement dans sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)

    # Mode Développement (PyCharm) : On garde ta logique PROJECT_ROOT actuelle
    # 'dirname(__file__), ".."' permet de remonter au dossier racine du projet
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(PROJECT_ROOT, relative_path)

class ClavierVisuel(QDialog):
    # Signal pour envoyer le texte construit à la fenêtre parente
    text_changed = pyqtSignal(str)
    validation_saisie = pyqtSignal()

    def __init__(self, target_line_edit=None, text_box=True):
        super().__init__()
        self.setWindowTitle("Clavier Visuel")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.cible = target_line_edit
        self.setMinimumWidth(800)
        self.setFixedHeight(400)
        self.set_position()
        self.text_box = text_box
        if self.text_box:
            self.buffer = self.cible.text()  # Buffer pour le texte en cours
        else:
            self.buffer = self.cible.value()
        self.state_casse = False

        self.main_layout = QVBoxLayout()

        # Affichage du texte en cours de saisie
        self.display = QLineEdit(self.buffer)
        self.display.setReadOnly(True)
        self.main_layout.addWidget(self.display)

        # Création des touches
        self.touches = self._creer_touches()
        self.main_layout.addLayout(self.touches)

        lay = QHBoxLayout()

        space = QPushButton('ESPACE')
        space.setFixedSize(500, 70)
        space.clicked.connect(lambda checked, t=' ': self.ajouter_caractere(t))
        space.setFocusPolicy(Qt.StrongFocus)
        #pos = (4, 3)
        lay.addWidget(space)

        self.sup_button = QPushButton('SUPPR')
        self.sup_button.setFixedSize(250,70)
        self.sup_button.clicked.connect(self.supprimer_caractere)
        self.sup_button.setFocusPolicy(Qt.StrongFocus)
        lay.addWidget(self.sup_button)

        self.ok = QPushButton('OK')
        self.ok.setFixedSize(150, 70)
        self.ok.clicked.connect(self.accepter_saisie)
        self.ok.setFocusPolicy(Qt.StrongFocus)
        lay.addWidget(self.ok)

        self.main_layout.addLayout(lay)

        self.setLayout(self.main_layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()  # Donne le focus à la fenêtre clavier
        #self.buildUI()

        self.setStyleSheet("font-size: 14pt")

    def set_position(self):
        point_gauche = self.cible.rect().bottomLeft()
        point_global = self.cible.mapToGlobal(point_gauche)

        self.move(int(point_global.x() - (self.width() / 2)), point_global.y() + 5)

    def set_target(self, new_target):
        self.cible = new_target
        self.set_position()
        # Déterminer si c'est un champ texte ou numérique
        self.text_box = isinstance(new_target, QLineEdit)
        
        # Mettre à jour le buffer avec la valeur actuelle du champ
        if self.text_box:
            self.buffer = self.cible.text()
        else:
            self.buffer = str(self.cible.value())
            
        # Mettre à jour l'affichage visuel du clavier
        self.display.setText(self.buffer)

    def _creer_touches(self):
        layout = QGridLayout()
        # Clavier simplifié (peut être étendu)
        touchs = "0123456789AZERTYUIOPQSDFGHJKLMWXCVBN.,"
        tab_touch=[]
        for i in touchs:
            tab_touch.append(i.lower())
        tab_touch.append('MAJ')

        self.btn_map = {}  # Pour retrouver les boutons

        positions = [(i, j) for i in range(4) for j in range(10)]

        for position, nom_touche in zip(positions, tab_touch):
            bouton = QPushButton()
            bouton.setText(nom_touche)
            bouton.setFixedHeight(60)

            # ⚠️ La connexion au signal standard n'est pas utilisée pour la navigation
            # On utilise uniquement le signal de clic direct pour gérer la souris ou le focus.
            if nom_touche == 'MAJ':
                bouton.clicked.connect(self.change_casse)
                bouton.setFixedWidth(280)
            else:
                bouton.clicked.connect(lambda checked, t=nom_touche: self.ajouter_caractere(t))

            # Important: Activer la navigation au clavier pour chaque bouton
            bouton.setFocusPolicy(Qt.StrongFocus)
            layout.addWidget(bouton, *position)
            if nom_touche != "MAJ":
                self.btn_map[nom_touche] = bouton

        return layout

    def change_casse(self):
        if not self.state_casse:
            for button in self.btn_map.values():
                button.setText(button.text().upper())
            self.state_casse = True
        else:
            for button in self.btn_map.values():
                button.setText(button.text().lower())
            self.state_casse = False

    def ajouter_caractere(self, char):
        if self.state_casse:
            self.buffer += char.upper()
        else:
            self.buffer += char.lower()
        self.display.setText(self.buffer)
        self.text_changed.emit(self.buffer)  # Mise à jour temps réel (optionnel)

    def supprimer_caractere(self):
        self.buffer = self.buffer[:-1]
        self.display.setText(self.buffer)
        self.text_changed.emit(self.buffer)

    def accepter_saisie(self):
        if self.text_box:
            self.cible.setText(self.buffer)
        else:
            self.cible.setValue(self.buffer)
        self.cible.clearFocus()
        self.validation_saisie.emit()
        self.hide()  # Ferme le dialogue avec succès

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

    def buildUI(self):
        screen_dims = get_screen_dimensions()
        largeur = screen_dims['width']
        hauteur = screen_dims['height']

        w_app = int(largeur * 0.5)
        h_app = int(hauteur * 0.75)

        self.resize(w_app, h_app)

        x_pos = int(largeur * (1 - 0.25) - w_app)
        y_pos = int(hauteur * (1 - 0.125) - h_app)

        self.setStyleSheet(f"font-size: 10pt;")

        self.move(x_pos, y_pos)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clavier = ClavierVisuel(QLineEdit())
    clavier.show()
    sys.exit(app.exec_())
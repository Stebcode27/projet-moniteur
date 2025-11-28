import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

def creer_logo_et_texte_centre(logo_path, texte_a_afficher):
    """
    Crée un widget conteneur avec le logo à gauche et le texte centré.
    """
    # --- Widget Conteneur Principal (là où tout sera placé) ---
    conteneur = QWidget()
    conteneur.setStyleSheet("background-color: black; color: white")  # Optionnel : fond noir pour mieux voir le logo et le texte
    h_layout = QHBoxLayout(conteneur)
    
    # Élimine la marge interne par défaut pour un placement plus précis
    h_layout.setContentsMargins(0, 0, 0, 0) 
    h_layout.setSpacing(10) # Espacement entre le logo et le texte

    # --- 1. Le Logo à Gauche (QLabel Image) ---
    label_logo = QLabel()
    try:
        pixmap = QPixmap(logo_path)
        
        # Redimensionnement (exemple : 50x50)
        taille = 50 
        pixmap_scaled = pixmap.scaled(taille, taille, Qt.KeepAspectRatio)
        
        label_logo.setPixmap(pixmap_scaled)
        # S'assure que le logo reste à gauche
        label_logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter) 
        
    except Exception as e:
        print(f"Erreur de chargement du logo : {e}")
        label_logo.setText("Logo non trouvé")
        
    # --- 2. Le Texte Centré (QLabel Texte) ---
    label_texte = QLabel(texte_a_afficher)
    # Important : Utiliser un 'stretch' pour forcer le QLabel texte à prendre 
    # le maximum d'espace disponible et ainsi permettre le centrage.
    label_texte.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
    
    # --- 3. Assemblage dans le QHBoxLayout ---
    # Ajout du logo (pas de 'stretch', il garde sa taille)
    h_layout.addWidget(label_logo) 
    
    # Ajout du texte (avec un facteur de 'stretch' de 1)
    # Cela permet au texte d'occuper l'espace restant
    h_layout.addWidget(label_texte, 1) 
    
    # (Optionnel) Ajout d'un stretch à droite pour centrer l'ensemble 
    # du texte sur l'espace restant après le logo.
    h_layout.addStretch(1) 
    
    return conteneur

# --- Utilisation dans l'Application ---
class MaFenetre(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logo à Gauche, Texte Centré")
        
        main_layout = QVBoxLayout(self)
        
        # NOTE : Remplacez 'logo.png' par le chemin de votre image
        logo_texte_widget = creer_logo_et_texte_centre(
            'assets/heart.png', 
            "Mon Titre d'Application Centré"
        )
        
        main_layout.addWidget(logo_texte_widget)
        main_layout.addStretch(1) # Pour pousser l'élément vers le haut

if __name__ == '__main__':
    app = QApplication(sys.argv)
    fenetre = MaFenetre()
    fenetre.show()
    sys.exit(app.exec_())
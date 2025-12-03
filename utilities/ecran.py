import sys
from PyQt5.QtWidgets import QApplication

def get_screen_dimensions():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    screen = app.primaryScreen()
    screen_geometry = screen.availableGeometry()
    largeur = screen_geometry.width()
    hauteur = screen_geometry.height()

    return {
        "width": largeur,
        "height": hauteur,
    }

if __name__ == '__main__':

    try:
        print(get_screen_dimensions())
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
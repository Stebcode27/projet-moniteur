from model_app_login import ModelApp
from loader import SplachScreen
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = ModelApp(app)

    splach = SplachScreen(5000, window)

    splach.show()

    sys.exit(app.exec_())
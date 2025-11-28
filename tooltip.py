from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
import sys

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setToolTip("Infobulle principal")

app = QApplication(sys.argv)

w = QWidget()
w.setToolTip(
    "Infos bulles"
)
w.show()
sys.exit(app.exec_())

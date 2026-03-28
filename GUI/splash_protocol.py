import time

from PyQt5.QtWidgets import QApplication, QSplashScreen, QDesktopWidget, QProgressBar
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import serial
import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

class MonitorSplash(QSplashScreen):
    """Ecran de chargement"""

    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.init_splash()
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(300, self.pixmap.height() - 100, self.pixmap.width() - 600, 25)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.show()
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: 1px solid white;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00ff00;
            }
        """)
        self.setStyleSheet("font-size: 15pt, font-weight: bold; font-family: sans-serif;")
        """self.timer = QTimer()
        self.timer.timeout.connect(self.d)
        self.timer.start(1000)"""

    def update_progress(self, value):
        self.progressBar.setValue(value)
    def d(self):
        self.progressBar.setValue(self.progressBar.value() + 5)

    def init_splash(self):
        screen_rect = QDesktopWidget().screenGeometry()
        width = screen_rect.width()
        height = screen_rect.height()

        chemin = os.path.join(PROJECT_ROOT, 'assets', 'Seaweed.png')
        self.pixmap = QPixmap(chemin).scaled(width, height,
                                      Qt.IgnoreAspectRatio,
                                      Qt.SmoothTransformation)
        self.setPixmap(self.pixmap)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

        marque = "LIFE KEEPER"
        style = f'<span style="font-family: freestyle script; font-size: 100pt; font-weight: bold; color: white;">{marque}</span>"'
        self.showMessage(style, Qt.AlignCenter)

class HandShakeThread(QThread):

    connection_established = pyqtSignal()
    progression = pyqtSignal(int)
    error_occured = pyqtSignal(str)

    def run(self):
        try:
            ser = serial.Serial('COM8', 115200, timeout=1)
            ser.flush()
            self.progression.emit(10)

            print("En attente d'Esp32")

            self.progression.emit(30)
            found_esp = False
            while not found_esp:
                if ser.in_waiting:
                    byte = ser.read(1)
                    if byte == bytes([0x01]):
                        found_esp = True
                        print("ESP32 détectée.")

            time.sleep(1)

            self.progression.emit(60)
            ser.write(bytes([0x02]))
            print("Confirmation envoyée")
            self.progression.emit(80)
            while True:
                if ser.in_waiting:
                    byte = ser.read(1)
                    if byte == bytes([0x03]):
                        print('Signal de démarrage recu!')
                        self.progression.emit(100)
                        self.connection_established.emit()
                        break
                #time.sleep(0.1)


        except Exception as e:
            self.error_occured.emit(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    comm = MonitorSplash()
    comm.showFullScreen()
    sys.exit(app.exec_())

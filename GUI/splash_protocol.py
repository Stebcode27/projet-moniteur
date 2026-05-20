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


def resource_path(relative_path):
    """ Récupère le chemin absolu vers la ressource, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Mode Production (.exe) : PyInstaller extrait tout directement dans sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)

    # Mode Développement (PyCharm) : On garde ta logique PROJECT_ROOT actuelle
    # 'dirname(__file__), ".."' permet de remonter au dossier racine du projet
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(PROJECT_ROOT, relative_path)

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

            self.progression.emit(50)
            ser.write(bytes([0x02]))
            print("Confirmation envoyée")
            while True:
                if ser.in_waiting:
                    self.progression.emit(80)
                    byte = ser.read(1)
                    if byte == bytes([0x03]):
                        print('Signal de démarrage recu!')
                        self.progression.emit(100)
                        self.connection_established.emit()
                        break
                #time.sleep(0.1)


        except Exception as e:
            self.error_occured.emit(str(e))


class MonitorSplash(QSplashScreen):
    """Ecran de chargement"""

    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.log_message ="Initialisation du programme de log..."
        self.stylised = None
        self.marque = None
        self.init_splash()
        self.progressBar = None
        self.liste_txt = ["Connexion au module de traitement", "En attente du module de traitement.", "Confirmation envoyée", "Signal de démarrage recu!"]
        self.txt_ptr = 0

        self.handshaker = HandShakeThread()
        self.handshaker.progression.connect(self.update_progress)
        self.handshaker.error_occured.connect(lambda msg: self.display_handshake_err(msg))

        self.timer_for_marque = QTimer()
        self.timer_for_marque.setSingleShot(True)
        self.timer_for_marque.timeout.connect(self.on_timer)
        self.timer_for_marque.start(8000)

        self.setStyleSheet("font-size: 15pt, font-weight: bold; font-family: sans-serif;")

        #self.timer = QTimer()
        #self.timer.timeout.connect(self.d)

    def on_timer(self):
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
        self.stylised = f'<div style="font-family: freestyle script; font-size: 100pt; font-weight: bold; color: white;">{self.marque}</div><br/><span style="font-family: consolas; font-size: 12pt; font-weight: italic; color: white;">{self.liste_txt[self.txt_ptr % len(self.liste_txt)]}</span>'
        self.txt_ptr += 1
        self.showMessage(self.stylised, Qt.AlignCenter)
        self.handshaker.start()

    def update_progress(self, value):
        self.progressBar.setValue(value)
        self.stylised = f'<div style="font-family: freestyle script; font-size: 100pt; font-weight: bold; color: white;">{self.marque}</div><br/><span style="font-family: consolas; font-size: 12pt; font-weight: italic; color: white;">{self.liste_txt[self.txt_ptr % len(self.liste_txt)]}</span>'
        self.showMessage(self.stylised, Qt.AlignCenter)
        self.txt_ptr += 1
        if self.progressBar.value() == 100:
            self.close()

    def d(self):
        self.progressBar.setValue(self.progressBar.value() + 25)
        self.stylised = f'<div style="font-family: freestyle script; font-size: 100pt; font-weight: bold; color: white;">{self.marque}</div><br/><span style="font-family: consolas; font-size: 12pt; font-weight: italic; color: white;">{self.liste_txt[self.txt_ptr % len(self.liste_txt)]}</span>'
        self.showMessage(self.stylised, Qt.AlignCenter)
        self.txt_ptr += 1

    def init_splash(self):
        screen_rect = QDesktopWidget().screenGeometry()
        width = screen_rect.width()
        height = screen_rect.height()

        chemin = resource_path("assets/Seaweed.png")
        self.pixmap = QPixmap(chemin).scaled(width, height,
                                      Qt.IgnoreAspectRatio,
                                      Qt.SmoothTransformation)
        self.setPixmap(self.pixmap)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

        self.marque = "LIFE KEEPER"
        self.stylised = f'<div style="font-family: freestyle script; font-size: 100pt; font-weight: bold; color: white;">{self.marque}</div>'
        self.showMessage(self.stylised, Qt.AlignCenter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    comm = MonitorSplash()
    sys.exit(app.exec_())

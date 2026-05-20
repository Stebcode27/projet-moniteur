import sys
import os
# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QVBoxLayout, QListWidget, QPushButton, QLabel, QMessageBox, QHBoxLayout
from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import Qt, QUrl, QJsonDocument, QTimer
from PyQt5.QtGui import QMovie
from utilities.duration import serialize_data_for_transmission


def resource_path(relative_path):
    """ Récupère le chemin absolu vers la ressource, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Mode Production (.exe) : PyInstaller extrait tout directement dans sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)

    # Mode Développement (PyCharm) : On garde ta logique PROJECT_ROOT actuelle
    # 'dirname(__file__), ".."' permet de remonter au dossier racine du projet
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(PROJECT_ROOT, relative_path)

class WifiScannerForServer(QDialog):
    def __init__(self, parent=None, payload=None, patient=False):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Wifi Scanner")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setMinimumSize(600, 300)
        self.setMaximumSize(700, 400)
        self.payload = payload
        self.is_patient = patient
        self.target_port = 5000
        self.udp_port = -45454

        self.timer = QTimer()
        self.timer.setSingleShot(True)

        self.connected_to_server = False

        self.setStyleSheet("font: normal 9pt roboto")

        self.widget = QWidget()
        self.widget_lay = QVBoxLayout(self.widget)

        self.label = QLabel()

        #config réseau
        self.udp_socket = QUdpSocket(self)

        self.udp_socket.readyRead.connect(self.process_udp_response)

        self.ico_wifi_search = resource_path("assets/radio.gif")

        #interface
        self.layout = QVBoxLayout(self)
        self.status_lab = QLabel("Cliquez sur scanner pour trouver des machines...")
        self.layout.addWidget(self.status_lab)

        self.list_devices = QListWidget()
        self.widget_lay.addWidget(self.list_devices)
        self.layout.addWidget(self.widget)

        btn_lay = QHBoxLayout()
        self.btn_scan = QPushButton("Scanner le réseau")
        self.btn_scan.clicked.connect(self.send_broadcast_query)

        self.btn_send = QPushButton("Connecter et Envoyer")
        self.btn_send.setStyleSheet("background-color:green; color:white; border-radius:5px; border:0px solid black; padding:7px;")
        self.btn_send.setEnabled(False)
        self.btn_send.clicked.connect(self.start_transfert)

        self.movie = QMovie(self.ico_wifi_search)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMovie(self.movie)
        self.widget_lay.addWidget(self.label)

        #self.btn_scan.setFocus()

        btn_lay.addWidget(self.btn_scan)
        btn_lay.addWidget(self.btn_send)
        self.layout.addLayout(btn_lay)

        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.on_http_finished)

        self.timer.timeout.connect(self.is_host_detected)

        self.movie.stop()
        self.list_devices.show()
        self.label.hide()

    def is_host_detected(self):
        if not self.connected_to_server:
            box = QMessageBox()
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle("Attention")
            box.setText(f"La connexion au serveur met trop de temps.\nAssurez-vous que le moniteur et le serveur soit dans le même réseau !")
            box.setStandardButtons(QMessageBox.Ok)
            box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
            if box.exec_() == QMessageBox.Ok:
                self.list_devices.show()
                self.label.hide()
                self.status_lab.setText("Cliquez sur scanner pour trouver des machines...")

    def send_broadcast_query(self):
        if not self.is_patient:
            messagebox = QMessageBox()
            messagebox.setIcon(QMessageBox.Critical)
            messagebox.setText("Impossble de trasferer les données car il manque des informations sur le patient actuel!")
            messagebox.setStandardButtons(QMessageBox.Cancel)
            messagebox.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
            if messagebox.exec_() == QMessageBox.Cancel:
                self.close()

        self.list_devices.clear()
        self.status_lab.setText("Recherche en cours...")

        self.list_devices.hide()

        self.movie.start()
        self.label.show()

        message = b"MONITOR_REQUEST"

        #envoie à l'adresse de broadcast sur le port dédié
        try:
            self.udp_socket.writeDatagram(message, QHostAddress.Broadcast, self.udp_port)
            self.execute_timer()
        except Exception as e:
            b = QMessageBox()
            b.setIcon(QMessageBox.Critical)
            b.setText(f"Erreur de Connexion!\nDétails: \t{str(e)}")
            b.setStandardButtons(QMessageBox.Cancel)
            b.setWindowTitle("Erreur")
            b.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
            self.label.hide()
            self.list_devices.show()
            self.movie.stop()
            self.status_lab.setText("Cliquez sur scanner pour trouver des machines...")
            b.exec_()

    def process_udp_response(self):
        if not self.udp_socket.hasPendingDatagrams():
            print("no data")
        while self.udp_socket.hasPendingDatagrams():
            datagram, host, port = self.udp_socket.readDatagram(self.udp_socket.pendingDatagramSize())
            response = datagram.decode()
            #si la machine répond avec le bon code?
            if "MONITOR_ALIVE" in response:
                ip_adress = host.toString()
                self.list_devices.addItem(ip_adress.replace("::ffff:", ""))
                self.btn_send.setEnabled(True)
                self.status_lab.setText("Hôte(s) trouvé(s) !")
                self.label.hide()
                self.list_devices.show()
                self.connected_to_server = True
            else:
                self.connected_to_server = False

    def start_transfert(self):
        selected = self.list_devices.currentItem()
        if not selected: return
        patient_infos = self.payload['patient'].values()

        if not patient_infos:
            box = QMessageBox()
            box.setIcon(QMessageBox.Critical)
            box.setText("Impossible de transferer les données sur le serveur distant car il manque l'identifiant du patient pour le faire !")
            box.setStandardButtons(QMessageBox.Cancel)
            box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
            if box.exec_() == QMessageBox.Cancel:
                self.close()

        ip = selected.text()
        ip = ip.replace("::ffff:", "")
        self.status_lab.setText(f"Envoie encours vers {ip}...")
        self.btn_send.setEnabled(False)

        url = QUrl(f"http://{ip}:{self.target_port}/api/monitoring/session")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        json_data = QJsonDocument(self.payload).toJson()

        self.network_manager.post(request, json_data)

        self.connected_to_server = True

    def on_http_finished(self, reply):
        error = reply.error()
        if error == reply.NoError:
            QMessageBox.information(self, "Succès", "Données transmises avec succès au serveur distant")
            self.parent.count_enregistrement += 1
            self.accept()
        else:
            self.status_lab.setText(f"Erreur: {reply.errorString()}")
            self.btn_send.setEnabled(True)
        reply.deleteLater()

    def set_payload(self, payload):
        self.payload = payload
    def get_payload(self):
        return self.payload

    def set_is_patient(self, is_patient):
        self.is_patient = is_patient

    def execute_timer(self):
        self.timer.start(10000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    data = [r**2 for r in range(1000000)]
    scanner = WifiScannerForServer()
    scanner.set_payload(data)
    scanner.set_is_patient(True)
    scanner.show()
    sys.exit(app.exec_())
    #print(serialize_data_for_transmission())
import json
import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QVBoxLayout, QListWidget, QPushButton, QLabel, QMessageBox, QHBoxLayout
from PyQt5.QtNetwork import QUdpSocket, QTcpSocket, QHostAddress
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QMovie
from utilities.ecran import get_screen_dimensions

class WifiScannerForServer(QDialog):
    def __init__(self, data_to_send=None):
        super().__init__()
        self.setWindowTitle("Wifi Scanner")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setMinimumSize(600, 300)
        self.setMaximumSize(700, 400)
        self.payload = data_to_send
        self.target_port = 8080
        self.udp_port = 45454

        self.connected_to_server = False

        self.setStyleSheet("font: normal 9pt Consolas;")

        self.widget = QWidget()
        self.widget_lay = QVBoxLayout(self.widget)

        self.label = QLabel()

        #config réseau
        self.udp_socket = QUdpSocket(self)
        self.tcp_socket = QTcpSocket(self)

        self.udp_socket.readyRead.connect(self.process_udp_response)

        self.tcp_socket.connected.connect(self.on_tcp_connected)
        self.tcp_socket.error.connect(self.on_tcp_error)

        self.ico_wifi_search = os.path.join(PROJECT_ROOT, 'assets', 'radio.gif')

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
        self.btn_send.clicked.connect(self.start_tcp_transfert)

        btn_lay.addWidget(self.btn_scan)
        btn_lay.addWidget(self.btn_send)
        self.layout.addLayout(btn_lay)

    def send_broadcast_query(self):
        self.list_devices.clear()
        self.status_lab.setText("Recherche en cours...")

        self.list_devices.hide()

        movie = QMovie(self.ico_wifi_search)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMovie(movie)
        movie.start()
        self.widget_lay.addWidget(self.label)

        message = b"MONITOR_REQUEST"

        #envoie à l'adresse de broadcast sur le port dédié
        try:
            self.udp_socket.writeDatagram(message, QHostAddress.Broadcast, self.udp_port)
            #print('envoyé')
        except Exception as e:
            print("Erreur lourde: " + str(e))

    def process_udp_response(self):
        if not self.udp_socket.hasPendingDatagrams():
            print("no data")
        while self.udp_socket.hasPendingDatagrams():
            datagram, host, port = self.udp_socket.readDatagram(self.udp_socket.pendingDatagramSize())
            response = datagram.decode()
            #si la machine répond avec le bon code?
            if "MONITOR_ALIVE" in response:
                ip_adress = host.toString()
                self.list_devices.addItem(ip_adress)
                self.btn_send.setEnabled(True)
                self.status_lab.setText("Machine(s) trouvée(s) !")
                self.label.hide()
                self.list_devices.show()

    def start_tcp_transfert(self):
        selected = self.list_devices.currentItem()
        if not selected: return
        ip = selected.text()
        self.status_lab.setText(f"Connexion à {ip}...")
        self.btn_send.setEnabled(False)

        self.tcp_socket.connectToHost(ip, self.target_port)
        self.connected_to_server = True

    def on_tcp_connected(self):
        raw_data = json.dumps(self.payload).encode()
        self.tcp_socket.write(raw_data)

        if self.tcp_socket.waitForBytesWritten(2000):
            QMessageBox.information(self, "Succès", "Données JSON transmises.")
            self.tcp_socket.disconnectFromHost()
            self.accept()
        else:
            self.status_lab.setText("Erreur lors de l'écriture des données.")
            self.btn_send.setEnabled(True)

    def on_tcp_error(self, error):
        #QMessageBox.critical(self, "Erreur TCP", self.tcp_socket.errorString())
        self.btn_send.setEnabled(True)

    def set_payload(self, payload):
        self.payload = payload
    def get_payload(self):
        return self.payload


if __name__ == '__main__':
    app = QApplication(sys.argv)
    data = {
        'ecg': [2., 3., 2.3],
        'sat': [0.04, 5.4, 9.009]
    }
    scanner = WifiScannerForServer(data)
    scanner.show()
    sys.exit(app.exec_())
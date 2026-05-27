import sys
import os
# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QVBoxLayout, QListWidget, QPushButton, QLabel, QMessageBox, QHBoxLayout, QProgressBar
# AJOUT de QNetworkInterface ici
from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QNetworkAccessManager, QNetworkRequest, QNetworkInterface
from PyQt5.QtCore import Qt, QUrl, QJsonDocument, QTimer
from PyQt5.QtGui import QMovie
from utilities.duration import serialize_data_for_transmission


def resource_path(relative_path):
    """ Récupère le chemin absolu vers la ressource, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
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
        self.udp_port = 45454

        self.timer = QTimer()
        self.timer.setSingleShot(True)

        self.connected_to_server = False
        self.current_reply = None

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

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

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

    def is_network_available(self):
        """
        Vérifie si une interface réseau (Wi-Fi / Ethernet) est active et
        possède une adresse IP valide (autre que localhost).
        """
        interfaces = QNetworkInterface.allInterfaces()
        for interface in interfaces:
            # On vérifie que l'interface est active (Up) et qu'elle tourne (Running)
            if interface.flags() & QNetworkInterface.IsUp and interface.flags() & QNetworkInterface.IsRunning:
                # On évite l'interface de Loopback (le localhost 127.0.0.1 de la machine)
                if not (interface.flags() & QNetworkInterface.IsLoopBack):
                    # On s'assure qu'elle possède au moins une adresse IP attribuée
                    if len(interface.addressEntries()) > 0:
                        return True
        return False

    def send_broadcast_query(self):
        # 1. AJOUT : Vérification de l'activation du Wi-Fi / Réseau
        if not self.is_network_available():
            messagebox = QMessageBox()
            messagebox.setIcon(QMessageBox.Warning)
            messagebox.setWindowTitle("Réseau indisponible")
            messagebox.setText("Le Wi-Fi ou la connexion réseau semble désactivé.\nVeuillez activer votre connexion avant de scanner.")
            messagebox.setStandardButtons(QMessageBox.Ok)
            messagebox.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
            messagebox.exec_()
            return  # On stoppe la fonction ici

        # 2. Vérification du patient (votre code d'origine)
        if not self.is_patient:
            messagebox = QMessageBox()
            messagebox.setIcon(QMessageBox.Critical)
            messagebox.setText("Impossible de transférer les données car il manque des informations sur le patient actuel!")
            messagebox.setStandardButtons(QMessageBox.Cancel)
            messagebox.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
            if messagebox.exec_() == QMessageBox.Cancel:
                self.close()
                return

        self.list_devices.clear()
        self.status_lab.setText("Recherche en cours...")
        self.list_devices.hide()
        self.movie.start()
        self.label.show()

        message = b"MONITOR_REQUEST"

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
            pass
        while self.udp_socket.hasPendingDatagrams():
            datagram, host, port = self.udp_socket.readDatagram(self.udp_socket.pendingDatagramSize())
            response = datagram.decode()
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
        try:
            patient_infos = self.payload['patient'].values()
        except TypeError:
            patient_infos = serialize_data_for_transmission()['patient'].values()

        if not patient_infos:
            box = QMessageBox()
            box.setIcon(QMessageBox.Critical)
            box.setText("Impossible de transférer les données sur le serveur distant car il manque l'identifiant du patient pour le faire !")
            box.setStandardButtons(QMessageBox.Cancel)
            box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
            if box.exec_() == QMessageBox.Cancel:
                self.close()

        ip = selected.text()
        ip = ip.replace("::ffff:", "")
        self.status_lab.setText(f"Envoi en cours vers {ip}...")
        self.btn_send.setEnabled(False)
        self.btn_scan.setEnabled(False)

        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        url = QUrl(f"http://{ip}:{self.target_port}/api/monitoring/session")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        json_data = QJsonDocument(self.payload).toJson()

        self.current_reply = self.network_manager.post(request, json_data)
        self.current_reply.uploadProgress.connect(self.on_upload_progress)
        self.current_reply.downloadProgress.connect(self.on_download_progress)

        self.connected_to_server = True

    def on_http_finished(self, reply):
        error = reply.error()
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        if error == reply.NoError:
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Succès", "Données transmises avec succès au serveur distant")
            if self.parent and hasattr(self.parent, 'count_enregistrement'):
                self.parent.count_enregistrement += 1
            self.accept()
        else:
            self.status_lab.setText(f"Erreur: {reply.errorString()}")
            self.btn_send.setEnabled(True)
        reply.deleteLater()

    def on_upload_progress(self, bytes_sent, total_bytes):
        if total_bytes > 0:
            percentage = int((bytes_sent / total_bytes) * 100)
            self.progress_bar.setValue(percentage)
            self.status_lab.setText(f"Envoi en cours... {percentage}%")

    def on_download_progress(self, bytes_received, total_bytes):
        if total_bytes > 0:
            percentage = int((bytes_received / total_bytes) * 100)
            self.progress_bar.setValue(min(percentage + 5, 100))

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
    data = {"patient": {"id": 123}, "data": [r**2 for r in range(100)]}
    scanner = WifiScannerForServer()
    scanner.set_payload(data)
    scanner.set_is_patient(True)
    scanner.show()
    sys.exit(app.exec_())
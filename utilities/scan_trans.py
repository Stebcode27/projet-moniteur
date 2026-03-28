import xml.etree.ElementTree as ET
import sys
import os
# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QVBoxLayout, QListWidget, QPushButton, QLabel, QMessageBox, QHBoxLayout
from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import Qt, QUrl, QJsonDocument
from PyQt5.QtGui import QPixmap, QMovie


def extraire_donnees_moniteur(chaine_xml):
    root_xml = f"<data>{chaine_xml}</data>"

    try:
        root = ET.fromstring(root_xml)
        balises_a_verifier = ['HR', 'SPO2', 'RESP', 'TEMP', 'PNI/SYS', 'PNI/DIAS', 'PNI/PAM', 'TIMESTAMP']

        for chemin in balises_a_verifier:
            element = root.find(chemin)
            if element is None or element.text is None or element.text.strip() == "":
                return None

        donnees = {
            "hr": int(root.find('HR').text),
            "spo2": int(root.find('SPO2').text),
            "resp": int(root.find('RESP').text),
            "temp": float(root.find('TEMP').text),
            "pni": {
                "sys": int(root.find('PNI/SYS').text),
                "dias": int(root.find('PNI/DIAS').text),
                "pam": int(root.find('PNI/PAM').text)
            },
            "timestamp": root.find('TIMESTAMP').text
        }
        return donnees

    except (ET.ParseError, ValueError):
        # On attrape aussi ValueError au cas où le texte n'est pas convertible en nombre
        return None

def serialize_data_for_transmission():
    database_file = os.path.join(PROJECT_ROOT, 'datas', 'base_donnees.txt')
    infos_exam_file = os.path.join(PROJECT_ROOT, 'datas', 'patient_infos.txt')
    """Modèle de l'objet Json à envoyer au serveur pour le stockage"""
    """data = {
        "patient": {
            "id": 5,
            "nom": "SENDER",
            "age": 27,
            "sexe": "Masculin",
            "poids": 23.34,
            "taille": 234
        },
        "medecin":,
        "exam": {
            "debut_exam":,
            "salle":,
            "service":,
        },
        "donnees": [
            {"timestamp":, "hr":, "spo2":, "resp":, "temp":, "pni": {"sys": , "dias": , "pam": }},
        ]      
    }"""
    data = {
        "patient": {},
        "medecin": "",
        "exam": {},
        "donnees": [],
    }

    with open(infos_exam_file, 'r+') as f:
        informations = f.readline().split("_")
        data['patient']['nom'] = informations[0]
        data['patient']['id'] = informations[1]
        data['patient']['age'] = informations[2]
        data['patient']['sexe'] = informations[3]
        data['patient']['poids'] = informations[4]
        data['patient']['taille'] = informations[5]

        data['exam']['salle'] = informations[6]
        data['exam']['service'] = informations[7]
        data['medecin'] = informations[8]
        data['exam']['debut_exam'] = informations[9]

    with open(database_file, 'r') as f:

        while True:
            line = f.readline()
            if line=='': break
            donnees = extraire_donnees_moniteur(line)
            data['donnees'].append(donnees)

    return data

class WifiScannerForServer(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wifi Scanner")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setMinimumSize(600, 300)
        self.setMaximumSize(700, 400)
        self.payload = serialize_data_for_transmission()
        self.target_port = 5000
        self.udp_port = 45454

        self.connected_to_server = False

        self.setStyleSheet("font: normal 9pt Consolas;")

        self.widget = QWidget()
        self.widget_lay = QVBoxLayout(self.widget)

        self.label = QLabel()

        #config réseau
        self.udp_socket = QUdpSocket(self)

        self.udp_socket.readyRead.connect(self.process_udp_response)

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
        self.btn_send.clicked.connect(self.start_transfert)

        btn_lay.addWidget(self.btn_scan)
        btn_lay.addWidget(self.btn_send)
        self.layout.addLayout(btn_lay)

        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.on_http_finished)

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

    def start_transfert(self):
        selected = self.list_devices.currentItem()
        if not selected: return

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
            self.accept()
        else:
            self.status_lab.setText(f"Erreur: {reply.errorString()}")
            self.btn_send.setEnabled(True)
        reply.deleteLater()

    def set_payload(self, payload):
        self.payload = payload
    def get_payload(self):
        return self.payload


if __name__ == '__main__':
    app = QApplication(sys.argv)
    data = [r**2 for r in range(1000000)]
    scanner = WifiScannerForServer()
    scanner.show()
    sys.exit(app.exec_())
    #print(serialize_data_for_transmission())
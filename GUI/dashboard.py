import sys
import os

import numpy as np

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialog, QPushButton,
                             QMessageBox, QGraphicsColorizeEffect)
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation
from PyQt5.QtGui import QIcon, QPixmap, QColor
from datetime import datetime
from definitions.templates_params import Ecg, Saturation, Respiration, Pression, Temperature, Interface
from definitions.erreur_seuils import SurveillanceThread
from GUI.patient_infos import FenetrePatient
from utilities.preferences import COLOR_THEME, PARAMS_SEUILS
from utilities.duration import calculate_time_format
from GUI.label_cliquable import LabelCliquable
from GUI.configs import ConfigBox
from GUI.log_widget import LogWidget
from GUI.admission_patient import AdmissionPatient
from utilities.scan_trans import WifiScannerForServer

class Dashboard(QMainWindow):

    """La classe qui définie l'interface principale du moniteur"""

    def __init__(self):
        super().__init__()
        self.ecg = Ecg(self)
        self.saturation = Saturation(self)
        self.respiration = Respiration(self)
        self.pression = Pression(self)
        self.temperature = Temperature(self)
        self.time_h = None
        self.name_patient = None
        self.date = None
        self.barre_etat = None
        self.timer_infos = None
        self.state_heart = None
        self.duration_count = 0
        self.heure_debut = ""

        self.data_from_serial = {}

        self.scanner = WifiScannerForServer()
        self.data_to_transfer = {
            'hr': [],
            'sat': [],
            'pni': {
                'systo': [],
                'diasto': [],
                'pam': []
            },
            'temp': [],
            'resp': []
        }
        self.alerte_status = False

        self.status_saved = False

        self.pause_state = False

        self.liste_boutons_cmd = []

        self.simul_state, self.next_simul_state = False, False

        self.wrong_param = None

        self.heart_on, self.heart_off = "heart_on.png", "heart_off.png"
        self.state_heart = True

        self.top_app = QWidget()
        self.bottom_app = QWidget()

        self.layout_app = QVBoxLayout()

        self.app_infos_patient = FenetrePatient()

        self.admission_patient = AdmissionPatient()

        self.error_modal_app = None
        self.configbox = None

        self.theme = None
        self.wifi_on = os.path.join(PROJECT_ROOT, 'assets', 'wifi_on.png')
        self.wifi_off = os.path.join(PROJECT_ROOT, 'assets', 'wifi_off.png')

        self.setWindowTitle("Moniteur")
        self.setGeometry(10, 10, 800, 400)
        self.buildUI()
        self.setContentsMargins(0, 0, 0, 0)

        self.setup_animations()

        self.thread_surveillance = SurveillanceThread(self)
        self.thread_surveillance.alerte_detectee.connect(self.gerer_alerte_visuelle)
        self.thread_surveillance.start()

        self.interface_serie = Interface()
        self.interface_serie.onChanged.connect(self.new_data_from_serial)
        self.interface_serie.onError.connect(self.error_from_serial)
        self.interface_serie.onPressionProcessed.connect(self.pression_processed)
        self.interface_serie.start()

    def buildUI(self):
        """Fonction pour la construction du dashboard"""
        layout_top = QHBoxLayout(self.top_app)
        self.top_app.setStyleSheet(f"background-color: {self.theme}; border-radius: 20px;")

        self.infos_patient = LabelCliquable("Informations patient")
        self.infos_patient.setStyleSheet("color: white; font-size: 14pt;")
        self.infos_patient.setAlignment(Qt.AlignLeft)
        self.infos_patient.clique.connect(self.get_infos_patient)

        self.alarm_lab = QLabel("Alarmes")
        self.alarm_lab.setStyleSheet("color: white; font-size: 13pt; background-color: #0055AA;")
        self.alarm_lab.setAlignment(Qt.AlignCenter)

        self.date = QLabel(datetime.now().strftime("%H:%M:%S"), self)

        self.utilitaires = QWidget()

        self.label_wifi = QLabel()
        self.label_wifi.setPixmap(QPixmap(self.wifi_off))

        self.duree_label = QLabel()
        self.duree_label.setText("Duree de l'examen")

        layout_util = QHBoxLayout(self.utilitaires)
        layout_util.addWidget(self.date, stretch=2)
        layout_util.addWidget(self.label_wifi, stretch=2)
        layout_util.addWidget(self.duree_label, stretch=2)

        self.utilitaires.setStyleSheet("color: white; font-size: 12pt;")

        layout_top.addWidget(self.infos_patient, stretch=1)
        layout_top.addWidget(self.alarm_lab, stretch=2)
        layout_top.addWidget(self.utilitaires, stretch=1)

        self.layout_app.addWidget(self.top_app, stretch=1)

        txt_buttons = ["Silence", "Pause", "Démarrer PNI", "Enregistrer", "Patient", "Menu"]
        icons_buttons = [os.path.join(PROJECT_ROOT, 'assets', 'silence.png'), os.path.join(PROJECT_ROOT, 'assets', 'pause.png'), os.path.join(PROJECT_ROOT, 'assets', 'pni.png'), os.path.join(PROJECT_ROOT, 'assets', 'save.png'), os.path.join(PROJECT_ROOT, 'assets', 'patient.png'), os.path.join(PROJECT_ROOT, 'assets', 'menu.png')]

        layout_bottom = QHBoxLayout(self.bottom_app)

        for txt in txt_buttons:
            button = QPushButton()
            button.setText(txt)
            button.setStyleSheet("color: white; font-size: 16pt; padding: 10px; background-color: #0055AA; border-radius: 20px;")
            self.liste_boutons_cmd.append(button)
            layout_bottom.addWidget(button)

        for i in range(len(self.liste_boutons_cmd)):
            icon = QIcon(icons_buttons[i])
            self.liste_boutons_cmd[i].setIcon(icon)
            self.liste_boutons_cmd[i].setIconSize(QSize(75, 75))

        for button in self.liste_boutons_cmd:
            if button.text() == "Patient":
                button.clicked.connect(self.add_patient)
            elif button.text() == "Menu":
                button.clicked.connect(self.open_param_box)
            elif button.text() == "Pause":
                button.clicked.connect(self.pause)
            elif button.text() == "Enregistrer":
                button.clicked.connect(self.start_transfert)

        self.time_h = QTimer()
        self.time_h.timeout.connect(self.update_time)
        self.time_h.start(1)

        self.layout1 = QHBoxLayout()

        #conteneurs pour les paramètres
        self.conteneur_ecg = QWidget()
        self.conteneur_ecg.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")
        self.conteneur_pression = QWidget()
        self.conteneur_pression.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")
        self.conteneur_saturation = QWidget()
        self.conteneur_saturation.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")
        self.conteneur_resp = QWidget()
        self.conteneur_resp.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")
        self.conteneur_temp = QWidget()
        self.conteneur_temp.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")
        self.conteneur_history = QWidget()
        self.conteneur_history.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")

        history_layout = QVBoxLayout(self.conteneur_history)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        heart_on_path = os.path.join(PROJECT_ROOT, 'assets', self.heart_on)
        self.logo_label.setPixmap(QPixmap(heart_on_path))
        self.seuil_hr_label = QLabel()
        self.seuil_hr_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.seuil_hr_label.setText(f"{PARAMS_SEUILS[0]['val_max']}\n{PARAMS_SEUILS[0]['val_min']}")
        self.seuil_hr_label.setStyleSheet("color: #33FF57; font-size: 16pt;")
        ecg_top_lay = QHBoxLayout()
        ecg_top_lay.addWidget(self.logo_label)
        ecg_top_lay.addWidget(self.seuil_hr_label)
        self.ecg_layout = QVBoxLayout(self.conteneur_ecg)
        self.ecg_layout.setContentsMargins(0, 0, 0, 0)
        self.ecg_layout.addLayout(ecg_top_lay)
        self.ecg_label = QLabel("--")
        self.ecg_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.ecg_label.setStyleSheet("font-size: 70pt; font-weight: bold; color: #33FF57; padding-bottom: 25px;")
        self.ecg_layout.addWidget(self.ecg_label)
        lay_unite_hr = QHBoxLayout()
        unite_hr = QLabel("bpm")
        hr = QLabel("HR")
        hr.setStyleSheet("color: #33FF57; font-size: 16pt;")
        unite_hr.setStyleSheet("color: #33FF57; font-size: 16pt;")
        lay_unite_hr.addStretch(1)
        lay_unite_hr.addWidget(unite_hr, stretch=1, alignment=Qt.AlignCenter)
        lay_unite_hr.addWidget(hr, stretch=1, alignment=Qt.AlignRight)
        self.ecg_layout.addLayout(lay_unite_hr)

        self.pression_layout = QVBoxLayout(self.conteneur_pression)
        self.pression_layout.setContentsMargins(0, 0, 0, 0)
        press_unite = QLabel("NIBP (Dias/Sys)")
        press_unite.setAlignment(Qt.AlignLeft)
        self.press_moy_value = QLabel("--")
        self.press_moy_value.setStyleSheet("color: white; font-size: 28pt;")
        self.press_moy_value.setAlignment(Qt.AlignRight)
        moy_lab = QLabel("(Moy)")
        moy_lab.setAlignment(Qt.AlignRight)
        moy_lab.setStyleSheet("color: white; font-size: 13pt;")
        press_unite.setStyleSheet("color: white; font-size: 13pt;")
        p_l_hbox = QHBoxLayout()
        p_l_hbox.addWidget(press_unite, stretch=2)
        p_l_hbox.addStretch()
        p_l_hbox.addWidget(moy_lab, stretch=1)
        v_h_layout = QHBoxLayout()
        v_h_layout.addStretch(1)
        self.pni_label = QLabel("--/--")
        self.pni_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.pni_label.setStyleSheet("font-size: 40pt; color: white;")
        self.mesure_label = QLabel("Pompage")
        self.mesure_label.setContentsMargins(10, 0, 0, 5)
        self.mesure_label.setStyleSheet("font-size: 10pt; color: white;")
        v_h_layout.addWidget(self.pni_label, stretch=2)
        v_h_layout.addStretch()
        v_h_layout.addWidget(self.press_moy_value, stretch=1)
        self.pression_layout.addLayout(p_l_hbox)
        self.pression_layout.addLayout(v_h_layout)
        self.pression_layout.addWidget(self.mesure_label, stretch=1)

        self.sat_layout = QVBoxLayout(self.conteneur_saturation)
        self.sat_layout.setContentsMargins(0, 0, 0, 0)
        sat_lab = QLabel("SpO2")
        sat_unite = QLabel("pulse")
        sat_lab.setAlignment(Qt.AlignLeft)
        sat_unite.setAlignment(Qt.AlignRight)
        sat_lab.setStyleSheet("color: #FF500A; font-size: 13pt;")
        sat_unite.setStyleSheet("color: #FF500A; font-size: 13pt;")
        self.sat_label = QLabel("--", self)
        self.hr_in_sat = QLabel("HR")
        percent_lab = QLabel("%")
        percent_lab.setStyleSheet("color: #FF500A; font-size: 14pt;")
        first_ligne = QHBoxLayout()
        first_ligne.setContentsMargins(0, 0, 0, 0)
        first_ligne.addWidget(sat_lab, 1)
        first_ligne.addStretch(2)
        first_ligne.addWidget(sat_unite, 1)
        sec_ligne = QHBoxLayout()
        sec_ligne.addStretch()
        sec_ligne.setContentsMargins(0, 0, 0, 0)
        sec_ligne.addWidget(self.sat_label)
        sec_ligne.addWidget(percent_lab)
        sec_ligne.addStretch()
        self.sat_label.setAlignment(Qt.AlignRight)
        self.hr_in_sat.setAlignment(Qt.AlignBottom)
        self.hr_in_sat.setStyleSheet('color: #33FF57; font-size: 16pt; font-weight: bold;')
        self.sat_label.setStyleSheet("color: #FF500A; font-weight: bold; font-size: 55pt;")
        self.sat_layout.addLayout(first_ligne)
        self.sat_layout.addLayout(sec_ligne)
        self.sat_layout.addWidget(self.hr_in_sat, alignment=Qt.AlignRight)

        layout_resp_temp = QHBoxLayout()
#RESPIRATION
        self.resp_layout = QVBoxLayout(self.conteneur_resp)
        self.resp_layout.setContentsMargins(0, 0, 0, 0)
        self.resp_label = QLabel("--", self)
        self.resp_label.setAlignment(Qt.AlignRight)
        self.resp_label.setStyleSheet("color: #DFEE0A; font-size: 40pt;")
        resp_ligne1 = QHBoxLayout()
        resp_ligne2 = QHBoxLayout()
        param_name = QLabel("RESP")
        param_name.setStyleSheet("color: #DFEE0A; font-size: 13pt;")
        param_name.setAlignment(Qt.AlignLeft)
        self.seuil_resp_label = QLabel()
        self.seuil_resp_label.setAlignment(Qt.AlignRight)
        self.seuil_resp_label.setStyleSheet("color: #DFEE0A; font-size: 11pt;")
        self.seuil_resp_label.setText(f"{PARAMS_SEUILS[3]['val_max']}\n{PARAMS_SEUILS[3]['val_min']}")
        resp_ligne1.addWidget(param_name, stretch=1)
        resp_ligne1.addWidget(self.seuil_resp_label, stretch=2)
        unit_resp = QLabel("rpm")
        unit_resp.setStyleSheet("color: #DFEE0A; font-size: 11pt;")
        unit_resp.setAlignment(Qt.AlignLeft)
        resp_ligne2.addStretch()
        resp_ligne2.addWidget(self.resp_label, stretch=1)
        resp_ligne2.addWidget(unit_resp, stretch=1)
        resp_ligne2.addStretch()
        self.resp_layout.addLayout(resp_ligne1)
        self.resp_layout.addStretch()
        self.resp_layout.addLayout(resp_ligne2)
        self.resp_layout.addStretch()

#TEMPERATURE
        self.temp_layout = QVBoxLayout(self.conteneur_temp)
        self.temp_layout.setContentsMargins(0, 0, 0, 0)
        self.temp_label = QLabel("--", self)
        self.temp_label.setAlignment(Qt.AlignRight)
        self.temp_label.setStyleSheet("color: #2093FF; font-size: 22pt;")
        temp_param = QLabel("TEMP")
        temp_param.setAlignment(Qt.AlignRight)
        temp_param.setStyleSheet("color: #2093FF; font-size: 13pt;")
        ligne = QHBoxLayout()
        unite = QLabel("°C")
        unite.setAlignment(Qt.AlignLeft)
        unite.setStyleSheet("color: #2093FF; font-size: 11pt;")
        ligne.addStretch()
        ligne.addWidget(self.temp_label, stretch=1)
        ligne.addWidget(unite, stretch=1)
        ligne.addStretch()
        self.temp_layout.addWidget(temp_param)
        self.temp_layout.addStretch()
        self.temp_layout.addLayout(ligne)
        self.temp_layout.addStretch()


        layout_resp_temp.addWidget(self.conteneur_resp, stretch=1)
        layout_resp_temp.addWidget(self.conteneur_temp, stretch=1)

        box_layout = QVBoxLayout()
        box_layout.addWidget(self.conteneur_ecg, stretch=3)
        box_layout.addWidget(self.conteneur_saturation, stretch=3)
        box_layout.addLayout(layout_resp_temp, stretch=3)

        self.log_widget = LogWidget(self)
        history_layout.addWidget(self.log_widget)

        self.layout1.addLayout(box_layout, stretch=2)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.plot_widget = pg.PlotWidget()
        bg_color = COLOR_THEME['default']['container-color']
        self.plot_widget.setBackground(background=bg_color)
        self.plot_widget.showGrid(x=False, y=False)
        self.plot_widget.setYRange(-1.5, 1.5)
        plot_item = self.plot_widget.getPlotItem()
        plot_item.getAxis('left').setVisible(False)
        plot_item.getAxis('bottom').setVisible(False)

        curve_infos = [
            {'name': 'ECG', 'color': 'lime'},
            {'name': 'SPO2', 'color': '#FF500A'},
            {'name': 'RESP', 'color': '#DFEE0A'},
        ]
        for infos in curve_infos:
            label = None
            if infos['name']=='ECG':
                label = pg.TextItem(text=infos['name'], color=infos['color'], anchor=(0, 10))
            elif infos['name'] == 'SPO2':
                label = pg.TextItem(text=infos['name'], color=infos['color'], anchor=(0, 3))          
            else:
                label = pg.TextItem(text=infos['name'], color=infos['color'], anchor=(0, -3))
            label.setPos(self.ecg.x_data[0], self.ecg.buffer[0])
            self.plot_widget.addItem(label)

        self.curve_resp = self.plot_widget.plot(pen=pg.mkPen(color='#DFEE0A', width=3))
        self.curve_ecg = self.plot_widget.plot(pen=pg.mkPen(color='lime', width=3))
        self.curve_spo2 = self.plot_widget.plot(pen=pg.mkPen(color='#FF500A', width=3))

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.plot_widget, stretch=6)

        bottom_right_layout = QHBoxLayout()
        bottom_right_layout.addWidget(self.conteneur_pression, stretch=2)
        bottom_right_layout.addWidget(self.conteneur_history, stretch=2)

        right_layout.addLayout(bottom_right_layout, stretch=2)

        self.layout1.addLayout(right_layout, stretch=4)

        self.layout_app.addLayout(self.layout1, stretch=14)

        self.layout_app.addWidget(self.bottom_app)

        self.centralWidget.setLayout(self.layout_app)

        self.ecg.reset_buffer()
        self.saturation.reset_buffer()
        self.respiration.reset_buffer()

        self.curve_ecg.setData(self.ecg.x_data, self.ecg.buffer + 0.9)
        self.curve_spo2.setData(self.saturation.x_data, self.saturation.get_display_data() - 0.35)
        self.curve_resp.setData(self.respiration.x_data, self.respiration.get_display_data() - 1.25)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.timer_txt = QTimer()
        self.timer_txt.timeout.connect(self.update_txt)

        self.timer_heart = QTimer()
        self.timer_heart.timeout.connect(self.update_logo)

        self.timer_log = QTimer()
        self.timer_log.timeout.connect(self.update_log)

        self.timer_buffer_tosend = QTimer()
        self.timer_buffer_tosend.timeout.connect(self.update_data_to_send)

        self.timer_temp = QTimer()
        self.timer_temp.timeout.connect(self.duree_exam)

        self.timer_txt.start(1)
        self.timer_heart.start(500)
        self.timer_log.start(1000)
        self.timer_buffer_tosend.start(100)
        self.timer_temp.start(1000)
        self.timer.start(self.ecg.update_interval)
        self.heure_debut = self.date.text()

        self.setStyleSheet(f"background-color: {COLOR_THEME['default']['app-color']}; font-family: {COLOR_THEME['default']['font-family']};")

    def new_data_from_serial(self, raw_data):
        self.data_from_serial = raw_data
        print(self.data_from_serial)
        if not self.simul_state:
            self.ecg.bpm = int(raw_data['ecg'])
            self.saturation.spo2_val = int(raw_data['sat'])
            self.respiration.resp_rate = int(raw_data['resp'])
            self.temperature.temperature = int(raw_data['temp'])
            self.pression.pam = int(raw_data['pni_moy'])
            self.pression.diasto = int(raw_data['diastol'])
            self.pression.systo = int(raw_data['systol'])

            self.ecg_label.setText(str(self.ecg.bpm))
            self.sat_label.setText(str(self.saturation.spo2_val))
            self.temp_label.setText(str(self.temperature.temperature))
            self.resp_label.setText(str(self.respiration.resp_rate))
            self.press_moy_value.setText(str(self.pression.pam))

    def pression_processed(self):
        if not self.simul_state:
            self.log_widget.ajouter_valeur()

    def error_from_serial(self, error):
        print(error)

    def setup_animations(self):
        self.animations = {}
        self.effects = {}

        # Dictionnaire pour mapper les signaux aux conteneurs
        self.map_conteneurs = {
            "hr": self.conteneur_ecg,
            "spo2": self.conteneur_saturation,
            "resp": self.conteneur_resp,
            "temp": self.conteneur_temp,
        }

        for key, widget in self.map_conteneurs.items():
            # Créer un effet de coloration
            eff = QGraphicsColorizeEffect(widget)
            widget.setGraphicsEffect(eff)
            eff.setEnabled(False)  # Désactivé par défaut
            self.effects[key] = eff

            # Créer l'animation de clignotement (Rouge)
            anim = QPropertyAnimation(eff, b"color")
            anim.setDuration(500)
            anim.setStartValue(QColor(Qt.red))
            anim.setEndValue(QColor(0, 0, 0, 0))  # Retour à l'original
            anim.setLoopCount(-1)  # Infini tant que l'alerte est là
            self.animations[key] = anim

    def gerer_alerte_visuelle(self, param, en_alerte):
        if en_alerte:
            self.alerte_status = True
            if not self.animations[param].state() == QPropertyAnimation.Running:
                self.effects[param].setEnabled(True)
                self.animations[param].start()
                # Optionnel : changer le texte de l'alarme en haut
                self.alarm_lab.setText(f"ALERTE : {param.upper()} HORS SEUILS")
                self.alarm_lab.setStyleSheet("background-color: red; color: white; font-size: 12pt;")
        else:
            self.alerte_status = False
            self.animations[param].stop()
            self.effects[param].setEnabled(False)

    def get_infos_patient(self):
        if not self.simul_state:
            self.app_infos_patient.show()
            if self.app_infos_patient.exec_() == QDialog.Accepted:
                datas = self.app_infos_patient.get_data()
                patient_info_path = os.path.join(PROJECT_ROOT, 'datas', 'patient_infos.txt')
                with open(patient_info_path, 'w+') as patient_file:
                    patient_file.write(datas['nom'])
                    patient_file.write("_")
                    patient_file.write(datas['id'])
                    patient_file.write("_")
                    patient_file.write(str(datas['age']))
                    patient_file.write("_")
                    patient_file.write(datas['sexe'])
                    patient_file.write("_")
                    patient_file.write(str(datas['poids']))
                    patient_file.write("_")
                    patient_file.write(str(datas['taille']))
                    patient_file.write("_")
                    patient_file.write(str(datas['salle']))
                    patient_file.write("_")
                    patient_file.write(datas['service'])
                    patient_file.write("_")
                    patient_file.write(datas['medecin'])
                    patient_file.write("_")
                    patient_file.write(self.heure_debut)

                patient_info_path = os.path.join(PROJECT_ROOT, 'datas', 'patient_infos.txt')
                with open(patient_info_path, 'r+') as patient_file:
                    line = patient_file.readline()
                    datas = line.split('_')
                    resume_for_lab_patient = f"{datas[0]}\nID. {datas[1]} {datas[6]}. {datas[7]}"
                    self.infos_patient.setText(resume_for_lab_patient)
        else:
            self.app_infos_patient.hide()

    def add_patient(self):
        if self.admission_patient.exec_() == QDialog.Accepted:
            messagebox = QMessageBox()
            messagebox.setIcon(QMessageBox.Information)
            messagebox.setText("Enregistrez d'abord les données du patient actuel!")
            messagebox.setStandardButtons(QMessageBox.Yes)
            messagebox.setDefaultButton(QMessageBox.Yes)
            messagebox.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
            if messagebox.exec_() == QDialog.Accepted:
                self.status_saved = True

    def start_transfert(self):
        messagebox = QMessageBox()
        messagebox.setIcon(QMessageBox.Information)
        messagebox.setText("Voulez vous commencer l'enregistrement des données du patient actuel sur le serveur distant ?")
        messagebox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        messagebox.setDefaultButton(QMessageBox.Yes)
        messagebox.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        if messagebox.exec_() == QMessageBox.Yes:
            self.scanner.show()

    def open_param_box(self):
        self.configbox = ConfigBox()
        if self.configbox.exec_()==QDialog.Accepted:
            if not self.hasFocus():
                self.simul_state = self.configbox.get_state()
                self.theme = self.configbox.getThemeSelected()
                self.repaintUi()
                if self.next_simul_state and not self.simul_state:
                    pass

    def repaintUi(self):
        if not self.theme:
            return
        self.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['app-color']}; font-family: {COLOR_THEME[self.theme]['font-family']};")
        #self.plot_widget.setBackground(f"{COLOR_THEME[self.theme]['container-color']};")
        self.conteneur_ecg.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")
        self.conteneur_pression.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")
        self.conteneur_saturation.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")
        self.conteneur_resp.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")
        self.conteneur_temp.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")
        self.conteneur_history.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")
        self.top_app.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")

    def update_time(self):
        self.date.setText(datetime.now().strftime("%H:%M:%S"))

    def update_txt(self):
        if self.simul_state:
            self.ecg_label.setText(str(f"{self.ecg.bpm}"))
            self.sat_label.setText(str(f"{self.saturation.spo2_val}"))
            self.pni_label.setText(str(f"{self.pression.systo}/{self.pression.diasto}"))
            self.temp_label.setText(str(f"{self.temperature.temperature}"))
            self.resp_label.setText(str(f"{self.respiration.rpm}"))
            self.press_moy_value.setText(str(f"{self.pression.pam}"))
            self.hr_in_sat.setText(str(f"{self.ecg.bpm}")+' bpm')
            self.infos_patient.setText('Mode Démo')
        #on met à jour l'icone du wifi
        if self.scanner.connected_to_server:
            self.label_wifi.setPixmap(QPixmap(self.wifi_on))
        else:
            self.label_wifi.setPixmap(QPixmap(self.wifi_off))

    def update_log(self):
        if self.simul_state:
            self.log_widget.ajouter_valeur()

    def update_logo(self):
        if self.simul_state:
            if self.state_heart:
                heart_off_path = os.path.join(PROJECT_ROOT, 'assets', self.heart_off)
                self.logo_label.setPixmap(QPixmap(heart_off_path))
                self.state_heart = False
            else:
                heart_on_path = os.path.join(PROJECT_ROOT, 'assets', self.heart_on)
                self.logo_label.setPixmap(QPixmap(heart_on_path))
                self.state_heart = True
        self.storage()

    def update(self):
        if self.simul_state:
            self.ecg.get_mit_data()
            self.ecg.update_data()

            self.saturation.update_data()
            self.respiration.update_data()

            self.curve_ecg.setData(self.ecg.x_data, self.ecg.buffer+0.9)
            self.curve_spo2.setData(self.saturation.x_data, self.saturation.get_display_data() - 0.35)
            self.curve_resp.setData(self.respiration.x_data, self.respiration.get_display_data()-1.25)
            try:
                self.plot_widget.setXRange([-self.ecg.x_data, self.ecg.x_data])
            except TypeError as e:
                #print(f"Erreur de type: {e}")
                pass
        else:
            try:
                self.ecg.buffer[self.ecg.ptr] = self.data_from_serial['buffer_ecg']
                self.respiration.display_buffer[self.respiration.ptr] = self.data_from_serial['buffer_resp']
                self.saturation.display_buffer[self.saturation.ptr] = self.data_from_serial['buffer_sat']
            except KeyError as e:
                print(str(e))
            #mise à jour
            gap_size = 30  # Nombre de points à effacer devant
            for i in range(1, gap_size + 1):
                idx_to_clearE = (self.ecg.ptr + i) % self.ecg.maxpoint
                idx_to_clearS = (self.ecg.ptr + i) % self.saturation.maxpoint
                idx_to_clearR = (self.ecg.ptr + i) % self.respiration.maxpoint
                self.ecg.buffer[idx_to_clearE] = np.nan  # Efface la vieille donnée
                self.saturation.display_buffer[idx_to_clearS] = np.nan
                self.respiration.display_buffer[idx_to_clearR] = np.nan
            self.ecg.ptr = (self.ecg.ptr + 1) % self.ecg.maxpoint
            self.saturation.ptr = (self.saturation.ptr + 1) % self.saturation.maxpoint
            self.respiration.ptr = (self.respiration.ptr + 1) % self.respiration.maxpoint
            self.curve_ecg.setData(self.ecg.x_data, self.ecg.buffer + 0.9)
            self.curve_spo2.setData(self.saturation.x_data, self.saturation.get_display_data() - 0.35)
            self.curve_resp.setData(self.respiration.x_data, self.respiration.get_display_data()-1.25)

    def update_data_to_send(self):
        if len(self.data_to_transfer['hr'])>20:
            self.data_to_transfer['hr'].pop(0)
        self.data_to_transfer['hr'].append(self.ecg.bpm)
        if len(self.data_to_transfer['sat'])>20:
            self.data_to_transfer['sat'].pop(0)
        self.data_to_transfer['sat'].append(self.saturation.spo2_val)
        if len(self.data_to_transfer['temp'])>20:
            self.data_to_transfer['temp'].pop(0)
        if len(self.data_to_transfer['resp'])>20:
            self.data_to_transfer['resp'].pop(0)
        #self.data_to_transfer['pni']['systo'].append(self.pression.systo)
        #self.data_to_transfer['pni']['diasto'].append(self.pression.diasto)
        #self.data_to_transfer['pni']['pam'].append(self.pression.pam)
        self.data_to_transfer['temp'].append(self.temperature.temperature)
        self.data_to_transfer['resp'].append(self.respiration.rpm)

    def duree_exam(self):
        self.duration_count+=1
        hours, minutes, seconds = calculate_time_format(self.duration_count)
        hours = "0" + str(hours) if hours < 10 else str(hours)
        minutes = "0" + str(minutes) if minutes < 10 else str(minutes)
        seconds = "0" + str(seconds) if seconds < 10 else str(seconds)
        self.duree_label.setText(f"{hours}:{minutes}:{seconds}")

    def pause(self):
        if not self.pause_state:
            self.timer.stop()
            self.timer_heart.stop()
            self.timer_txt.stop()
            self.pause_state = True
        else:
            self.timer.start()
            self.timer_heart.start()
            self.timer_txt.start()
            self.pause_state = False

    def storage(self):
        num_car = 5
        file_name = os.path.join(PROJECT_ROOT, 'datas', 'base_donnees.txt')
        debut = datetime.now().strftime("the %d/%m/%Y at %H:%M:%S")
        with open(file_name, "a+") as f:
            f.write('<HR>')
            if not self.ecg_label.text()[0] == '-':
                f.write(self.ecg_label.text())
            f.write('</HR>')
            f.write('<SPO2>')
            if not self.sat_label.text()[0] == '-':
                f.write(self.sat_label.text())
            f.write('</SPO2>')
            f.write('<RESP>')
            if not self.resp_label.text()[0] == '-':
                f.write(self.resp_label.text())
            f.write('</RESP>')
            f.write('<TEMP>')
            if not self.temp_label.text()[0] == '-':
                f.write(self.temp_label.text())
            f.write('</TEMP>')
            f.write('<PNI>')
            if not self.pni_label.text()[0] == '-':
                f.write('<SYS>')
                f.write(self.pni_label.text().split("/")[0])
                f.write('</SYS>')
                f.write('<DIAS>')
                f.write(self.pni_label.text().split("/")[1])
                f.write('</DIAS>')
                f.write('<PAM>')
                if not self.press_moy_value.text()[0] == '-':
                    f.write(self.press_moy_value.text())
                f.write('</PAM>')
            f.write('</PNI>')
            f.write('<TIMESTAMP>')
            f.write(self.duree_label.text())
            f.write('</TIMESTAMP>')
            f.write("\n")
        f.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Dashboard()
    window.showFullScreen()
    sys.exit(app.exec_())
import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QAction, QLabel, QToolBar, QVBoxLayout, QHBoxLayout, QGroupBox, QDialog, QPushButton)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap
from datetime import datetime
from definitions.templates_params import Ecg, Saturation, Respiration, Pression, Temperature
from GUI.patient_infos import FenetrePatient
from definitions.erreur_seuils import ParamError, ENUM_LIST_SEUILS
from utilities.preferences import COLOR_THEME, PARAMS_SEUILS
from GUI.label_cliquable import LabelCliquable
from GUI.configs import ConfigBox
from GUI.log_widget import LogWidget
from GUI.admission_patient import AdmissionPatient

class Dashboard(QMainWindow):

    """La classe qui définie l'interface principale du moniteur"""

    def __init__(self):
        super().__init__()
        self.ecg = Ecg()
        self.saturation = Saturation()
        self.respiration = Respiration()
        self.pression = Pression()
        self.temperature = Temperature()
        self.time_h = None
        self.name_patient = None
        self.date = None
        self.barre_etat = None
        self.timer_infos = None
        self.state_heart = None

        self.pause_state = False

        self.liste_boutons_cmd = []

        self.simul_state = False

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

        self.setWindowTitle("Moniteur")
        self.setGeometry(10, 10, 800, 400)
        self.buildUI()
        self.setContentsMargins(0, 0, 0, 0)

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

        self.settings = LabelCliquable()
        self.settings.clique.connect(self.open_param_box)
        self.settings.setStyleSheet('background-color: #0055AA;')

        self.date = QLabel(datetime.now().strftime("%H:%M:%S"), self)
        #self.date.setAlignment(Qt.AlignLeft)

        self.utilitaires = QWidget()

        layout_util = QHBoxLayout(self.utilitaires)
        layout_util.addWidget(self.date, stretch=2)
        layout_util.addStretch(3)
        layout_util.addWidget(self.settings, stretch=1)

        self.utilitaires.setStyleSheet("color: white; font-size: 12pt;")

        layout_top.addWidget(self.infos_patient, stretch=1)
        layout_top.addWidget(self.alarm_lab, stretch=2)
        layout_top.addWidget(self.utilitaires, stretch=1)

        self.layout_app.addWidget(self.top_app, stretch=1)

        txt_buttons = ["Silence", "Pause", "Démarrer PNI", "Enregistrer", "Patient", "Paramètres"]
        icons_buttons = [os.path.join(PROJECT_ROOT, 'assets', 'silence.png'), os.path.join(PROJECT_ROOT, 'assets', 'pause.png'), os.path.join(PROJECT_ROOT, 'assets', 'pni.png'), os.path.join(PROJECT_ROOT, 'assets', 'save.png'), os.path.join(PROJECT_ROOT, 'assets', 'patient.png'), os.path.join(PROJECT_ROOT, 'assets', 'gear.png')]

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
            elif button.text() == "Paramètres":
                button.clicked.connect(self.open_param_box)
            elif button.text() == "Pause":
                button.clicked.connect(self.pause)

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
        self.conteneur_resp_temp = QWidget()
        self.conteneur_resp_temp.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")
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
        self.press_moy_value = QLabel("__")
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
        self.sat_label = QLabel("__", self)
        self.hr_in_sat = QLabel("HR")
        percent_lab = QLabel("%")
        percent_lab.setStyleSheet("color: #FF500A; font-size: 13pt;")
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

        self.temp_layout = QHBoxLayout(self.conteneur_resp_temp)
        self.temp_layout.setContentsMargins(0, 0, 0, 0)
        self.resp_label = QLabel("--", self)
        self.resp_label.setAlignment(Qt.AlignCenter)
        self.resp_label.setStyleSheet("color: #DFEE0A; font-size: 40pt;")
        self.temp_label = QLabel("--", self)
        self.temp_label.setAlignment(Qt.AlignBottom)
        self.temp_label.setStyleSheet("color: #2093FF; font-size: 22pt; padding: 15px")
        resp_lay = QVBoxLayout()
        temp_lay = QVBoxLayout()
        self.seuil_resp_label = QLabel()
        self.seuil_resp_label.setAlignment(Qt.AlignRight)
        self.seuil_resp_label.setStyleSheet("color: #DFEE0A; font-size: 11pt;")
        self.seuil_resp_label.setText(f"{PARAMS_SEUILS[3]['val_max']}\n{PARAMS_SEUILS[3]['val_min']}")
        unit_t = QLabel("TEMP")
        unit_t.setAlignment(Qt.AlignRight)
        unit_t.setStyleSheet("color: #2093FF; font-size: 13pt;")
        temp_lay.addWidget(unit_t)
        temp_lay.addWidget(self.temp_label, alignment=Qt.AlignRight)
        unite_lay = QHBoxLayout()
        unit = QLabel("RESP")
        unit_1 = QLabel("resp/min")
        unit.setAlignment(Qt.AlignLeft)
        unit_1.setAlignment(Qt.AlignRight)
        unit.setStyleSheet("color: #DFEE0A; font-size: 13pt;")
        unit_1.setStyleSheet("color: #DFEE0A; font-size: 13pt;")
        unite_lay.addWidget(unit, alignment=Qt.AlignLeft)
        unite_lay.addWidget(unit_1, alignment=Qt.AlignRight)
        resp_lay.addLayout(unite_lay)
        resp_lay.addWidget(self.seuil_resp_label)
        resp_lay.addWidget(self.resp_label, alignment=Qt.AlignCenter)
        resp_lay.addWidget(QLabel())
        temp_lay.addWidget(QLabel())
        self.temp_layout.addLayout(resp_lay)
        self.temp_layout.addLayout(temp_lay)

        box_layout = QVBoxLayout()
        box_layout.addWidget(self.conteneur_ecg, stretch=3)
        box_layout.addWidget(self.conteneur_saturation, stretch=3)
        box_layout.addWidget(self.conteneur_resp_temp, stretch=2)

        self.log_widget = LogWidget()
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

        self.curve_resp = self.plot_widget.plot(pen=pg.mkPen(color='#DFEE0A', width=5))
        self.curve_ecg = self.plot_widget.plot(pen=pg.mkPen(color='lime', width=5))
        self.curve_spo2 = self.plot_widget.plot(pen=pg.mkPen(color='#FF500A', width=5))

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

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.timer_txt = QTimer()
        self.timer_txt.timeout.connect(self.update_txt)

        self.timer_heart = QTimer()
        self.timer_heart.timeout.connect(self.update_logo)

        self.timer_log = QTimer()
        self.timer_log.timeout.connect(self.update_log)

        self.timer_txt.start(1)
        self.timer_heart.start(250)
        self.timer_log.start(1000)

        self.setStyleSheet(f"background-color: {COLOR_THEME['default']['app-color']}; font-family: {COLOR_THEME['default']['font-family']};")

    def get_infos_patient(self):
        self.app_infos_patient.show()
        if self.app_infos_patient.exec_() == QDialog.Accepted:
            datas = self.app_infos_patient.get_data()
            patient_info_path = os.path.join(PROJECT_ROOT, 'datas', 'patient_infos.txt')
            with open(patient_info_path, 'w+') as patient_file:
                #patient_file.write("")
                patient_file.write(datas['nom']);patient_file.write("_");patient_file.write(datas['id']);patient_file.write("_");patient_file.write(str(datas['age']));patient_file.write("_");patient_file.write(datas['sexe']);patient_file.write("_");patient_file.write(str(datas['poids']));patient_file.write("_");patient_file.write(str(datas['taille']));patient_file.write("_");
                patient_file.write(str(datas['salle'])); patient_file.write("_"); patient_file.write(datas['service'])
                patient_file.write("\n")

            patient_info_path = os.path.join(PROJECT_ROOT, 'datas', 'patient_infos.txt')
            with open(patient_info_path, 'r+') as patient_file:
                line = patient_file.readline()
                datas = line.split('_')
                resume_for_lab_patient = f"{datas[0]}\nID. {datas[1]} {datas[6]}. {datas[7]}"
                self.infos_patient.setText(resume_for_lab_patient)

    def add_patient(self):
        self.admission_patient.show();
        if self.admission_patient.exec_() == QDialog.Accepted:
            pass

    def open_param_box(self):
        self.configbox = ConfigBox()
        if self.configbox.exec_()==QDialog.Accepted:
            if not self.hasFocus():
                self.simul_state = self.configbox.get_state()
                self.timer.start(self.ecg.update_interval)
                self.theme = self.configbox.getThemeSelected()
                self.repaintUi()

    def repaintUi(self):
        if not self.theme:
            return
        self.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['app-color']}; font-family: {COLOR_THEME[self.theme]['font-family']};")
        #self.plot_widget.setBackground(f"{COLOR_THEME[self.theme]['container-color']};")
        self.conteneur_ecg.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")
        self.conteneur_pression.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")
        self.conteneur_saturation.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")
        self.conteneur_resp_temp.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")
        self.conteneur_history.setStyleSheet(f"background-color: {COLOR_THEME[self.theme]['container-color']}; border-radius: 20px;")

    def update_time(self):
        self.date.setText(datetime.now().strftime("%H:%M:%S"))
        if self.simul_state:
            self.alarm_lab.setText('Mode Démo')
            self.alarm_lab.setStyleSheet('color: white; font-size: 13pt; background-color: #999950')
        else:
            self.alarm_lab.setText('Alarmes')
            self.alarm_lab.setStyleSheet('color: white; font-size: 13pt; background-color: #0055AA')

    def update_txt(self):
        if self.simul_state:
            self.ecg_label.setText(str(f"{self.ecg.bpm}"))
            self.sat_label.setText(str(f"{self.saturation.spo2_val}"))
            self.pni_label.setText(str(f"{self.pression.systo}/{self.pression.diasto}"))
            self.temp_label.setText(str(f"{self.temperature.temperature}")+" °C")
            self.resp_label.setText(str(f"{self.respiration.rpm}"))
            self.press_moy_value.setText(str(f"{self.pression.pam}"))
            self.hr_in_sat.setText(str(f"{self.ecg.bpm}")+' bpm')
        self.storage()

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

    def update(self):
        if self.simul_state:
            self.ecg.get_mit_data()
            self.ecg.update_data()

            self.saturation.update_data()
            self.respiration.update_data()

            self.curve_ecg.setData(self.ecg.x_data, self.ecg.buffer+1)
            self.curve_spo2.setData(self.saturation.x_data, self.saturation.get_display_data())
            self.curve_resp.setData(self.respiration.x_data, self.respiration.get_display_data()-1.)
            self.plot_widget.setXRange([-self.ecg.x_data, self.ecg.x_data])
        else:
            pass

    def pause(self):
        if not self.pause_state:
            self.timer.stop()
            self.timer_infos.stop()
            self.timer_heart.stop()
            self.timer_txt.stop()
            self.pause_state = True
        else:
            self.timer.start()
            self.timer_infos.start()
            self.timer_heart.start()
            self.timer_txt.start()
            self.pause_state = False

    def storage(self):
        num_car = 5
        file_name = os.path.join(PROJECT_ROOT, 'datas', 'base_donnees.txt')
        debut = datetime.now().strftime("the %d/%m/%Y at %H:%M:%S")
        with open(file_name, "w+") as f:
            for i in range(num_car):
                f.write('-')
            f.write("Beginning of transmission at "+debut)
            for i in range(num_car):
                f.write('-')
            f.write('<HR>')
            f.write(str(self.ecg._get_data_()[len(self.ecg._get_data_())-1]))
            f.write('</HR>')
            f.write('<SPO2>')
            f.write(str(self.ecg._get_data_()[len(self.ecg._get_data_())-1]))
            f.write('</SPO2>')
            for i in range(num_car):
                f.write('-')
            f.write("End of transmission")
            for i in range(num_car):
                f.write('-')
            f.write("\n")
        f.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Dashboard()
    window.showFullScreen()
    sys.exit(app.exec_())
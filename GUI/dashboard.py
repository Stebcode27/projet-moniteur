import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QAction, QLabel, QToolBar, QVBoxLayout, QHBoxLayout, QGroupBox, QDialog, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from datetime import datetime
from definitions.templates_params import Ecg
from GUI.patient_infos import FenetrePatient
from definitions.erreur_seuils import ParamError, ENUM_LIST_SEUILS
from utilities.preferences import COLOR_THEME

class Dashboard(QMainWindow):

    def __init__(self):
        super().__init__()
        self.max_points = 100
        self.data_y = np.zeros(self.max_points)
        self.ptr=0
        self.update_interval = 75
        self.time_h = None
        self.name_patient = None
        self.date = None
        self.barre_etat = None
        self.timer_infos = None
        self.state_heart = None
        self.hours = None

        self.heart_on, self.heart_off = "heart_on.png", "heart_off.png"
        self.state_heart = True

        self.layout_app = QVBoxLayout()

        self.app_infos_patient = FenetrePatient()

        self.error_modal_app = None

        self.setWindowTitle("Moniteur")
        self.setGeometry(10, 10, 800, 400)
        self.buildUI()

    def buildUI(self):
        """Fonction pour la construction du dashboard"""
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.barre_etat = self.statusBar()
        self.date = QLabel(datetime.now().strftime("%H:%M le %d/%m/%Y"), self)
        self.date.setAlignment(Qt.AlignLeft)
        self.barre_etat.setStyleSheet(f"color: white; font-size: 20px; padding: 10px; background: {COLOR_THEME['default']['container-color']}")
        self.name_patient = QLabel("Patient Name (Adult)", self)
        self.name_patient.setAlignment(Qt.AlignCenter)
        self.settings = QLabel(self)
        self.settings.setAlignment(Qt.AlignRight)
        settings_icon_path = os.path.join(PROJECT_ROOT, 'assets', 'gear.png')
        self.settings.setPixmap(QPixmap(settings_icon_path))

        self.barre_etat.addWidget(self.date, stretch=1)
        self.barre_etat.addWidget(self.name_patient, stretch=2)
        self.barre_etat.addWidget(self.settings, stretch=1)
        self.time_h = QTimer()
        self.time_h.timeout.connect(self.update_time)
        self.time_h.start(999)

        #self.colors = ["#D7EE0A", "#220CE7"]

        self.layout1 = QHBoxLayout()

        #conteneurs pour les paramètres
        conteneur_ecg = QWidget()
        conteneur_ecg.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")
        conteneur_pression = QWidget()
        conteneur_pression.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")
        conteneur_saturation = QWidget()
        conteneur_saturation.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")
        conteneur_resp_temp = QWidget()
        conteneur_resp_temp.setStyleSheet(f"background-color: {COLOR_THEME['default']['container-color']}; border-radius: 20px;")
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        heart_on_path = os.path.join(PROJECT_ROOT, 'assets', self.heart_on)
        self.logo_label.setPixmap(QPixmap(heart_on_path))
        self.ecg_layout = QVBoxLayout(conteneur_ecg)
        self.ecg_layout.setContentsMargins(0, 0, 0, 0)
        self.ecg_layout.addWidget(self.logo_label)
        self.ecg_label = QLabel("--")
        self.ecg_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.ecg_label.setStyleSheet("font-size: 65pt; font-weight: bold; color: #33FF57; padding-bottom: 25px;")
        self.ecg_layout.addWidget(self.ecg_label)
        lay_unite_hr = QHBoxLayout(conteneur_ecg)
        unite_hr = QLabel("bpm")
        hr = QLabel("HR")
        hr.setStyleSheet("color: #33FF57; font-size: 15pt;")
        unite_hr.setStyleSheet("color: #33FF57; font-size: 15pt;")
        lay_unite_hr.addStretch(1)
        lay_unite_hr.addWidget(unite_hr, stretch=1, alignment=Qt.AlignCenter)
        lay_unite_hr.addWidget(hr, stretch=1, alignment=Qt.AlignRight)
        self.ecg_layout.addLayout(lay_unite_hr)

        self.pression_layout = QVBoxLayout(conteneur_pression)
        self.pression_layout.setContentsMargins(0, 0, 0, 0)
        press_unite = QLabel("NIBP (Dias/Sys)")
        press_unite.setAlignment(Qt.AlignLeft)
        self.press_moy_value = QLabel("__")
        self.press_moy_value.setStyleSheet("color: white; font-size: 25pt;")
        self.press_moy_value.setAlignment(Qt.AlignRight)
        moy_lab = QLabel("(Moy)")
        moy_lab.setAlignment(Qt.AlignRight)
        moy_lab.setStyleSheet("color: white; font-size: 12pt;")
        press_unite.setStyleSheet("color: white; font-size: 12pt;")
        p_l_hbox = QHBoxLayout()
        p_l_hbox.addWidget(press_unite, stretch=2)
        p_l_hbox.addStretch()
        p_l_hbox.addWidget(moy_lab, stretch=1)
        v_h_layout = QHBoxLayout()
        v_h_layout.addStretch(1)
        self.pni_label = QLabel("--/--")
        self.pni_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.pni_label.setStyleSheet("font-size: 35pt; color: white;")
        v_h_layout.addWidget(self.pni_label, stretch=2)
        v_h_layout.addStretch()
        v_h_layout.addWidget(self.press_moy_value, stretch=1)
        self.pression_layout.addLayout(p_l_hbox)
        self.pression_layout.addLayout(v_h_layout)
        self.pression_layout.addWidget(QLabel(""))

        self.sat_layout = QVBoxLayout(conteneur_saturation)
        self.sat_layout.setContentsMargins(0, 0, 0, 0)
        sat_lab = QLabel("SpO2")
        sat_unite = QLabel("pulse")
        sat_lab.setAlignment(Qt.AlignLeft)
        sat_unite.setAlignment(Qt.AlignRight)
        sat_lab.setStyleSheet("color: #FF500A; font-size: 12pt;")
        sat_unite.setStyleSheet("color: #FF500A; font-size: 12pt;")
        self.sat_label = QLabel("__", self)
        self.hr_in_sat = QLabel("HR")
        percent_lab = QLabel("%")
        percent_lab.setStyleSheet("color: #FF500A; font-size: 12pt;")
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
        self.hr_in_sat.setAlignment(Qt.AlignRight)
        self.hr_in_sat.setStyleSheet('color: #33FF57; font-size: 15pt; font-weight: bold;')
        self.sat_label.setStyleSheet("color: #FF500A; font-weight: bold; font-size: 50pt;")
        self.sat_layout.addLayout(first_ligne)
        self.sat_layout.addLayout(sec_ligne)
        self.sat_layout.addWidget(self.hr_in_sat)

        self.temp_layout = QHBoxLayout(conteneur_resp_temp)
        self.temp_layout.setContentsMargins(0, 0, 0, 0)
        self.resp_label = QLabel("--", self)
        self.resp_label.setAlignment(Qt.AlignCenter)
        self.resp_label.setStyleSheet("color: #DFEE0A; font-size: 35pt;")
        self.temp_label = QLabel("--", self)
        self.temp_label.setAlignment(Qt.AlignBottom)
        self.temp_label.setStyleSheet("color: #3020FF; font-size: 20pt; padding: 15px")
        resp_lay = QVBoxLayout()
        temp_lay = QVBoxLayout()
        unit_t = QLabel("TEMP")
        unit_t.setAlignment(Qt.AlignRight)
        unit_t.setStyleSheet("color: #3020FF; font-size: 12pt;")
        temp_lay.addWidget(unit_t)
        temp_lay.addWidget(self.temp_label, alignment=Qt.AlignRight)
        unite_lay = QHBoxLayout()
        unit = QLabel("RESP")
        unit_1 = QLabel("resp/min")
        unit.setAlignment(Qt.AlignLeft)
        unit_1.setAlignment(Qt.AlignRight)
        unit.setStyleSheet("color: #DFEE0A; font-size: 12pt;")
        unit_1.setStyleSheet("color: #DFEE0A; font-size: 12pt;")
        unite_lay.addWidget(unit, alignment=Qt.AlignLeft)
        unite_lay.addWidget(unit_1, alignment=Qt.AlignRight)
        resp_lay.addLayout(unite_lay, stretch=1)
        resp_lay.addWidget(self.resp_label, alignment=Qt.AlignCenter, stretch=2)
        resp_lay.addStretch(1)
        self.temp_layout.addLayout(resp_lay)
        self.temp_layout.addLayout(temp_lay)

        box_layout = QVBoxLayout()
        box_layout.addWidget(conteneur_ecg)
        box_layout.addWidget(conteneur_saturation)
        box_layout.addWidget(conteneur_resp_temp)
        box_layout.addWidget(conteneur_pression)

        self.layout1.addLayout(box_layout, stretch=2)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.plot_widget = pg.PlotWidget()
        bg_color = COLOR_THEME['default']['container-color']
        self.plot_widget.setBackground(bg_color)
        self.plot_widget.showGrid(x=False, y=False)
        self.plot_widget.setYRange(-1.5, 1.5)
        plot_item = self.plot_widget.getPlotItem()
        plot_item.getAxis('left').setVisible(False)
        plot_item.getAxis('bottom').setVisible(False)

        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='#DFEE0A', width=3), name="RESP")
        self.curve1 = self.plot_widget.plot(pen=pg.mkPen(color='g', width=2), name="ECG")
        self.curve2 = self.plot_widget.plot(pen=pg.mkPen(color='#FF500A', width=4), name="SpO2")

        self.layout1.addWidget(self.plot_widget, stretch=4)

        self.layout_app.addLayout(self.layout1, stretch=6)

        self.centralWidget.setLayout(self.layout_app)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.timer_txt = QTimer()
        self.timer_txt.timeout.connect(self.update_txt)

        self.timer_heart = QTimer()
        self.timer_heart.timeout.connect(self.update_logo)

        self.timer_infos = QTimer()
        self.timer_infos.timeout.connect(self.get_infos_patient)
        self.timer_infos.setSingleShot(True)
        self.timer_infos.start(500)

        self.setStyleSheet(f"background-color: {COLOR_THEME['default']['app-color']}; font-family: {COLOR_THEME['solar']['font-family']};")

    def get_infos_patient(self):
        self.app_infos_patient.show()
        if self.app_infos_patient.exec_() == QDialog.Accepted:
            self.timer.start(self.update_interval)
            self.timer_txt.start(1000)
            self.timer_heart.start(250)
            datas = self.app_infos_patient.get_data()
            patient_info_path = os.path.join(PROJECT_ROOT, 'datas', 'patient_infos.txt')
            with open(patient_info_path, 'w+') as patient_file:
                #patient_file.write("")
                patient_file.write(datas['nom']);patient_file.write("_");patient_file.write(datas['id']);patient_file.write("_");patient_file.write(str(datas['age']));patient_file.write("_");patient_file.write(datas['sexe']);patient_file.write("_");patient_file.write(str(datas['poids']));patient_file.write("_");patient_file.write(str(datas['taille']));patient_file.write("_");salle = datas['salle'].split(' ');
                try:
                    patient_file.write(str(salle[0])+str(salle[1]))
                except IndexError:
                    print("Erreur de données concernant la salle du patient")
                finally:
                    patient_file.write("\n")

            patient_info_path = os.path.join(PROJECT_ROOT, 'datas', 'patient_infos.txt')
            with open(patient_info_path, 'r+') as patient_file:
                line = patient_file.readline()
                datas = line.split('_')
                age = int(datas[2])
                self.name_patient.setText(datas[0]+" (Adult)") if age>=18 else self.name_patient.setText(datas[0]+ " (Mineur)")

    def update_time(self):
        self.hours.setText(datetime.now().strftime("%H:%M"))
        self.date.setText(datetime.now().strftime("%d/%m/%Y"))

    def update_txt(self):
        self.ecg_label.setText(str(f"{round(120*abs(self.data_y[len(self.data_y)-1]))}"))
        self.sat_label.setText(str(f"{100*abs(self.data_y[len(self.data_y)-1]):.2f}"))
        self.pni_label.setText(str(f"{round(200*abs(self.data_y[len(self.data_y)-1]))}")+"\n"+str(f"{round(180*abs(self.data_y[len(self.data_y)-1]/2))}"))
        self.temp_label.setText(str(f"{100*abs(self.data_y[len(self.data_y)-1]):.2f}")+" °C")
        self.resp_label.setText(str(f"{round(60*abs(self.data_y[len(self.data_y)-1]))}"))
        self.press_moy_value.setText(str(f"{round(abs(90*self.data_y[len(self.data_y)-1]))}"))
        self.hr_in_sat.setText(str(f"{round(120*abs(self.data_y[len(self.data_y)-1]))}")+' bpm')
        self.storage()

    def update_logo(self):
        if self.state_heart:
            heart_off_path = os.path.join(PROJECT_ROOT, 'assets', self.heart_off)
            self.logo_label.setPixmap(QPixmap(heart_off_path))
            self.state_heart = False
        else:
            heart_on_path = os.path.join(PROJECT_ROOT, 'assets', self.heart_on)
            self.logo_label.setPixmap(QPixmap(heart_on_path))
            self.state_heart = True

    def update(self):
        data_esp = Ecg()
        if(data_esp._get_data_()[0]==0):
            new_val = np.exp(-(self.ptr+1))+np.random.normal(size=1, scale=1, loc=0.5)*0.015
            self.data_y[:-1]=self.data_y[1:]
            try:        #possible erreur
                self.data_y[-1]=new_val
            except DeprecationWarning as e:
                pass
            finally:

                x_data = np.arange(self.ptr-self.max_points,self.ptr)
                self.curve.setData(x_data, self.data_y-1.25)
                self.curve1.setData(x_data, self.data_y+0.85)
                self.curve2.setData(x_data, self.data_y-0.25)
                self.plot_widget.setXRange(self.ptr-self.max_points,self.ptr)
                self.ptr+=5
                self.ptr%=50
                #self.verify_value_out_of_range()
        else:
            return

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
            f.write(str(self.data_y[len(self.data_y)-1]))
            f.write('</HR>')
            f.write('<SPO2>')
            f.write(str(self.data_y[len(self.data_y)-1]))
            f.write('</SPO2>')
            for i in range(num_car):
                f.write('-')
            f.write("End of transmission")
            for i in range(num_car):
                f.write('-')
            f.write("\n")
        f.close()

    def verify_value_out_of_range(self):
        err_value_app = ParamError("sat", self)
        value_sat = float(self.sat_label.text())
        value_ecg = float(self.ecg_label.text())
        value_temp = float(self.temp_label.text()[:len(self.temp_label.text()) - 2])
        value_resp = float(self.resp_label.text())
        value_pni = float(self.pni_label.text().split('\n')[0])
        if value_ecg > ENUM_LIST_SEUILS[0]:
            if self.app_infos_patient.exec_() == QDialog.Accepted:
                err_value_app.show()
        if value_sat > ENUM_LIST_SEUILS[1]:
            if self.app_infos_patient.exec_() == QDialog.Accepted:
                err_value_app.show()
        if value_pni > ENUM_LIST_SEUILS[2]:
            if self.app_infos_patient.exec_() == QDialog.Accepted:
                err_value_app.show()
        if value_temp > ENUM_LIST_SEUILS[3]:
            if self.app_infos_patient.exec_() == QDialog.Accepted:
                err_value_app.show()
        if value_resp > ENUM_LIST_SEUILS[4]:
            if self.app_infos_patient.exec_() == QDialog.Accepted:
                err_value_app.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Dashboard()
    window.showFullScreen()
    sys.exit(app.exec_())
import sys
import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QAction, QLabel, QToolBar, QVBoxLayout, QHBoxLayout, QGroupBox, QDialog, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from datetime import datetime
from definitions.templates_params import Ecg
from GUI.patient_infos import FenetrePatient
from definitions.erreur_seuils import ParamError, ENUM_LIST_SEUILS

class Dashboard(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moniteur")
        self.setGeometry(10, 10, 800, 400)
        self.buildUI()

    def buildUI(self):
        """Fonction pour la construction du dashboard"""
        self.barre_etat = self.statusBar()
        self.hours = QLabel(datetime.now().strftime("%H:%M"), self)
        self.hours.setAlignment(Qt.AlignLeft)
        self.date = QLabel(datetime.now().strftime("%d/%m/%Y"), self)
        self.date.setAlignment(Qt.AlignRight)
        self.barre_etat.addWidget(self.hours,stretch=1)
        self.barre_etat.setStyleSheet("color: white; font-size: 20px; padding: 10px; background: #0A0A0A;")
        self.name_patient = QLabel("Patient Name (Adult)", self)
        self.name_patient.setAlignment(Qt.AlignCenter)

        self.app_infos_patient = FenetrePatient()

        self.barre_etat.addWidget(self.name_patient, stretch=2)
        self.barre_etat.addWidget(self.date, stretch=1)
        self.time_h = QTimer()
        self.time_h.timeout.connect(self.update_time)
        self.time_h.start(999)

        self.colors = ["#D7EE0A", "#220CE7"]

        self.max_points = 250

        self.data_y = np.zeros(self.max_points)
        self.ptr=0
        self.update_interval = 50

        self.heart_on, self.heart_off = "heart_on.png", "heart_off.png"
        self.state_heart = True

        self.layout_app = QVBoxLayout()

        self.layout1 = QHBoxLayout()

        #conteneurs pour les paramètres
        conteneur_ecg = QWidget()
        conteneur_ecg.setStyleSheet("background-color: black; border-radius: 20px;")
        conteneur_pression = QWidget()
        conteneur_pression.setStyleSheet("background-color: black; border-radius: 20px;")
        conteneur_saturation = QWidget()
        conteneur_saturation.setStyleSheet("background-color: black; border-radius: 20px;")
        conteneur_resp_temp = QWidget()
        conteneur_resp_temp.setStyleSheet("background-color: black; border-radius: 20px;")
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.logo_label.setPixmap(QPixmap(f'../assets/{self.heart_on}'))
        self.ecg_layout = QVBoxLayout(conteneur_ecg)
        self.ecg_layout.setContentsMargins(0, 0, 0, 0)
        self.ecg_layout.addWidget(self.logo_label)
        self.ecg_label = QLabel("ECG")
        self.ecg_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.ecg_label.setStyleSheet("font-size: 55pt; font-weight: bold; color: #33FF57; padding-bottom: 25px;")
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
        press_unite = QLabel("NIBP")
        press_unite.setAlignment(Qt.AlignLeft)
        self.press_moy_value = QLabel("moyenne")
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
        self.pni_label = QLabel("Pression")
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
        self.sat_label = QLabel("Saturation", self)
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
        self.sat_label.setStyleSheet("color: #FF500A; font-weight: bold; font-size: 55pt;")
        self.sat_layout.addLayout(first_ligne)
        self.sat_layout.addLayout(sec_ligne)
        self.sat_layout.addWidget(QLabel(""))

        self.temp_layout = QVBoxLayout(conteneur_resp_temp)
        self.temp_layout.setContentsMargins(0, 0, 0, 0)
        self.resp_label = QLabel("Respiration", self)
        self.resp_label.setAlignment(Qt.AlignCenter)
        self.resp_label.setStyleSheet("color: #DFEE0A; font-size: 35pt;")
        self.temp_label = QLabel("Temperature", self)
        self.temp_label.setAlignment(Qt.AlignBottom)
        self.temp_label.setStyleSheet("color: #3020FF; font-size: 20pt; padding: 15px")
        resp_lay = QVBoxLayout()
        temp_lay = QHBoxLayout()
        unit_t = QLabel("TEMP")
        unit_t.setAlignment(Qt.AlignLeft)
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
        resp_lay.addLayout(unite_lay)
        resp_lay.addWidget(self.resp_label, alignment=Qt.AlignCenter)
        self.temp_layout.addLayout(resp_lay)
        self.temp_layout.addLayout(temp_lay)

        box_layout = QVBoxLayout()
        box_layout.addWidget(conteneur_ecg)
        box_layout.addWidget(conteneur_pression)
        box_layout.addWidget(conteneur_saturation)
        box_layout.addWidget(conteneur_resp_temp)

        self.layout1.addLayout(box_layout, stretch=2)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.showGrid(x=False, y=False)
        self.plot_widget.setYRange(-1.5, 1.5)
        plot_item = self.plot_widget.getPlotItem()
        plot_item.getAxis('left').setVisible(False)
        plot_item.getAxis('bottom').setVisible(False)

        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='#DFEE0A', width=2), name="RESP")
        self.curve1 = self.plot_widget.plot(pen=pg.mkPen(color='g', width=2), name="ECG")
        self.curve2 = self.plot_widget.plot(pen=pg.mkPen(color='#FF500A', width=2), name="SpO2")

        self.layout1.addWidget(self.plot_widget, stretch=4)

        self.layout_app.addLayout(self.layout1, stretch=6)

        self.centralWidget.setLayout(self.layout_app)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.update_interval)

        self.timer_txt = QTimer()
        self.timer_txt.timeout.connect(self.update_txt)
        self.timer_txt.start(1000)

        self.timer_heart = QTimer()
        self.timer_heart.timeout.connect(self.update_logo)
        self.timer_heart.start(250)

        self.timer_infos = QTimer()
        self.timer_infos.timeout.connect(self.get_infos_patient)
        self.timer_infos.setSingleShot(True)
        self.timer_infos.start(500)

        self.setStyleSheet("background-color: #1A1A1A; font-family: roboto;")

    def get_infos_patient(self):
        self.app_infos_patient.show()
        if self.app_infos_patient.exec_() == QDialog.Accepted:
            datas = self.app_infos_patient.get_data()
            with open("../datas/patient_infos.txt", 'w+') as patient_file:
                #patient_file.write("")
                patient_file.write(datas['nom']);patient_file.write(" ");patient_file.write(datas['id']);patient_file.write(" ");patient_file.write(str(datas['age']));patient_file.write(" ");patient_file.write(datas['sexe']);patient_file.write(" ");patient_file.write(str(datas['poids']));patient_file.write(" ");patient_file.write(str(datas['taille']));patient_file.write(" ");salle = datas['salle'].split(' ');
                try:
                    patient_file.write(str(salle[0])+str(salle[1]));
                except IndexError:
                    print("Erreur de données concernant la salle du patient")
                finally:
                    patient_file.write("\n")

            with open("../datas/patient_infos.txt", 'r+') as patient_file:
                line = patient_file.readline()
                datas = line.split(' ')
                age = int(datas[2])
                self.name_patient.setText(datas[0]+" (Adult)") if age>=18 else self.name_patient.setText(datas[0]+ " (Mineur)")

    def update_time(self):
        self.hours.setText(datetime.now().strftime("%H:%M"))
        self.date.setText(datetime.now().strftime("%d/%m/%Y"))

    def update_txt(self):
        self.ecg_label.setText(str(f"{50*abs(self.data_y[len(self.data_y)-1]):.2f}"))
        self.sat_label.setText(str(f"{abs(self.data_y[len(self.data_y)-1]):.2f}"))
        self.pni_label.setText(str(f"{120*self.data_y[len(self.data_y)-1]:.2f}")+"\n"+str(f"{80*self.data_y[len(self.data_y)-1]/2:.2f}"))
        self.temp_label.setText(str(f"{self.data_y[len(self.data_y)-1]:.2f}")+" °C")
        self.resp_label.setText(str(f"{self.data_y[len(self.data_y)-1]:.2f}"))
        self.press_moy_value.setText(str(f"{abs(90*self.data_y[len(self.data_y)-1]):.2f}"))
        self.storage()

    def update_logo(self):
        if self.state_heart:
            self.logo_label.setPixmap(QPixmap(f'../assets/{self.heart_off}'))
            self.state_heart = False
        else:
            self.logo_label.setPixmap(QPixmap(f'../assets/{self.heart_on}'))
            self.state_heart = True

    def update(self):
        data_esp = Ecg()
        if(data_esp._get_data_()[0]==0):
            new_val = np.sin(self.ptr*0.2)*0.1+np.random.normal(size=1, scale=1, loc=0.5)*0.15
            self.data_y[:-1]=self.data_y[1:]
            try:        #possible erreur
                self.data_y[-1]=new_val
            except DeprecationWarning as e:
                pass
            finally:
                x_data = np.arange(self.ptr-self.max_points,self.ptr)
                self.curve.setData(x_data, self.data_y-1)
                self.curve1.setData(x_data, self.data_y+1)
                self.curve2.setData(x_data, self.data_y)
                self.plot_widget.setXRange(self.ptr-self.max_points,self.ptr)
                self.ptr+=1
                #self.verify_value_out_of_range()
        else:
            return

    def storage(self):
        num_car = 5
        file_name = "../datas/base_donnees.txt"
        debut = datetime.now().strftime("the %d/%m/%Y at %H:%M:%S")
        with open(file_name, "w+") as f:
            for i in range(num_car):
                f.write('-')
            f.write("Beginning of transmission at "+debut)
            for i in range(num_car):
                f.write('-')
            f.write(" HR: "+str(self.data_y[len(self.data_y)-1])+" bpm ")
            f.write("SATURATION: "+str(self.data_y[len(self.data_y)-1])+"% ")
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
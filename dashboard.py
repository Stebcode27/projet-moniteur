import sys
import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QAction, QLabel, QToolBar, QVBoxLayout, QHBoxLayout, QGroupBox, QDialog, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from datetime import datetime
from templates_params import Ecg

class Dashboard(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moniteur")
        self.setGeometry(10, 10, 800, 400)

        self.barre_etat = self.statusBar()
        self.hours = QLabel(datetime.now().strftime("%Hh %M"), self)
        self.hours.setAlignment(Qt.AlignLeft)
        self.date = QLabel(datetime.now().strftime("%d/%m/%Y"), self)
        self.date.setAlignment(Qt.AlignRight)
        self.barre_etat.addWidget(self.hours,stretch=1)
        self.barre_etat.setStyleSheet("color: white; font-size: 20px; padding: 10px; background: #0A0A0A;")
        self.name_patient = QLabel("Patient Name (Adult)", self)
        self.name_patient.setAlignment(Qt.AlignCenter)

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

        action = QAction(QIcon('assets/save.png'), '&Enregistrer', self)
        action.setStatusTip('Enregistrer')
        action.triggered.connect(self.storage)

        self.tool_bar = QToolBar("Barre d'outils")
        self.addToolBar(self.tool_bar)
        self.tool_bar.addAction(action)

        self.layout_app = QVBoxLayout()

        self.layout1 = QHBoxLayout()

        conteneur_ecg = QWidget()
        conteneur_ecg.setStyleSheet("background-color: black; border-radius: 20px;")
        conteneur_pression = QWidget()
        conteneur_pression.setStyleSheet("background-color: black; border-radius: 20px;")

        pixmap = QPixmap('assets/heart.png')
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        logo_label.setPixmap(pixmap)

        self.ecg_layout = QVBoxLayout(conteneur_ecg)
        self.ecg_layout.setContentsMargins(0, 0, 0, 0)
        self.ecg_layout.addWidget(logo_label)
        self.ecg_label = QLabel("ECG")
        self.ecg_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.ecg_label.setStyleSheet("background-color: black; font-size: 35pt; font-weight: bold; color: #33FF57; padding-bottom: 75px; border-radius: 20px;")
        self.ecg_layout.addWidget(self.ecg_label)
        hr = QLabel("HR")
        hr.setAlignment(Qt.AlignRight)
        hr.setStyleSheet("color: #33FF57; font-size: 15pt;")
        self.ecg_layout.addWidget(hr)

        self.pression_layout = QVBoxLayout(conteneur_pression)
        self.pression_layout.setContentsMargins(0, 0, 0, 0)
        press_dias_sys = QLabel("SYS/DIAS mmHg")
        press_dias_sys.setAlignment(Qt.AlignLeft)
        moy_lab = QLabel("(Moy)")
        moy_lab.setAlignment(Qt.AlignRight)
        moy_lab.setStyleSheet("color: white; font-size: 12pt; padding: 5px;")
        press_dias_sys.setStyleSheet("color: white; font-size: 12pt; padding: 5px;")
        p_l_hbox = QHBoxLayout()
        p_l_hbox.addWidget(press_dias_sys, stretch=2)
        p_l_hbox.addStretch()
        p_l_hbox.addWidget(moy_lab, stretch=1)
        self.pni_label = QLabel("Pression")
        self.pni_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.pni_label.setStyleSheet("background-color: black; font-size: 35pt; font-weight: bold; color: #FF5733; padding-bottom: 100px; border-radius: 20px;")
        self.pression_layout.addLayout(p_l_hbox)
        self.pression_layout.addWidget(self.pni_label)

        self.sat_label = QLabel("Saturation", self)
        self.temp_label = QLabel("Temperature", self)

        box_layout = QVBoxLayout()
        box_layout.addWidget(conteneur_ecg)
        box_layout.addWidget(conteneur_pression)
        self.group_labels = [self.sat_label, self.temp_label]
        for label in self.group_labels:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(f"background-color: black; font-size: 35pt; font-weight: bold; color: {self.colors[self.group_labels.index(label) % len(self.colors)]}; padding: 10px; border-radius: 20px;")
            box_layout.addWidget(label)

        self.layout1.addLayout(box_layout, stretch=2)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.showGrid(x=False, y=False)
        self.plot_widget.setYRange(-1.5,1.5)
        plot_item = self.plot_widget.getPlotItem()
        plot_item.getAxis('left').setVisible(False)
        plot_item.getAxis('bottom').setVisible(False)

        self.curve=self.plot_widget.plot(pen=pg.mkPen(color='b', width=2))
        self.curve1=self.plot_widget.plot(pen=pg.mkPen(color='g', width=2))
        self.curve2=self.plot_widget.plot(pen=pg.mkPen(color='y', width=2))

        self.layout1.addWidget(self.plot_widget, stretch=4)

        self.layout_app.addLayout(self.layout1, stretch=6)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.update_interval)

        centralWidget.setLayout(self.layout_app)

        self.timer_txt = QTimer()
        self.timer_txt.timeout.connect(self.update_txt)
        self.timer_txt.start(1000)

        self.setStyleSheet("background-color: #1A1A1A;")

    def update_time(self):
        self.hours.setText(datetime.now().strftime("%Hh %M"))
        self.date.setText(datetime.now().strftime("%d/%m/%Y"))

    def update_txt(self):
        self.ecg_label.setText(str(f"{50*abs(self.data_y[len(self.data_y)-1]):.2f}")+"bpm")
        self.sat_label.setText(str(f"{abs(self.data_y[len(self.data_y)-1]):.2f}")+"%")
        self.pni_label.setText(str(f"{self.data_y[len(self.data_y)-1]:.2f}")+"/"+str(f"{self.data_y[len(self.data_y)-1]/2:.2f}"))
        self.temp_label.setText(str(f"{self.data_y[len(self.data_y)-1]:.2f}")+" °C")

    def update(self):
        data_esp = Ecg()
        if(data_esp._get_data_()[0]==0):
            new_val = np.sin(self.ptr*0.2)*0.3+np.random.normal(size=1, scale=1, loc=0.5)*0.15
            self.data_y[:-1]=self.data_y[1:]
            try:        #possible erreur
                self.data_y[-1]=new_val
            except DeprecationWarning as e:
                pass
            finally:
                x_data = np.arange(self.ptr-self.max_points,self.ptr)
                self.curve.setData(x_data, self.data_y-1)
                self.curve1.setData(x_data, self.data_y)
                self.curve2.setData(x_data, self.data_y+1)
                self.plot_widget.setXRange(self.ptr-self.max_points,self.ptr)
                self.ptr+=1
        else:
            return

    def storage(self):
        num_car = 5
        file_name = "base_donnees.txt"
        debut = datetime.now().strftime("the %d/%m/%Y at %H:%M:%S")
        with open(file_name, "a+") as f:
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Dashboard()
    window.showFullScreen()
    sys.exit(app.exec_())
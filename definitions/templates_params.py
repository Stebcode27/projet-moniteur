"""Definition des templates paramètres du moniteur multiparamétrique"""
import sys
import os
import time

from PyQt5.QtWidgets import QApplication

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

import numpy as np
"""import pandas as pd

try:
    pd.set_option('mode.copy_on_write', False)
except:
    pass
"""
import wfdb
from definitions.PanTompkins import PanTompkinsDetector
from PyQt5.QtCore import QThread, pyqtSignal
import serial
import struct

MAXPOINT = 2500

class Interface(QThread):

    onChanged = pyqtSignal(dict)
    onError = pyqtSignal(str)
    onPressionProcessed = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        self.data = None
        self.running = True
        self.isData = False

    def run(self):
        try:
            ser = serial.Serial("COM8", 115200, timeout=1)
            packet_format = "<BffffffffffIBB"
            packet_size = struct.calcsize(packet_format)

            while self.running:
                if ser.in_waiting > packet_size:
                    self.isData = True
                    raw_data = ser.read(packet_size)

                    header, ecg, buffer_ecg, sat, buffer_sat, resp, buffer_resp, temp, pni_moy, diastol, systol, ts, code, footer = struct.unpack(packet_format, raw_data)
                    if header == 0xAA and footer == 0x55:
                        self.data = {
                            "ecg": ecg,
                            "buffer_ecg": buffer_ecg,
                            "sat": sat,
                            "buffer_sat": buffer_sat,
                            "resp": resp,
                            "buffer_resp": buffer_resp,
                            "temp": temp,
                            "pni_moy": pni_moy,
                            "diastol": diastol,
                            "systol": systol,
                            "code": code,
                            "ts": ts,
                        }
                        self.onChanged.emit(self.data)
                        if code==0xFF:
                            self.onPressionProcessed.emit(bytes(code))
                    else:
                        ser.read(1)
                    #time.sleep(1)
                else:
                    self.isData = False
        except Exception as e:
            self.onError.emit(str(e))

    def set_running(self, running):
        self.running = running

#Template pour tous les paramètres du moniteur
class Param():

    def __init__(self, param_name):
        self.maxpoint = MAXPOINT   #pour eviter les messages d'erreur en cas de manque de données
        self._data_ = np.zeros(self.maxpoint, dtype='int16')
        self.param_name = param_name

    #Les getters de chaque attribut
    def _get_data_(self):
        return self._data_
    def get_param_name(self):
        return self.param_name
    def get_maxpoint(self):
        return self.maxpoint
    
    #Les setters de chaque attribut
    def _set_maxpoint_(self, maxpoint):
        self.maxpoint = maxpoint
    def _set_data_(self, data):
        self._data_ = data

class Ecg(Param):
    
    def __init__(self, parent=None):
        super(Ecg, self).__init__("ecg")
        self.parent = parent
        self.fs = 360
        self._set_data_(np.zeros(self.maxpoint))
        self.buffer = np.zeros(self.maxpoint)
        self.ptr=0
        self.update_interval = 1
        self.x_data = np.arange(self.ptr,self.maxpoint)
        self.pt = PanTompkinsDetector()
        self.bpm = 70

        self.detection = (0,False)
    
    def update_data(self):
        if self.parent.simul_state:
            self.buffer[self.ptr] = self._get_data_()[self.ptr] * 0.25
            gap_size = 30  # Nombre de points à effacer devant
            for i in range(1, gap_size + 1):
                idx_to_clear = (self.ptr + i) % self.maxpoint
                self.buffer[idx_to_clear] = np.nan  # Efface la vieille donnée
            self.ptr = (self.ptr + 1) % self.maxpoint
        else:
            if not self.parent.interface_serie.isData:
                print('yes')
                self.buffer[self.ptr] = 0
                gap_size = 30  # Nombre de points à effacer devant
                for i in range(1, gap_size + 1):
                    idx_to_clear = (self.ptr + i) % self.maxpoint
                    self.buffer[idx_to_clear] = np.nan  # Efface la vieille donnée
                self.ptr = (self.ptr + 1) % self.maxpoint

    def get_mit_data(self):
        try:
            record = wfdb.rdrecord(f"{os.path.join(PROJECT_ROOT, 'datas', '234')}", sampto=2500)
            signal = record.p_signal[:, 0]
            self.fs = record.fs
            self._set_data_(signal)
        except Exception as e:
            print(f"Impossible d'ouvrir le fichier spécifié. Erreur: {e}")
            return
        filt_list = []
        bpm=0.
        for sample in self._data_:
            p, der, filtred = self.pt.process(sample)
            self.detection = self.pt.detect_peak(p, der)
            if self.detection[1]:
                self.bpm = int(self.detection[0])
            filt_list.append(filtred)
        self._set_data_(filt_list)
    def setbpm(self, bpm):
        self.bpm = bpm

    def reset_buffer(self):
        self.buffer = np.zeros(self.maxpoint)

class Saturation(Param):
    def __init__(self, parent=None):
        super(Saturation, self).__init__("sat")
        self.parent = parent
        self.fs = 360
        self.display_buffer = np.zeros(self.maxpoint)
        self.ptr = 0
        self.data_index = 0
        self.x_data = np.arange(self.maxpoint)

        # Paramètres physiologiques
        self.bpm = 70  # On peut imaginer synchroniser cela avec l'ECG plus tard
        self.spo2_val = 95  # Valeur numérique (%)

    def _generate_pleth_wave(self, i):
        """ Génère une onde de pouls réaliste (montée rapide, descente dicrote) """
        samples_per_beat = (self.fs * 60) / self.bpm
        phase = (i % samples_per_beat) / samples_per_beat

        # Onde systolique (montée brusque) + Onde dicrote (petit rebond lors de la relaxation)
        # Formule mathématique simplifiée pour le tracé
        v = (np.exp(-0.5 * ((phase - 0.2) / 0.05) ** 2) * 0.8 +
             np.exp(-0.5 * ((phase - 0.45) / 0.12) ** 2) * 0.3)

        return v * 0.5  # Amplitude réglable pour ton graphique

    def update_data(self):
        if self.parent.simul_state:
            # 1. Générer la nouvelle valeur
            val = self._generate_pleth_wave(self.data_index)

            # 2. Écrire dans le buffer au niveau du pointeur
            self.display_buffer[self.ptr] = val

            # 3. LE GAPPING (Effacer devant pour le défilement rouge)
            gap_size = 30
            for i in range(1, gap_size + 1):
                idx_to_clear = (self.ptr + i) % self.maxpoint
                self.display_buffer[idx_to_clear] = np.nan

            # 4. Incrémenter les index
            self.ptr = (self.ptr + 1) % self.maxpoint
            self.data_index += 1

    def get_display_data(self):
        return self.display_buffer

    def reset_buffer(self):
        self.display_buffer = np.zeros(self.maxpoint)

class Respiration(Param):
    def __init__(self, parent=None):
        super(Respiration, self).__init__("resp")
        self.parent = parent
        self.fs = 360  # On garde la même fréquence pour la synchro
        self.display_buffer = np.zeros(self.maxpoint)
        self.ptr = 0
        self.data_index = 0
        self.x_data = np.arange(self.maxpoint)

        # Paramètres respiratoires
        self.rpm = 50  # Respirations Par Minute (très lent)
        self.resp_rate = 45  # Valeur numérique (%)

    def _generate_resp_wave(self, i):
        """ Génère une onde respiratoire fluide (plus lente que le pouls) """
        # Calcul du cycle (15 cycles par minute = 1 cycle toutes les 4 secondes)
        samples_per_cycle = (self.fs * 60) / self.rpm
        phase = (i % samples_per_cycle) / samples_per_cycle
        v = np.sin(15 * (2 * np.pi * phase - (np.pi / 2)))
        drift = 0.1 * np.sin(2 * np.pi * 0.05 * phase)

        return (v + drift) * 0.1  # On scale pour l'affichage

    def update_data(self):
        if self.parent.simul_state:
            val = self._generate_resp_wave(self.data_index)
            self.display_buffer[self.ptr] = val
            gap_size = 30
            for i in range(1, gap_size + 1):
                idx_to_clear = (self.ptr + i) % self.maxpoint
                self.display_buffer[idx_to_clear] = np.nan
            self.ptr = (self.ptr + 1) % self.maxpoint
            self.data_index += 1

    def get_display_data(self):
        return self.display_buffer
    def reset_buffer(self):
        self.display_buffer = np.zeros(self.maxpoint)

class Pression(Param):

    def __init__(self, parent=None):
        super(Pression, self).__init__("pni")
        self.parent = parent
        self.pam = 90
        self.systo = 120
        self.diasto = 85

    def update_values(self, systo, diasto, pam):
        self.systo = systo
        self.diasto = diasto
        self.pam = pam

class Temperature(Param):

    def __init__(self, parent=None):
        super(Temperature, self).__init__("temp")
        self.parent = parent
        self.temperature = 37.2

    def update_value(self, temperature):
        self.temperature = temperature
        
if __name__ == '__main__':
    """ecg = Ecg()
    import matplotlib.pyplot as plt
    ecg.get_mit_data()
    t = np.arange(len(ecg._get_data_())) / ecg.fs
    plt.figure(figsize=(12,8))
    #print(ecg.get_bpm())
    plt.plot(t, ecg._get_data_(), color='blue', label='MIT')
    plt.show()"""
    app = QApplication(sys.argv)
    interface = Interface()
    interface.start()
    sys.exit(app.exec_())
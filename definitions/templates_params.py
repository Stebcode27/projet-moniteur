"""Definition des templates paramètres du moniteur multiparamétrique"""
import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd

try:
    pd.set_option('mode.copy_on_write', False)
except:
    pass

import wfdb
from definitions.PanTompkins import PanTompkinsDetector
from threading import Thread

MAXPOINT = 500

#Template pour tous les paramètres du moniteur
class Param(Thread):

    def __init__(self, param_name):
        Thread.__init__(self)
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
    
    def __init__(self):
        super(Ecg, self).__init__("ecg")
        self.fs = 360
        self._set_data_(np.zeros(self.maxpoint))
        self.buffer = np.zeros(self.maxpoint)
        self.ptr=0
        self.update_interval = 25
        self.x_data = np.arange(self.ptr,self.maxpoint)
        self.pt = PanTompkinsDetector()
        self.bpm = 80
    
    def update_data(self):
        self.buffer[self.ptr] = self._get_data_()[self.ptr] * 0.5
        # --- LE GAP SE MET ICI ---
        gap_size = 5  # Nombre de points à effacer devant
        for i in range(1, gap_size + 1):
            idx_to_clear = (self.ptr + i) % self.maxpoint
            self.buffer[idx_to_clear] = np.nan  # Efface la vieille donnée
        # -------------------------
        self.ptr = (self.ptr + 1) % self.maxpoint
        #self.x_data = np.arange(self.ptr-self.maxpoint,self.ptr)

    def get_mit_data(self):
        try:
            record = wfdb.rdrecord(f"{os.path.join(PROJECT_ROOT, 'datas', '101')}", sampto=500)
            signal = record.p_signal[:, 0]
            self.fs = record.fs
            self._set_data_(signal)
        except Exception as e:
            print(f"Impossible d'ouvrir le fichier spécifié. Erreur: {e}")
            return
        filt_list = []
        for sample in self._data_:
            p, der, filtred = self.pt.process(sample)
            bpm, d = self.pt.detect_peak(p, der)
            filt_list.append(filtred)
        self._set_data_(filt_list)

class Saturation(Param):
    def __init__(self):
        super(Saturation, self).__init__("sat")
        self.fs = 360
        self.maxpoint = 500
        self.display_buffer = np.zeros(self.maxpoint)
        self.ptr = 0
        self.data_index = 0
        self.x_data = np.arange(self.maxpoint)

        # Paramètres physiologiques
        self.bpm = 70  # On peut imaginer synchroniser cela avec l'ECG plus tard
        self.spo2_val = 98  # Valeur numérique (%)

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
        # 1. Générer la nouvelle valeur
        val = self._generate_pleth_wave(self.data_index)

        # 2. Écrire dans le buffer au niveau du pointeur
        self.display_buffer[self.ptr] = val

        # 3. LE GAPPING (Effacer devant pour le défilement rouge)
        gap_size = 5
        for i in range(1, gap_size + 1):
            idx_to_clear = (self.ptr + i) % self.maxpoint
            self.display_buffer[idx_to_clear] = np.nan

        # 4. Incrémenter les index
        self.ptr = (self.ptr + 1) % self.maxpoint
        self.data_index += 1

    def get_display_data(self):
        return self.display_buffer

class Respiration(Param):
    def __init__(self):
        super(Respiration, self).__init__("resp")
        self.fs = 360  # On garde la même fréquence pour la synchro
        self.maxpoint = 500
        self.display_buffer = np.zeros(self.maxpoint)
        self.ptr = 0
        self.data_index = 0
        self.x_data = np.arange(self.maxpoint)

        # Paramètres respiratoires
        self.rpm = 15  # Respirations Par Minute (très lent)
        self.resp_rate = 98  # Valeur numérique (%)

    def _generate_resp_wave(self, i):
        """ Génère une onde respiratoire fluide (plus lente que le pouls) """
        # Calcul du cycle (15 cycles par minute = 1 cycle toutes les 4 secondes)
        samples_per_cycle = (self.fs * 60) / self.rpm
        phase = (i % samples_per_cycle) / samples_per_cycle

        # La respiration est plus proche d'une onde sinusoïdale pure,
        # mais l'expiration est souvent un peu plus longue que l'inspiration.
        # On utilise une fonction sinus légèrement déformée
        v = np.sin(15 * (2 * np.pi * phase - (np.pi / 2)))

        # Ajout d'un peu de "bruit de fond" basse fréquence pour le réalisme
        drift = 0.1 * np.sin(2 * np.pi * 0.05 * phase)

        return (v + drift) * 0.1  # On scale pour l'affichage

    def update_data(self):
        # 1. Générer la valeur
        val = self._generate_resp_wave(self.data_index)

        # 2. Écrire dans le buffer
        self.display_buffer[self.ptr] = val

        # 3. LE GAPPING (Effacer devant)
        # On peut mettre un gap un peu plus large car l'onde est lente
        gap_size = 5
        for i in range(1, gap_size + 1):
            idx_to_clear = (self.ptr + i) % self.maxpoint
            self.display_buffer[idx_to_clear] = np.nan

        # 4. Incrémenter
        self.ptr = (self.ptr + 1) % self.maxpoint
        self.data_index += 1

    def get_display_data(self):
        return self.display_buffer

class Pression(Param):

    def __init__(self):
        super(Pression, self).__init__("pni")
        self.pam = 90
        self.systo = 120
        self.diasto = 85

    def update_values(self, systo, diasto, pam):
        self.systo = systo
        self.diasto = diasto
        self.pam = pam

class Temperature(Param):

    def __init__(self):
        super(Temperature, self).__init__("temp")
        self.temperature = 37.1

    def update_value(self, temperature):
        self.temperature = temperature
        
if __name__ == '__main__':
    ecg = Ecg()
    import matplotlib.pyplot as plt
    ecg.get_mit_data()
    t = np.arange(len(ecg._get_data_())) / ecg.fs
    plt.figure(figsize=(12,8))
    #print(ecg.get_bpm())
    plt.plot(t, ecg._get_data_(), color='blue', label='MIT')
    plt.show()
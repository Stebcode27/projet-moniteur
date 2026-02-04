import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

class Pantompkins:

    def __init__(self):

        self.ind = 0
        #coefficients du filtre passe bas
        self.x_lpf = [0] * 13
        self.y_lpf = [0] * 2
        self.x_lpf_ptr = 0

        #coefficients du filtre passe haut
        self.x_hpf = [0] * 33
        self.y_hpf = 0
        self.x_hpf_ptr = 0

        #coefficients du filtre derivatif
        self.x_der = [0] * 5
        self.x_der_ptr = 0

        #coefficients de l'integration à moyenne glissante
        self.N_mwi = 54     #54 échantillons pour une fréquence de 360Hz
        self.buffer_mwi = [0] * self.N_mwi
        self.mwi_ptr = 0
        self.sum_mwi = 0

        #paramètres utilisés pour la détection des pics
        self.spk = 0.0
        self.npk = 0.0
        self.threshold = self.npk + 0.25 * ( self.spk - self.npk )
        self.count = 0
        self.last_peak = 0
        self.fs = 360#Hz
        self.mwi_max_detected = 0
        self.rr_intervals = []
        self.avg_rr = 0
        self.limit_search_back = 512
        self.count_pics = 0

    def _passe_bas(self, signal):
        self.x_lpf[self.x_lpf_ptr] = signal

        fir_term = (self.x_lpf[self.x_lpf_ptr] - 2 * self.x_lpf[(self.x_lpf_ptr - 6) % 13] + self.x_lpf[(self.x_lpf_ptr - 12) % 13]) / 32.0

        # Équation récursive
        sortie = 2 * self.y_lpf[1] - self.y_lpf[0] + fir_term

        self.y_lpf[0] = self.y_lpf[1]
        self.y_lpf[1] = sortie
        self.x_lpf_ptr = (self.x_lpf_ptr + 1) % 13
        return sortie

    def _passe_haut(self, signal):
        self.x_hpf[self.x_hpf_ptr] = signal

        # y[n] = y[n-1] - x[n]/32 + x[n-16] - x[n-17] + x[n-32]/32
        sortie = (self.y_hpf - (self.x_hpf[self.x_hpf_ptr] / 32.0) +
                  self.x_hpf[(self.x_hpf_ptr - 16) % 33] - self.x_hpf[(self.x_hpf_ptr - 17) % 33] +
                  (self.x_hpf[(self.x_hpf_ptr - 32) % 33] / 32.0))

        self.y_hpf = sortie
        self.x_hpf_ptr = (self.x_hpf_ptr + 1) % 33
        return sortie

    def _derivatif(self, signal):
        self.x_der[self.x_der_ptr] = signal

        #y(n) = \frac{1}{8}[2x(n) + x(n - 1) - x(n - 3) - 2x(n - 4)]
        sortie =  (1 / 8) * (2 * self.x_der[self.x_der_ptr] + self.x_der[(self.x_der_ptr - 1) % 5] - self.x_der[(self.x_der_ptr - 3) % 5] - 2 * self.x_der[(self.x_der_ptr - 4) % 5])

        self.x_der_ptr = (self.x_der_ptr + 1) % 5
        return sortie

    def _mise_au_carre(self, signal):
        return signal*signal

    def _mwi(self, signal):
        val_out = self.buffer_mwi[self.mwi_ptr]

        self.sum_mwi = self.sum_mwi + signal - val_out

        self.buffer_mwi[self.mwi_ptr] = signal

        sortie = self.sum_mwi / self.N_mwi
        self.mwi_ptr = (self.mwi_ptr + 1) % self.N_mwi
        return sortie

    def process(self, input_sample):
        low_passed = self._passe_bas(input_sample)
        high_passed = self._passe_haut(low_passed)
        derivative = self._derivatif(high_passed)
        squared = self._mise_au_carre(derivative)
        integrated = self._mwi(squared)
        return integrated, high_passed

    def detect_pic(self, signal):
        self.count += 1
        bpm = 0

        if self.count < 560:
            if signal > self.mwi_max_detected:
                self.mwi_max_detected = signal
            return bpm

        self.spk = self.mwi_max_detected
        self.npk = self.spk / 2

        if (self.count - self.last_peak) > self.limit_search_back and self.limit_search_back > 0:
            self.threshold = self.threshold * 0.5

        if signal > self.threshold and (self.count - self.last_peak) > 72:  #periode refractaire de 200ms
            rr_ = self.count - self.last_peak
            self.rr_intervals.append(rr_)
            if len(self.rr_intervals) > 8:
                self.rr_intervals.pop(0)
            self.avg_rr = sum(self.rr_intervals) / len(self.rr_intervals)
            self.limit_search_back = 1.66 * self.avg_rr

            bpm = 360 * 60 / rr_

            self.last_peak = self.count
            self.spk = 0.125 * signal + 0.875 * self.spk

            print(f"Pic Détecté ! BPM : {bpm:.1f} bpm/min")
            self.count_pics += 1
        else:
            self.npk = 0.125 * signal + 0.875 * self.npk

        self.threshold = self.npk + 0.25 * (self.spk - self.npk)
        return bpm

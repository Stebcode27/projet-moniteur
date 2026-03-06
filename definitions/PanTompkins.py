class Threshold:
    def __init__(self):
        self.i1, self.i2 = 0, 0
        self.spk, self.npk = 0, 0

    def set(self, i):
        self.i1 = i
        self.i2 = self.i1 * 0.5

    def update(self):
        # Formule originale : Thresh = NPK + 0.25*(SPK - NPK)
        self.i1 = self.npk + 0.25 * (self.spk - self.npk)
        self.i2 = 0.5 * self.i1

    def updateNoise(self, noise):
        self.npk = 0.125 * noise + 0.875 * self.npk
        self.update()

    def updateSignal(self, signal):
        self.spk = 0.125 * signal + 0.875 * self.spk
        self.update()


class PanTompkinsDetector:
    def __init__(self):
        # Filtres (inchangés car corrects)
        self.x_lpf, self.y_lpf, self.x_lpf_ptr = [0] * 13, [0] * 2, 0
        self.x_hpf, self.y_hpf, self.x_hpf_ptr = [0] * 33, 0, 0
        self.x_der, self.x_der_ptr = [0] * 5, 0
        self.N_mwi = 54
        self.buffer_mwi, self.mwi_ptr, self.sum_mwi = [0] * 54, 0, 0

        # Variables de détection
        self.current_sample_count = 0
        self.last_peak_sample = 0
        self.last_integ_val = 0
        self.is_rising = False  # Pour détecter le vrai sommet

        self.rr_intervals = [288] * 8  # Init à 80 BPM (360Hz * 60 / 80)
        self.avg_rr = 288
        self.count = 0
        self.threshold = Threshold()
        self.mwi_max_init = 0

    # ... (Garder tes méthodes _passe_bas, _passe_haut, _derivatif, _mise_au_carre, _mwi identiques)
    def _passe_bas(self, signal):
        self.x_lpf[self.x_lpf_ptr] = signal
        fir_term = (self.x_lpf[self.x_lpf_ptr] - 2 * self.x_lpf[(self.x_lpf_ptr - 6) % 13] + self.x_lpf[
            (self.x_lpf_ptr - 12) % 13]) / 32.0
        sortie = 2 * self.y_lpf[1] - self.y_lpf[0] + fir_term
        self.y_lpf[0], self.y_lpf[1] = self.y_lpf[1], sortie
        self.x_lpf_ptr = (self.x_lpf_ptr + 1) % 13
        return sortie

    def _passe_haut(self, signal):
        self.x_hpf[self.x_hpf_ptr] = signal
        sortie = (self.y_hpf - (self.x_hpf[self.x_hpf_ptr] / 32.0) +
                  self.x_hpf[(self.x_hpf_ptr - 16) % 33] - self.x_hpf[(self.x_hpf_ptr - 17) % 33] +
                  (self.x_hpf[(self.x_hpf_ptr - 32) % 33] / 32.0))
        self.y_hpf = sortie
        self.x_hpf_ptr = (self.x_hpf_ptr + 1) % 33
        return sortie

    def _derivatif(self, signal):
        self.x_der[self.x_der_ptr] = signal
        sortie = (1 / 8) * (2 * self.x_der[self.x_der_ptr] + self.x_der[(self.x_der_ptr - 1) % 5] - self.x_der[
            (self.x_der_ptr - 3) % 5] - 2 * self.x_der[(self.x_der_ptr - 4) % 5])
        self.x_der_ptr = (self.x_der_ptr + 1) % 5
        return sortie

    def _mise_au_carre(self, signal):
        return signal ** 2

    def _mwi(self, signal):
        val_out = self.buffer_mwi[self.mwi_ptr]
        self.sum_mwi = self.sum_mwi + signal - val_out
        self.buffer_mwi[self.mwi_ptr] = signal
        sortie = self.sum_mwi / self.N_mwi
        self.mwi_ptr = (self.mwi_ptr + 1) % self.N_mwi
        return sortie

    def process(self, input_sample):
        lp = self._passe_bas(input_sample)
        hp = self._passe_haut(lp)
        der = self._derivatif(hp)
        sq = self._mise_au_carre(der)
        intgr = self._mwi(sq)
        return intgr, der, hp

    def updateRR(self, rr):
        self.rr_intervals.append(rr)
        if len(self.rr_intervals) > 8: self.rr_intervals.pop(0)
        self.avg_rr = sum(self.rr_intervals) / len(self.rr_intervals)

    def detect_peak(self, integrated_val, derivative_val):
        detected = False
        bpm = 0
        self.current_sample_count += 1

        # 1. Phase d'apprentissage (1ère seconde)
        if self.current_sample_count < 360:
            if integrated_val > self.mwi_max_init:
                self.mwi_max_init = integrated_val
            if self.current_sample_count == 359:
                self.threshold.spk = self.mwi_max_init
                self.threshold.npk = self.mwi_max_init * 0.125
                self.threshold.update()
            return (0, False)

        # 2. Logique de détection de maximum local (évite le bruit du 108)
        # On cherche l'instant où le signal commence à redescendre
        if integrated_val > self.last_integ_val:
            self.is_rising = True
        elif integrated_val < self.last_integ_val and self.is_rising:
            # On est au sommet d'un pic !
            self.is_rising = False
            possible_pk = self.last_integ_val

            # Période réfractaire stricte de 200ms (72 éch.)
            time_since_last = self.current_sample_count - self.last_peak_sample

            if time_since_last > 72:
                if possible_pk > self.threshold.i1:
                    # QRS Validé
                    self.count += 1
                    self.updateRR(time_since_last)
                    self.threshold.updateSignal(possible_pk)
                    self.last_peak_sample = self.current_sample_count
                    detected = True
                    bpm = (60 * 360) / self.avg_rr
                    print(f"Battement {self.count} | BPM: {bpm:.1f} | RR: {time_since_last}")
                else:
                    # C'est du bruit
                    self.threshold.updateNoise(possible_pk)

        # 3. Search-back (si rien trouvé depuis 166% du RR moyen)
        if (self.current_sample_count - self.last_peak_sample) > int(1.66 * self.avg_rr):
            # Ici on devrait normalement chercher dans le buffer le pic > i2
            # Pour simplifier et éviter le bug, on abaisse juste un peu le seuil
            self.threshold.i1 *= 0.75
            self.threshold.update()

        self.last_integ_val = integrated_val
        return (bpm, detected)
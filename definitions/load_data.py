import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from definitions.filtres import Pantompkins
import wfdb

def test_mit_wfdb():
    # 1. Téléchargement/Lecture du record 100
    # sampto=3600 correspond à 10 secondes (360 Hz * 10)
    file = os.path.join(PROJECT_ROOT, 'datas', '101')
    points = 500
    try:
        record = wfdb.rdrecord(file, sampto=points)
        signal = record.p_signal[:, 0]  # Canal MLII
        fs = record.fs # Devrait être 360
    except Exception as e:
        print(f"Erreur de chargement : {e}")
        return

    # 2. Initialisation
    pt = Pantompkins()
    filtered = []
    bpm_list = []
    pics = 1860
    # 3. Traitement
    for sample in signal:
        # Note : On multiplie par un gain (ex: 1000) si tes seuils
        # sont calibrés pour des entiers (0-4095) et non des mV.
        # Pour tester tes filtres seuls, pas besoin de gain.
        out, filt = pt.process(sample)
        bpm_list.append(pt.detect_pic(out))
        filtered.append(filt)

    return filtered, points
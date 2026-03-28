import sys
import os

# Ajouter le dossier racine du projet au path
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, PROJECT_ROOT)

def calculate_time_format(temp_seconds):
    hours, minutes, seconds = 0, 0, 0
    if temp_seconds < 60:
        seconds = temp_seconds
        return (hours, minutes, seconds)
    else:
        minutes = temp_seconds // 60
        seconds = temp_seconds % 60
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
        return (hours, minutes, seconds)
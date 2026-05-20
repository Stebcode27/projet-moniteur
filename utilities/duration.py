import sys
import os
import xml.etree.ElementTree as ET

# Ajouter le dossier racine du projet au path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)


def resource_path(relative_path):
    """ Récupère le chemin absolu vers la ressource, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Mode Production (.exe) : PyInstaller extrait tout directement dans sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)

    # Mode Développement (PyCharm) : On garde ta logique PROJECT_ROOT actuelle
    # 'dirname(__file__), ".."' permet de remonter au dossier racine du projet
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(PROJECT_ROOT, relative_path)

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

def extraire_donnees_moniteur(chaine_xml):
    root_xml = f"<data>{chaine_xml}</data>"

    try:
        root = ET.fromstring(root_xml)
        balises_a_verifier = ['HR', 'SPO2', 'RESP', 'TEMP', 'PNI/SYS', 'PNI/DIAS', 'PNI/PAM', 'TIMESTAMP']

        for chemin in balises_a_verifier:
            element = root.find(chemin)
            if element is None or element.text is None or element.text.strip() == "":
                return None

        donnees = {
            "hr": int(root.find('HR').text),
            "spo2": int(root.find('SPO2').text),
            "resp": int(root.find('RESP').text),
            "temp": float(root.find('TEMP').text),
            "pni": {
                "sys": int(root.find('PNI/SYS').text),
                "dias": int(root.find('PNI/DIAS').text),
                "pam": int(root.find('PNI/PAM').text)
            },
            "timestamp": root.find('TIMESTAMP').text
        }
        return donnees

    except (ET.ParseError, ValueError):
        # On attrape aussi ValueError au cas où le texte n'est pas convertible en nombre
        return None

def serialize_data_for_transmission():
    database_file = resource_path("datas/base_donnees.txt")
    infos_exam_file = resource_path("datas/patient_infos.txt")
    """Modèle de l'objet Json à envoyer au serveur pour le stockage"""

    data = {
        "patient": {},
        "medecin": "",
        "exam": {},
        "donnees": [],
    }

    with open(infos_exam_file, 'r+') as f:
        informations = f.readline().split("_")
        data['patient']['nom'] = informations[0]
        data['patient']['id'] = informations[1]
        data['patient']['age'] = informations[2]
        data['patient']['sexe'] = informations[3]
        data['patient']['poids'] = informations[4]
        data['patient']['taille'] = informations[5]

        data['exam']['salle'] = informations[6]
        data['exam']['service'] = informations[7]
        data['medecin'] = informations[8]
        data['exam']['debut_exam'] = informations[9]

    with open(database_file, 'r') as f:

        while True:
            line = f.readline()
            if line=='': break
            donnees = extraire_donnees_moniteur(line)
            data['donnees'].append(donnees)

    return data
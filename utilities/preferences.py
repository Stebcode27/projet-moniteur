"""Definition des preferences concernant le moniteur allant de l'interface utilisateur aux autres paramètres"""

#--------------------------GUI----------------------------#
COLOR_THEME = {
    'default': {
        'app-color': 'black',
        'container-color': '#1A1A1A',
        'font-familly': 'Roboto',
    },
    'solar': {
        'app-color': '#1A1A1A',
        'container-color': 'black',
        'font-familly': 'Arial',
    }
}

if __name__ == '__main__':
    print(COLOR_THEME['solar']['container-color'])
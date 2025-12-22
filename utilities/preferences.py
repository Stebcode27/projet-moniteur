"""Definition des preferences concernant le moniteur allant de l'interface utilisateur aux autres paramètres"""

#--------------------------GUI_PREFERENCES----------------------------#
COLOR_THEME = {
    'default': {
        'app-color': 'black',
        'container-color': '#1A1A1A',
        'font-family': 'Roboto',
    },
    'solar': {
        'app-color': "#1A1A1A",
        'container-color': 'black',
        'font-family': 'Arial',
    },
    'optimized': {
        'app-color': "#012C2D",
        'container-color': "#01021E",
        'font-family': 'Calibri',
    }
}

if __name__ == '__main__':
    print(COLOR_THEME['solar']['container-color'])
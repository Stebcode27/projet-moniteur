"""Definition des preferences concernant le moniteur allant de l'interface utilisateur aux autres paramètres"""

#--------------------------GUI_PREFERENCES----------------------------#
COLOR_THEME = {
    'default': {
        'app-color': "black",
        'container-color': 'black',
        'font-family': '-apple-system',
    },
    'optimized': {
        'app-color': 'black',
        'container-color': '#1A1A1A',
        'font-family': 'Roboto',
    },
    'solar': {
        'app-color': "#012C2D",
        'container-color': "#01021E",
        'font-family': 'Roboto',
    }
}

PARAMS_SEUILS = [
    {
        'id': 'HR',
        'val_min': 45,
        'val_max': 100,
    },{
        'id': 'SPO2',
        'val_min': 92,
    },{
        'id': 'PNI',
        'subparam': [
            {
                'id': 'PNI_SYS',
                'val_min': 0,
                'val_max': 1,
            },{
                'id': 'PNI_DIAS',
                'val_min': 0,
                'val_max': 1,
            },{
                'id': 'PNI_MOY',
                'val_min': 0,
                'val_max': 1,
            }
        ]
    },{
        'id': 'RESP',
        'val_min': 40,
        'val_max': 80,
    },{
        'id': 'TEMP',
        'val_min': 35,
        'val_max': 38.5,
    }
]

if __name__ == '__main__':
    print(COLOR_THEME['solar']['container-color'])
    print(PARAMS_SEUILS[2]['subparam'][0]['id'])
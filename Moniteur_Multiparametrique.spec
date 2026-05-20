# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# On liste ici tous les dossiers contenant des fichiers non-python (QSS, images, données)
# Syntaxe : ('nom_du_dossier_source', 'nom_du_dossier_destination')
dossiers_a_inclure = [
    ('assets', 'assets'),
    ('GUI', 'GUI'),
    ('datas', 'datas'),
    ('definitions', 'definitions'),
    ('utilities', 'utilities'),
    ('utils', 'utils')
]

a = Analysis(
    ['GUI/dashboard.py'],
    pathex=[],
    binaries=[],
    datas=dossiers_a_inclure,  # Injection de tes dossiers ici
    hiddenimports=['utilities', 'utils', 'wfdb'], # Sécurité pour être sûr que tes modules internes soient embarqués
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Moniteur_Multiparametrique',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # False pour ne pas afficher la console Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/surg.ico' # Optionnel : ajoute un fichier .ico si tu en as un dans tes assets
)
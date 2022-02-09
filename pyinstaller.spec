# -*- mode: python -*-

block_cipher = None


analysis = Analysis(
    ['./src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('settings.json', '.')
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(
    analysis.pure,
    analysis.zipped_data,
    cipher=block_cipher,
)
exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name='dcs_mission_buzzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    analysis.binaries,
    analysis.zipfiles,
    analysis.datas,
    strip=False,
    upx=True,
    name='dcs-mission-buzzer',
)

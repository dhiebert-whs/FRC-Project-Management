# -*- mode: python ; coding: utf-8 -*-
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # ('core/templates', 'core/templates'),
        (os.path.join(base_dir, 'core', 'templates'), 'core/templates'),
        (os.path.join(base_dir, 'core', 'templates', 'registration'), 'core/templates/registration'),
   
        ('static', 'static'),
        # Explicitly include authentication templates
        # ('core/templates/registration', 'core/templates/registration'),
    ],
    hiddenimports=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_widget_tweaks',
        'core',
        'core.version',          # Include version module
        'core.context_processors', # Include context processors
        'initialize',            # Include initialization script
    ],
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
    [],
    exclude_binaries=True,
    name='FRC_Project_Management',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/img/logo.ico',  # Add your logo if available
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FRC_Project_Management',
)
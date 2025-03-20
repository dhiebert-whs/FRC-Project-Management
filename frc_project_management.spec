# -*- mode: python ; coding: utf-8 -*-
import os

base_dir = os.path.dirname(os.path.abspath(__name__))

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
datas=[
    (os.path.join(base_dir, 'core', 'templates', 'base.html'), 'core/templates/core'),
    (os.path.join(base_dir, 'core', 'templates', '*.html'), 'core/templates/core'),
    (os.path.join(base_dir, 'core', 'templates', 'registration'), 'core/templates/registration'),
    (os.path.join(base_dir, 'static'), 'static'),
],
    hiddenimports=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_widget_tweaks',
        'widget_tweaks',
        'core',
        'core.version',          # Include version module
        'core.context_processors', # Include context processors
        'initialize',            # Include initialization script
        'django.contrib.auth.context_processors',
        'django.contrib.messages.templatetags',
        'django.contrib.auth.templatetags',
        'django.contrib.staticfiles.context_processors',
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
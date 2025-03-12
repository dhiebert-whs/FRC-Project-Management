# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect Django data files
django_data = collect_data_files('django')

# Collect all submodules from Django and other packages
django_submodules = collect_submodules('django')
widget_tweaks_submodules = collect_submodules('widget_tweaks')

# Add all necessary Python modules
added_modules = django_submodules + widget_tweaks_submodules

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('core/templates', 'core/templates'),
        ('static', 'static'),
        # Include Django and other package data files
        *django_data,
    ],
    hiddenimports=added_modules + [
        'django.template.defaulttags',
        'django.template.defaultfilters',
        'django.template.loader_tags',
        'django.templatetags.static',
        'svgwrite',
        'markdown',
        'widget_tweaks.templatetags.widget_tweaks',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FRC_Project_Management',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/favicon.ico',  # Add an icon if you have one
)
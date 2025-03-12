
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('core/templates', 'core/templates'),
        ('static', 'static'),
    ],
    hiddenimports=[
        'django.template.defaulttags',
        'django.template.defaultfilters',
        'django.template.loader_tags',
        'django.templatetags.static',
        'django.contrib.admin.apps',
        'django.contrib.auth.apps',
        'django.contrib.contenttypes.apps',
        'django.contrib.sessions.apps',
        'django.contrib.messages.apps',
        'django.contrib.staticfiles.apps',
        'widget_tweaks',
        'widget_tweaks.templatetags.widget_tweaks',
        'svgwrite',
        'markdown',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'django.contrib.gis',  # Exclude GIS which is causing warnings
    ],
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
)
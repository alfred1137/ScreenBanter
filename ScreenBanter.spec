# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# Add project root to path so we can import app modules if needed for analysis
project_root = os.path.abspath(os.getcwd())
sys.path.insert(0, project_root)

a = Analysis(
    ['app/main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'pystray._win32',
        'PIL._tkinter_finder',
        'customtkinter',
        'darkdetect',
        'dxcam',
        'google.genai',
        'google.genai.types',
        'google.generativeai',
        'google.ai.generativelanguage',
        'requests',
        'pyaudio',
        'app',
        'app.capture',
        'app.vision',
        'app.audio_client',
        'app.settings',
        'app.hud_window',
        'app.region_selector',
        'app.settings_window',
        'app.tts_manager',
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
    name='ScreenBanter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.ico'] if os.path.exists('assets/icon.ico') else None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ScreenBanter',
)

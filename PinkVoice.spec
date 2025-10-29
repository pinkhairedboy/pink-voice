# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/pink_voice/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('src/pink_voice/assets/icon.png', 'pink_voice/assets')],
    hiddenimports=[
        'pink_voice',
        'pink_voice.main',
        'pink_voice.config',
        'pink_voice.ui',
        'pink_voice.ui.base',
        'pink_voice.ui.macos',
        'pink_voice.ui.headless',
        'pink_voice.platform',
        'pink_voice.platform.clipboard',
        'pink_voice.platform.sounds',
        'pink_voice.platform.notifications',
        'pink_voice.services',
        'pink_voice.services.recorder',
        'pink_voice.services.transcribe',
        'pink_voice.hotkeys',
        'pink_voice.hotkeys.listener',
        'rumps',
        'pynput',
        'sounddevice',
        'numpy',
        'scipy',
        'objc',
        'HIServices',
        'Quartz',
        'CoreFoundation',
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
    name='Pink Voice',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Pink Voice',
)

app = BUNDLE(
    coll,
    name='Pink Voice.app',
    icon='src/pink_voice/assets/icon.icns',
    bundle_identifier='com.pink.voice',
    info_plist={
        'CFBundleName': 'Pink Voice',
        'CFBundleDisplayName': 'Pink Voice',
        'CFBundleIdentifier': 'com.pink.voice',
        'CFBundleVersion': '1.1.0',
        'CFBundleShortVersionString': '1.1.0',
        'LSUIElement': True,
        'LSMultipleInstancesProhibited': True,
        'NSHighResolutionCapable': True,
        'NSMicrophoneUsageDescription': 'Pink Voice needs microphone access for voice recording',
        'NSAccessibilityUsageDescription': 'Pink Voice needs accessibility access to detect Ctrl+Q hotkey',
    },
)

# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(['src/main.py'],
             pathex=[],
             binaries=[],
             datas=[
                 ('resources/icons/*', 'resources/icons'),
                 ('resources/qss/*', 'resources/qss'),
                 ('src/config/*.py', 'config'),
                 ('src/ui/*.py', 'ui'),
                 ('src/core/*.py', 'core')
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='PasswordManager',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon='resources/icons/app.ico')
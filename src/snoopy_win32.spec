# -*- mode: python -*-

block_cipher = None


added_files = [
  ('win32/nssm.exe','.'),
  ('win32/capture.exe','.'),
  ('mail.config','.')
]

snoopy = Analysis(['snoopy_win32.py'],
             pathex=['HOME_DIRECTORY'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(snoopy.pure, snoopy.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          snoopy.scripts,
          exclude_binaries=True,
          name='snoopy',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               snoopy.binaries,
               snoopy.zipfiles,
               snoopy.datas,
               strip=False,
               upx=True,
               name='snoopy')

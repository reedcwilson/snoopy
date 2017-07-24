# -*- mode: python -*-

block_cipher = None


added_files = [
  ('reload_service.exe','.'),
  ('win32/nssm.exe','.'),
  ('win32/capture.exe','.'),
  ('mail.config','.')
]

a = Analysis(['snoopy_win32.py'],
             pathex=['//psf/Home/code/snoopy'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='snoopy',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries + binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='snoopy')

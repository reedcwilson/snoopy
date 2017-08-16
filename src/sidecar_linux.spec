# -*- mode: python -*-

block_cipher = None


added_files = [
  ('linux/start.sh','.'),
  ('../config/sidecar.service','.'),
  ('../config/snoopy.service','.'),
]

a = Analysis(['sidecar_linux.py'],
             pathex=['HOME_DIRECTORY'],
             #pathex=['/home/parallels/code/snoopy/src'],
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
          name='sidecar',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='sidecar')

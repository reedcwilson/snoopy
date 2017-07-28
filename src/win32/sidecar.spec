# -*- mode: python -*-

block_cipher = None


sidecar = Analysis(['sidecar.py'],
             pathex=['c:\\Users\\rwilson\\code\\snoopy\\src\\win32'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(sidecar.pure, sidecar.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          sidecar.scripts,
          exclude_binaries=True,
          name='sidecar',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               sidecar.binaries,
               sidecar.zipfiles,
               sidecar.datas,
               strip=False,
               upx=True,
               name='sidecar')

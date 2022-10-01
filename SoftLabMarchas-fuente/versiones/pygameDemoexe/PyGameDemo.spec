# -*- mode: python -*-
a = Analysis(['PyGameDemo.py'],
             pathex=['D:\\YAGUI\\PROYECTO LAB MARCHAS\\Pasos del proyecto\\work_folder\\pygameDemoexe'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='PyGameDemo.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='PyGameDemo')

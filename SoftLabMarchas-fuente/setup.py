from distutils.core import setup
import py2exe
from glob import glob

#sys.path.append("C:\\Program Files\\Microsoft Visual Studio 9.0\\VC\\redist\\x86\\Microsoft.VC90.CRT")

mis_datos =[('phonon_backend', ['C:\Python27\Lib\site-packages\PyQt4\plugins\phonon_backend\phonon_ds94.dll']),
            ("Microsoft.VC90.CRT", glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]
#[('iconos', ['D:\YAGUI\PROYECTO LAB MARCHAS\Pasos del proyecto\work_folder\iconos\config.png']),
              #('iconos', ['D:\YAGUI\PROYECTO LAB MARCHAS\Pasos del proyecto\work_folder\iconos\datos.png']),
              #('iconos', ['D:\YAGUI\PROYECTO LAB MARCHAS\Pasos del proyecto\work_folder\iconos\curva.png']),
              #('iconos', ['D:\YAGUI\PROYECTO LAB MARCHAS\Pasos del proyecto\work_folder\iconos\iniciar.png']),
              #('iconos', ['D:\YAGUI\PROYECTO LAB MARCHAS\Pasos del proyecto\work_folder\iconos\video.png']),
              #('iconos', ['D:\YAGUI\PROYECTO LAB MARCHAS\Pasos del proyecto\work_folder\iconos\UNNe.gif']),             


setup(windows=[{"script": "AMEN.py"}], 
        data_files = mis_datos,
        options={"py2exe":{"includes":["sip", "PyQt4", "numpy"], "bundle_files": 3, "compressed": False}}
        )

#mysetup.py
import os
from distutils.core import setup
import py2exe
mfcdir = 'C:\Python27\Lib\site-packages\pythonwin'
mfcfiles = [os.path.join(mfcdir, i) for i in ["mfc90.dll", "mfc90u.dll", "mfcm90.dll", "mfcm90u.dll", "Microsoft.VC90.MFC.manifest"]]
data_files = [("Microsoft.VC90.MFC", mfcfiles),
              ]
setup(console=["Main.py"],
      data_files=data_files,
      )
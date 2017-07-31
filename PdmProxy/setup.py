# -*- coding: utf-8 -*-
import msilib
import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", 'tornado'], "excludes": ["tkinter",'collections.abc']}

# GUI applications require a different base on Windows (the default is for a
# console application).
# product_name = 'PdmProxy'
# product_desc = 'Pdm Proxy'
# product_code = msilib.gen_uuid()
# # 快捷方式表，这里定义了三个快捷方式
# shortcut_table = [
#
#     # 1、桌面快捷方式
#     ("DesktopShortcut",  # Shortcut
#      "DesktopFolder",  # Directory_ ，必须在Directory表中
#      product_name,  # Name
#      None,  # Arguments
#      product_desc,  # Description
#      None,  # Hotkey
#      None,  # Icon
#      None,  # IconIndex
#      None,  # ShowCmd
#      ),
#
#     # 2、开始菜单快捷方式
#     ("StartupShortcut",  # Shortcut
#      "MenuDir",  # Directory_
#      product_name,  # Name
#      None,  # Arguments
#      product_desc,  # Description
#      None,  # Hotkey
#      None,  # Icon
#      None,  # IconIndex
#      None,  # ShowCmd
#      ),
# ]
#
# directories = [
#      ( "ProgramMenuFolder","TARGETDIR","." ),
#      ( "MenuDir", "ProgramMenuFolder", product_name)
#      ]
# msi_data = {#"Directory":directories ,
#             "Shortcut": shortcut_table
#           }
# bdist_msi_options = { 'data': msi_data,
#                       'upgrade_code': '{9f21e33d-48f7-cf34-33e9-efcfd80eed10}',
#                       'add_to_path': False,
#                       'directories': directories,
#                       'initial_target_dir': r'[ProgramFilesFolder]\%s' % (product_name)}
base = None
if sys.platform == "win32":
    base = "Win32GUI"
setup(  name = "PdmProxy",
        version = "0.1",
        description = "PdmProxy!",
        options = {"build_exe": build_exe_options,
                   # "bdist_msi": bdist_msi_options
                   },
        executables = [Executable("Main.py", base=base, shortcutName='PdmProxy', shortcutDir='DesktopFolder')])
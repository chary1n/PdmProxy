"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""
import platform

from setuptools import setup

APP = ['Main.py']
DATA_FILES = []
prefer_ppc = platform.processor() == 'powerpc'
OPTIONS = {
        'argv_emulation': True,
        'prefer_ppc': prefer_ppc,
        'semi_standalone': True,
        'site_packages': True,
        'iconfile': 'logo.icns'
        # 'includes': ['tornado']
}
setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

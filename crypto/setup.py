import os
import sys
from distutils.core import setup, Extension

module_pycryptsetup = Extension('pycryptsetup',
                                    include_dirs = ['/usr/include/python3.5m'],
                                    libraries = ['cryptsetup'],
                                    sources = ['pycryptsetup.c'])

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0], 'build_ext', '-i']
setup(name = 'pycryptsetup',
      description = 'CryptSetup pythonized API.',
      ext_modules = [ module_pycryptsetup ])

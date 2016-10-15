from setuptools import setup, Extension

module_pycryptsetup = Extension('pycryptsetup',
                                    include_dirs = ['/usr/include/python3'],
                                    libraries = ['cryptsetup'],
                                    sources = ['pycryptsetup.c'])

setup(name = 'pycryptsetup',
      description = 'CryptSetup pythonized API.',
      ext_modules = [ module_pycryptsetup ])

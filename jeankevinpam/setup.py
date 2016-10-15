from setuptools import setup

setup(name='jeankevinpam',
      version='0.1',
      description='PAM module that handle encrypted volumes',
      url='http://www.perdu.com',
      author='Bastien DHIVER',
      author_email='epitech@bastn.fr',
      license='GPLv2',
      packages=['jeankevinpam'],
      install_requires=[
          'simplejson',
          'pysqlcipher3',
          'python-systemd'
      ],
)

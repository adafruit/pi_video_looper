from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name              = 'NURD_Video_Looper',
      version           = '1.0.0',
      author            = 'Nurds',
      author_email      = 'ben@nurd.me',
      description       = 'Application to turn your Raspberry Pi Zero into a dedicated looping video playback device',
      license           = 'GNU GPLv2',
      url               = 'https://github.com/FRCTeam3255/pi_video_looper',
      install_requires  = ['pyudev'],
      packages          = find_packages())

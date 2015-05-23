import os
import sys


try:
    from setuptools import setup
except ImportError:
    import warnings
    warnings.warn('No setuptools. Script creation will be skipped.')
    from distutils.core import setup


setup(name='juicer',
      version='1.0.0',
      description='Administer Pulp and Release Carts',
      maintainer='Tim Bielawa',
      maintainer_email='tbielawa@redhat.com',
      url='https://github.com/juicer/juicer',
      license='GPLv3+',
      package_dir={ 'juicer': 'juicer' },
      packages=[
          'juicer',
          'juicer.command',
          'juicer.common',
          'juicer.parser',
          'juicer.pulp',
      ],
      entry_points={
          'console_scripts': [
              'juicer = juicer.parser.Parser:main',
          ],
      }
)

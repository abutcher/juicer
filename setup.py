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
          'juicer.cart',
          'juicer.common',
          'juicer.config',
          'juicer.interface',
          'juicer.juicer',
          'juicer.log',
          'juicer.rpm'
      ],
      entry_points={
          'console_scripts': [
              'juicer = juicer.juicer.Parser:main',
          ],
      }
)

import os
import sys

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
          'juicer.config',
          'juicer.juicer',
          'juicer.log'
      ],
      scripts=[
         'bin/juicer'
      ]
)

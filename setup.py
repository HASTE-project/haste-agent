#!/usr/bin/env python

from setuptools import setup

setup(name='haste_desktop_agent',
      version='0.10',
      packages=[
                'haste.desktop_agent'],
      description='Desktop Client for the HASTE platform: http://http://haste.research.it.uu.se',
      author='Ben Blamey',
      author_email='ben.blamey@it.uu.se',
      install_requires=[
          'watchdog',
          'aiohttp'

          # 'requests',
          # 'requests-futures'

          # 'pymongo',
          # 'python-swiftclient',
          # 'keystoneauth1',
          # 'future',
      ],
      test_requires=[
          'pytest'
      ]
      )

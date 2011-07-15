#!/usr/bin/env python
# encoding: utf-8
import sys
from distutils.core import setup

if sys.version_info >= (3, 0):
    package = {'': 'seat/3.x.x'}
else:
    package = {'': 'seat/2.x.x'}

setup(
    name='seat',
    version='0.2.4',
    description='Seat-Python is an elegant and lightweight REST interface to CouchDB, complete with ORM.',
    author='Fredrick Galoso - Stackd, LLC',
    license='MIT/X11',
    url='https://github.com/stackd/seat-py',
    download_url='https://github.com/stackd/seat-py',
    requires=['pyyaml'],
    package_dir=package,
    py_modules=[
        'seat',
    ],
)

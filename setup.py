#!/usr/bin/env python
# encoding: utf-8
from distutils.core import setup

setup(
    name='seat',
    version='0.2.4',
    description='Seat-Python is an elegant and lightweight REST interface to CouchDB, complete with ORM.',
    author='Fredrick Galoso - Stackd, LLC',
    license='MIT/X11',
    url='https://github.com/stackd/seat-py',
    download_url='https://github.com/stackd/seat-py',
    package_dir={'': 'seat'},
    py_modules=[
        'seat',
    ],
)

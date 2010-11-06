#!/usr/bin/env python
# encoding: utf-8
from distutils.core import setup
 
setup(
    name = 'seat',
    version = '0.1.1',
    description = 'Seat-Python is an elegant and lightweight REST interface to CouchDB.',
    author = 'Fredrick Galoso - Stackd',
    url = 'http://github.com/stackd/seat-py',
	download_url = 'http://github.com/stackd/seat-py.git',
    package_dir = {'': 'src'},
    py_modules = [
        'seat',
    ],
)
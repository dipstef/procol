#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.2',
    'Topic :: Internet',
    'Topic :: Utilities',
]

settings = dict(
    name='procol',
    version='0.1',
    description='A concurrent processing library',
    long_description=open('README.rst').read(),
    author='Stefano Dipierro',
    license='Apache 2.0',
    url='https://github.com/dipstef/procol',
    classifiers=CLASSIFIERS,
    keywords='process thread multiprocessing pool scheduler zmq',
    packages=['procol', 'procol.queue', 'procol.pool'],
    requires=['pyzmq', 'funlib'],
    test_suite='tests'
)

setup(**settings)
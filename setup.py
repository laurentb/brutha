#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import version_info

from setuptools import setup

assert version_info >= (2, 6)
requirements = ['mutagen']
if version_info < (2, 7):
    requirements.append('argparse')

setup(
    name='brutha',
    version='1.0.2',
    description='Sync FLAC music files to Ogg Vorbis (or keep lossy as-is)',
    long_description=open('README').read(),
    author='Laurent Bachelier',
    author_email='laurent@bachelier.name',
    url='http://git.p.engu.in/laurentb/brutha/',
    packages=['brutha'],
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
    ],
    entry_points={'console_scripts': ['brutha = brutha.__main__:main']},
)

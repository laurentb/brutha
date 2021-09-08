#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import version_info

from setuptools import setup

assert version_info >= (3, 2)  # 'argparse' module requires Python 3.2 or later
requirements = ['mutagen']

setup(
    name='brutha',
    version='1.1.1',
    description='Sync FLAC music files to Ogg Vorbis (or keep lossy as-is)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Laurent Bachelier',
    author_email='laurent@bachelier.name',
    url='http://git.p.engu.in/laurentb/brutha/',
    packages=['brutha'],
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
    ],
    entry_points={'console_scripts': ['brutha = brutha.__main__:main']},
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='brutha',
    version='0.0.0',
    description='Sync FLAC music files to Ogg Vorbis (or keep lossy as-is)',
    long_description=open('README').read(),
    author='Laurent Bachelier',
    author_email='laurent@bachelier.name',
    url='http://git.p.engu.in/laurentb/brutha/',
    packages=['brutha'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
    ],
    entry_points={'console_scripts': ['brutha = brutha.__main__:main']},
)

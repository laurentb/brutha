# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import re

from .file import FlacFile, LossyFile
from .util import escape


class NotInteresting(Exception):
    """
    A directory with no sound files whatsoever
    """
    pass


class Directory(object):
    def __init__(self, path, destpath, options=None, _files=None):
        assert os.path.isdir(path)
        self.path = path
        self.destpath = destpath
        self.options = {}
        if options:
            self.options.update(options)
        self._files = _files or \
            [f for f in os.listdir(self.path) if not os.path.isdir(f)]

    def commands(self):
        commands = []
        files = list(self.files())
        if not len(files):
            raise NotInteresting("No sound files")

        if not os.path.isdir(self.destpath):
            commands.append(self.mkdir())

        for f in files:
            commands.extend(f.pre())
        if not all([f.uptodate() for f in files]) and self.options['gain']:
            commands.append(self.vorbisgain())
        for f in files:
            commands.extend(f.post())
        return commands

    def wanted(self):
        d = os.path.normpath(self.destpath)
        while len(d) > 1:
            yield d
            # all parent directories are wanted, too
            d = os.path.normpath(os.path.join(d, os.path.pardir))
        for f in self.files():
            yield os.path.normpath(f.dest())

    def files(self):
        flacs = self.flacs()
        mp3s = self.mp3s()
        oggs = self.oggs()
        for flac in flacs:
            yield FlacFile(self.path, self.destpath, flac, self.options)
        for mp3 in mp3s:
            yield LossyFile(self.path, self.destpath, mp3, self.options)
        for ogg in oggs:
            yield LossyFile(self.path, self.destpath, ogg, self.options)

    def mkdir(self):
        return 'mkdir -p %s' % escape(os.path.join(self.destpath))

    def vorbisgain(self):
        return 'vorbisgain -q -s -f -a %s' % escape(os.path.join(self.destpath))

    def flacs(self):
        return self.type_files('flac')

    def mp3s(self):
        return self.type_files('mp3')

    def oggs(self):
        return self.type_files('ogg')

    def type_files(self, ext):
        pattern = re.compile(r'\.%s$' % re.escape(ext), flags=re.IGNORECASE)

        return [f for f in self._files if pattern.search(f)]

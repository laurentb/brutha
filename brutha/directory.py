# -*- coding: utf-8 -*-

import re
import os

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
        flacs = self.flacs()
        mp3s = self.mp3s()
        oggs = self.oggs()
        if not any(flacs + mp3s + oggs):
            raise NotInteresting("No sound files")

        if not os.path.isdir(self.destpath):
            commands.append(self.mkdir_command())
        for flac in flacs:
            f = FlacFile(self.path, self.destpath, flac, self.options)
            commands.append(f.commands())
        for mp3 in mp3s:
            f = LossyFile(self.path, self.destpath, mp3, self.options)
            commands.append(f.commands())
        for ogg in oggs:
            f = LossyFile(self.path, self.destpath, ogg, self.options)
            commands.append(f.commands())
        return commands

    def mkdir_command(self):
        return 'mkdir -pv %s' % escape(os.path.join(self.destpath))

    def flacs(self):
        return self.files('flac')

    def mp3s(self):
        return self.files('mp3')

    def oggs(self):
        return self.files('ogg')

    def files(self, ext):
        pattern = re.compile(r'\.%s$' % re.escape(ext), flags=re.IGNORECASE)

        return [f for f in self._files if pattern.search(f)]

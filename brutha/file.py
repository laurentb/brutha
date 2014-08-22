# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import re
from datetime import datetime
from time import localtime

import mutagen
from mutagen.flac import FLACNoHeaderError, FLACVorbisError

from .util import escape


class NotAllowed(Exception):
    pass


def mtime(path):
    """
    Get a comparable modification time for a file.
    None if it does not exist.
    """
    if os.path.exists(path):
        return int(datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y%m%d%H%M%s'))


class File(object):
    def __init__(self, path, destpath, name, options):
        self.path = path
        self.destpath = destpath
        self.name = name
        self.options = options

    def destname(self):
        raise NotImplementedError()

    def pre(self):
        raise NotImplementedError()

    def post(self):
        commands = []
        if not self.uptodate():
            self.touch(commands)
        return commands

    def touch(self, commands):
        mtime = os.path.getmtime(self.src())
        i = localtime(mtime)
        stamp = "%s%s%s%s%s.%s" % (
                str(i.tm_year).zfill(4),
                str(i.tm_mon).zfill(2), str(i.tm_mday).zfill(2),
                str(i.tm_hour).zfill(2), str(i.tm_min).zfill(2),
                str(i.tm_sec).zfill(2))
        commands.append('touch -t%s -c -m %s' % (stamp, escape(self.dest())))

    def src(self):
        return os.path.join(self.path, self.name)

    def dest(self):
        return os.path.join(self.destpath, self.destname())

    def uptodate(self):
        return mtime(self.src()) == mtime(self.dest())


class FlacFile(File):
    PATTERN = re.compile(r'\.flac$', flags=re.IGNORECASE)

    def destname(self):
        return self.PATTERN.sub('.ogg', self.name)

    def pre(self):
        commands = []
        if not self.uptodate():
            self.transcode(commands)
        return commands

    def resample(self):
        rate = bits = ''
        if self.options['maxrate'] or self.options['maxbits']:
            try:
                f = mutagen.File(self.src())
            except FLACNoHeaderError:
                raise NotAllowed("Could not read FLAC header")
            except FLACVorbisError:
                raise NotAllowed("FLAC Vorbis error")
            if self.options['maxrate'] and f.info.sample_rate > self.options['maxrate']:
                rate = ' rate -v -L %s dither' % self.options['maxrate']
            if self.options['maxbits'] and f.info.bits_per_sample > self.options['maxbits']:
                bits = ' -b %s' % self.options['maxbits']
        return (rate, bits)

    def transcode(self, commands):
        rate, bits = self.resample()
        commands.append('sox -V1 %s -C %s%s %s%s' %
                        (escape(self.src()), self.options['quality'], bits, escape(self.dest()), rate))


class LossyFile(File):
    def destname(self):
        return self.name

    def pre(self):
        commands = []
        if not self.uptodate():
            self.copy(commands)
        return commands

    def copy(self, commands):
        if not self.sample_ok():
            raise NotAllowed("Sample rate or bit depth too high")
        commands.append('cp %s %s' % (escape(self.src()), escape(self.dest())))

    def sample_ok(self):
        if not self.options['lossycheck']:
            return True

        f = mutagen.File(self.src())
        try:
            if self.options['maxrate'] and f.info.sample_rate > self.options['maxrate']:
                return False
        except AttributeError:
            pass

        try:
            if self.options['maxbits'] and f.info.bits_per_sample > self.options['maxbits']:
                return False
        except AttributeError:
            pass

        return True

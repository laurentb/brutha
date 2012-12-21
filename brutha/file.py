# -*- coding: utf-8 -*-

import os
import re
from time import localtime


class File(object):
    def __init__(self, path, destpath, name):
        self.path = path
        self.destpath = destpath
        self.name = name

    def commands(self):
        raise NotImplementedError()

    def touch(self, commands):
        mtime = os.path.getmtime(self.src())
        i = localtime(mtime)
        stamp = "%s%s%s%s%s.%s" % (str(i.tm_year).zfill(4),
                str(i.tm_mon).zfill(2), str(i.tm_mday).zfill(2),
                str(i.tm_hour).zfill(2), str(i.tm_min).zfill(2),
                str(i.tm_sec).zfill(2))
        commands.append("touch -t%s -c -m '%s'" % (stamp, self.dest()))

    def src(self):
        return os.path.join(self.path, self.name)

    def dest(self):
        return os.path.join(self.destpath, self.destname)


class FlacFile(File):
    PATTERN = re.compile(r'\.flac$')

    def __init__(self, path, destpath, name):
        File.__init__(self, path, destpath, name)
        self.destname = self.PATTERN.sub('.ogg', self.name)

    def commands(self):
        commands = []
        self.transcode(commands)
        self.touch(commands)
        return commands

    def transcode(self, commands):
        commands.append("oggenc -q8 '%s' -o '%s'" % (self.src(), self.dest()))


class LossyFile(File):
    def __init__(self, path, destpath, name):
        File.__init__(self, path, destpath, name)
        self.destname = self.name

    def commands(self):
        commands = []
        self.copy(commands)
        self.touch(commands)
        return commands

    def copy(self, commands):
        commands.append("cp -v '%s' '%s'" % (self.src(), self.dest()))

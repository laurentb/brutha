# -*- coding: utf-8 -*-

import os
import re
from time import localtime
from datetime import datetime

from .util import escape


def mtime(path):
    """
    Get a comparable modification time for a file.
    None if it does not exist.
    """
    if os.path.exists(path):
        return int(datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y%m%d%H%M%s'))


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
        commands.append("touch -t%s -c -m %s" % (stamp, escape(self.dest())))

    def src(self):
        return os.path.join(self.path, self.name)

    def dest(self):
        return os.path.join(self.destpath, self.destname)

    def uptodate(self):
        return mtime(self.src()) == mtime(self.dest())

class FlacFile(File):
    PATTERN = re.compile(r'\.flac$', flags=re.IGNORECASE)

    def __init__(self, path, destpath, name):
        File.__init__(self, path, destpath, name)
        self.destname = self.PATTERN.sub('.ogg', self.name)

    def commands(self):
        commands = []
        if not self.uptodate():
            self.transcode(commands)
            self.touch(commands)
        return commands

    def transcode(self, commands):
        commands.append("oggenc -q8 %s -o %s" % (escape(self.src()), escape(self.dest())))


class LossyFile(File):
    def __init__(self, path, destpath, name):
        File.__init__(self, path, destpath, name)
        self.destname = self.name

    def commands(self):
        commands = []
        if not self.uptodate():
            self.copy(commands)
            self.touch(commands)
        return commands

    def copy(self, commands):
        commands.append("cp -v %s %s" % (escape(self.src()), escape(self.dest())))

# -*- coding: utf-8 -*-

import re
import os
from time import localtime


class NotInteresting(Exception):
    """
    A directory with no sound files whatsoever
    """
    pass


class Weird(Exception):
    """
    A "weird" directory, for instance with two different types of sound files
    """
    pass


class Directory(object):
    def __init__(self, path, destpath, options=None):
        assert os.path.isdir(path)
        self.path = path
        self.destpath = destpath
        self.commands = []
        self.options = {}
        if options:
            self.options.update(options)

    def analyze(self):
        flacs = self.get_flacs()
        mp3s = self.get_mp3s()
        oggs = self.get_oggs()
        if not any(flacs + mp3s + oggs):
            raise NotInteresting("No sound files")

        if ((len(flacs) > 0) + (len(mp3s) > 0) + (len(oggs) > 0)) > 1:
            raise Weird("More than one sound file type")

        self.commands.append(self.get_mkdir_command())
        if flacs:
            self.transcode_flacs(flacs)
        else:
            self.copy_files(mp3s or oggs)

    def get_commands(self):
        self.commands = []
        self.analyze()
        return "\n".join(self.commands)

    def transcode_flacs(self, files):
        pattern = re.compile(r'\.flac$')
        for f in files:
            df = pattern.sub('.ogg', f)
            self.add_command(self.get_oggenc_command(f, df))
            self.add_command(self.get_touch_command(f, df))

    def copy_files(self, files):
        for f in files:
            self.add_command(self.get_copy_command(f))
            self.add_command(self.get_touch_command(f, f))

    def get_touch_command(self, f, df):
        """
        f = where to get the time
        df = where to set the time
        """
        mtime = os.path.getmtime(self.get_path(f))
        i = localtime(mtime)
        stamp = "%s%s%s%s%s.%s" % (str(i.tm_year).zfill(4), \
                str(i.tm_mon).zfill(2), str(i.tm_mday).zfill(2), \
                str(i.tm_hour).zfill(2), str(i.tm_min).zfill(2), \
                str(i.tm_sec).zfill(2))

        return "touch -t%s -c -m '%s'" % (stamp, self.get_destpath(df))

    def get_copy_command(self, f):
        return "cp -v '%s' '%s'" % (self.get_path(f), self.get_destpath(f))

    def get_oggenc_command(self, f, df):
        return "oggenc -q8 '%s' -o '%s'" % \
                (self.get_path(f), self.get_destpath(df))

    def get_mkdir_command(self):
        return 'mkdir -pv %s' % os.path.join(self.destpath)

    def get_flacs(self):
        return self.get_files('flac')

    def get_mp3s(self):
        return self.get_files('mp3')

    def get_oggs(self):
        return self.get_files('ogg')

    def get_files(self, ext):
        pattern = re.compile(r'\.%s$' % re.escape(ext))
        files = os.listdir(self.path)

        return [f for f in files if pattern.search(f)]

    def add_command(self, cmd):
        self.commands.append(cmd)

    def get_path(self, f):
        return os.path.join(self.path, f)

    def get_destpath(self, df):
        return os.path.join(self.destpath, df)

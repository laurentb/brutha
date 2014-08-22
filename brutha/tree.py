# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from .directory import Directory, NotInteresting
from .file import NotAllowed
from .util import escape


class Tree(object):
    def __init__(self, path, destpath, options=None, log=None):
        assert os.path.isdir(path)
        self.path = path
        self.destpath = destpath
        self.options = {'quality': 8, 'gain': False, 'delete': False,
                        'maxrate': None, 'maxbits': None, 'lossycheck': True}
        if options:
            self.options.update(options)
        self.log = log

    def commands(self):
        commands = []
        wanted = []
        num = 0
        if self.log:
            print >>self.log, "Walking source directory..."
        for root, dirs, files in os.walk(self.path, followlinks=True):
            num += 1
            if not num % 200:
                self.progress(num)
            relpath = os.path.relpath(root, self.path)
            if relpath != '.':
                destpath = os.path.join(self.destpath, relpath)
            else:
                destpath = self.destpath
            try:
                d = Directory(root, destpath, self.options, _files=files)
                c = d.commands()
                if c:
                    commands.append(c)
                wanted.extend(d.wanted())
            except NotInteresting:
                pass
            except NotAllowed as e:
                commands.append(['echo %s' % escape('%s: %s' % (root, str(e)))])

        if self.options['delete']:
            if self.log:
                print >>self.log, "Walking destination directory..."
            c = list(self.delete(wanted))
            if c:
                commands.append(c)
        return commands

    def delete(self, wanted):
        num = 0
        for root, dirs, files in os.walk(self.destpath, topdown=False, followlinks=False):
            num += 1
            if not num % 2000:
                self.progress(num)
            for d in dirs:
                d = os.path.normpath(os.path.join(root, d))
                if d not in wanted:
                    yield 'rmdir %s' % escape(d)
            for f in files:
                f = os.path.normpath(os.path.join(root, f))
                if f not in wanted:
                    yield 'rm %s' % escape(f)

    def progress(self, num):
        if self.log:
            print >>self.log, "%s directories processed..." % num

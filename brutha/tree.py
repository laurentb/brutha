# -*- coding: utf-8 -*-

import os
from .directory import Directory, NotInteresting
from .util import escape


class Tree(object):
    def __init__(self, path, destpath, options=None):
        assert os.path.isdir(path)
        self.path = path
        self.destpath = destpath
        self.options = {'quality': 8, 'gain': False, 'delete': False,
                        'maxrate': None, 'maxbits': None}
        if options:
            self.options.update(options)

    def commands(self):
        commands = []
        wanted = []
        for root, dirs, files in os.walk(self.path, followlinks=True):
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
        if self.options['delete']:
            c = list(self.delete(wanted))
            if c:
                commands.append(c)
        return commands

    def delete(self, wanted):
        for root, dirs, files in os.walk(self.destpath, topdown=False, followlinks=False):
            for d in dirs:
                d = os.path.join(root, d)
                if d not in wanted:
                    yield 'rmdir -v %s' % escape(d)
            for f in files:
                f = os.path.join(root, f)
                if f not in wanted:
                    yield 'rm -v %s' % escape(f)

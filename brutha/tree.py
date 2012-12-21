# -*- coding: utf-8 -*-

import os
from .directory import Directory, NotInteresting


class Tree(object):
    def __init__(self, path, destpath, options=None):
        assert os.path.isdir(path)
        self.path = path
        self.destpath = destpath
        self.options = {'quality': 8}
        if options:
            self.options.update(options)

    def commands(self):
        commands = []
        for root, dirs, files in os.walk(self.path, followlinks=True):
            relpath = os.path.relpath(root, self.path)
            if relpath != '.':
                destpath = os.path.join(self.destpath, relpath)
            else:
                destpath = self.destpath
            try:
                d = Directory(root, destpath, self.options, _files=files)
                commands.append(d.commands())
            except NotInteresting:
                pass
        return commands

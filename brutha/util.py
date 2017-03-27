# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os


def escape(x):
    if '\'' not in x:
        return '\'' + x + '\''
    s = '"'
    for c in x:
        if c in '\\$"`':
            s = s + '\\'
        s = s + c
    s = s + '"'
    return s


def find_executable(name, names=None):
    envname = '%s_EXECUTABLE' % name.upper()
    if names is None:
        names = [name]
    if os.getenv(envname):
        return os.getenv(envname)
    paths = os.getenv('PATH', os.defpath).split(os.pathsep)
    exts = os.getenv('PATHEXT', os.pathsep).split(os.pathsep)
    for name in names:
        for path in paths:
            for ext in exts:
                fpath = os.path.join(path, name) + ext
                if os.path.exists(fpath) and os.access(fpath, os.X_OK):
                    return fpath


def require_executable(name, names=None):
    e = find_executable(name, names)
    if e:
        return e
    raise Exception('Could not find executable: %s' % name)


def default_output(cores=None):
    if cores and cores > 1:
        if find_executable('parallel'):
            return 'parallel'
        if find_executable('make', ['gmake', 'make']):
            return 'make'
    return 'sh'

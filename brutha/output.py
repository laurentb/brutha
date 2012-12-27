# -*- coding: utf-8 -*-
from __future__ import division

import subprocess

from brutha.util import find_executable


def pbar(cur, total, color=True):
    "Progress bar"
    if color:
        BRIGHT = '\x1b[1m'
        NORMAL = '\x1b[22m'
    else:
        BRIGHT = ''
        NORMAL = ''
    if total == 0:
        pct = 100
    else:
        pct = int(100 * cur / total)

    bar = (int(pct/10) * '#') + (int(10-pct/10) * ' ')
    return "echo '%s[%s] (%s%%)%s'" % (BRIGHT, bar, pct, NORMAL)


# PRINTERS


def sh(p, commands, echo=False):
    p('#!%s' % find_executable('sh', ['bash', 'zsh', 'dash', 'sh']))
    p('set -eu')
    if echo:
        p('set -x')
    for i, subcommands in enumerate(commands):
        p("\n".join(subcommands))
        if echo:
            p('( set +x ; %s ) 2>/dev/null' % pbar(i+1, len(commands)))
        else:
            p(pbar(i+1, len(commands)))
        p()


def parallel(p, commands, echo=False):
    p('#!%s --shebang%s --' % (find_executable('parallel'), (' --verbose' if echo else '')))
    for i, subcommands in enumerate(commands):
        p(" && ".join(subcommands + [pbar(i+1, len(commands))]))


def make(p, commands, echo=False):
    prefix = '' if echo else '@'
    targets = ' '.join('d%s' % i for i in xrange(0, len(commands)))
    p('.PHONY: all %s' % targets)
    p('all: %s' % targets)
    p()
    for i, subcommands in enumerate(commands):
        p('d%s:' % i)
        for subcommand in subcommands:
            p('\t%s%s' % (prefix, subcommand))
        p('\t@%s' % pbar(i+1, len(commands)))


PRINTERS = {'sh': sh, 'parallel': parallel, 'make': make}


# EXECUTORS


def shebang(stream):
    """
    Extracts the shebang (#!) line and runs it, with the script provided as stdin.
    This is known to work at least with bash and GNU parallel.
    """
    stream.seek(0)
    line = stream.readline()
    assert line.startswith('#!')
    shebang = line[2:].split()
    p = subprocess.Popen(shebang, shell=False, stdin=subprocess.PIPE)
    p.communicate(stream.getvalue())
    return p.returncode


def emake(stream):
    p = subprocess.Popen([find_executable('make', ['gmake', 'make']), '-f', '-'], shell=False, stdin=subprocess.PIPE)
    p.communicate(stream.getvalue())
    return p.returncode


EXECUTORS = {'sh': shebang, 'parallel': shebang, 'make': emake}

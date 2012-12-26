#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import argparse
import sys

from brutha.tree import Tree
from brutha.util import uprint


def pbar(cur, total, color=True):
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


def sh(p, commands, echo=False):
    p('#!/bin/sh')
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
    p('#!/usr/bin/parallel --shebang%s --' % (' --verbose' if echo else ''))
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


if __name__ == '__main__':
    printers = {'sh': sh, 'parallel': parallel, 'make': make}

    parser = argparse.ArgumentParser(
        description='Sync FLAC music files to Ogg Vorbis (or keep lossy as-is).')
    parser.add_argument('-q', '--quality', default=8, type=int,
                        help='Ogg Vorbis quality, -1 to 10, default 8')
    parser.add_argument('-g', '--gain', action='store_true',
                        help='Compute ReplayGain if missing')
    parser.add_argument('-d', '--delete', action='store_true',
                        help='Delete extraneous files in destination')
    parser.add_argument('-o', '--output', default='sh',
                        help='Command list type (%s), default sh' % ', '.join(printers.keys()))
    parser.add_argument('-R', '--maxrate', type=int,
                        help='Maximum sample rate allowed (e.g. 44100)', metavar='RATE')
    parser.add_argument('-B', '--maxbits', type=int,
                        help='Maximum bit depth allowed (e.g. 16)', metavar='BITS')
    parser.add_argument('-e', '--echo', action='store_true',
                        help='Show started commands')
    parser.add_argument('src', help='Source directory', metavar='SOURCE')
    parser.add_argument('dest', help='Destination directory', metavar='DESTINATION')
    args = parser.parse_args()

    tree = Tree(args.src, args.dest,
                {'quality': args.quality, 'gain': args.gain, 'delete': args.delete,
                 'maxrate': args.maxrate, 'maxbits': args.maxbits})
    p = uprint(sys.stdout)
    printers[args.output](p, tree.commands(), args.echo)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from brutha.tree import Tree
import argparse


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


def sh(commands):
    print '#!/bin/sh'
    print 'set -xeu'
    for i, subcommands in enumerate(commands):
        print "\n".join(subcommands)
        print '( set +x ; %s ) 2>/dev/null' % pbar(i+1, len(commands))
        print


def parallel(commands):
    print '#!/usr/bin/parallel --shebang --verbose'
    for i, subcommands in enumerate(commands):
        print " && ".join(subcommands + [pbar(i+1, len(commands))])


def make(commands):
    targets = ' '.join('d%s' % i for i in xrange(0, len(commands)))
    print '.PHONY: all %s' % targets
    print 'all: %s' % targets
    print
    for i, subcommands in enumerate(commands):
        print 'd%s:' % i
        for subcommand in subcommands:
            print '\t%s' % subcommand
        print '\t@%s' % pbar(i+1, len(commands))


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
    parser.add_argument('src', help='Source directory', metavar='SOURCE')
    parser.add_argument('dest', help='Destination directory', metavar='DESTINATION')
    args = parser.parse_args()

    tree = Tree(args.src, args.dest,
                {'quality': args.quality, 'gain': args.gain, 'delete': args.delete,
                 'maxrate': args.maxrate, 'maxbits': args.maxbits})
    printers[args.output](tree.commands())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from brutha.tree import Tree
import argparse


def sh(commands):
    print '#!/bin/sh'
    print 'set +xeu'
    print "\n\n".join(["\n".join(subcommands) for subcommands in commands])


def parallel(commands):
    print '#!/usr/bin/parallel --shebang --verbose'
    print "\n".join([" && ".join(subcommands) for subcommands in commands])


def makefile(commands):
    targets = ' '.join('d%s' % i for i in xrange(0, len(commands)))
    print '.PHONY: all %s' % targets
    print 'all: %s' % targets
    print
    for i, subcommands in enumerate(commands):
        print 'd%s:' % i
        for subcommand in subcommands:
            print '\t%s' % subcommand


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quality', default=8, type=int)
    parser.add_argument('-g', '--gain', action='store_true')
    parser.add_argument('-d', '--delete', action='store_true')
    parser.add_argument('-o', '--output', default='sh')
    parser.add_argument('-R', '--maxrate', type=int)
    parser.add_argument('-B', '--maxbits', type=int)
    parser.add_argument('src')
    parser.add_argument('dest')
    args = parser.parse_args()
    tree = Tree(args.src, args.dest,
                {'quality': args.quality, 'gain': args.gain, 'delete': args.delete,
                 'maxrate': args.maxrate, 'maxbits': args.maxbits})
    printers = {'sh': sh, 'parallel': parallel, 'makefile': makefile}
    printers[args.output](tree.commands())

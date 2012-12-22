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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quality', default=8, type=int)
    parser.add_argument('-g', '--gain', action='store_true')
    parser.add_argument('-d', '--delete', action='store_true')
    parser.add_argument('-o', '--output', default='sh')
    parser.add_argument('src')
    parser.add_argument('dest')
    args = parser.parse_args()
    tree = Tree(args.src, args.dest,
                {'quality': args.quality, 'gain': args.gain, 'delete': args.delete})
    printers = {'sh': sh, 'parallel': parallel}
    printers[args.output](tree.commands())

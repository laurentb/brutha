#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys

from brutha.tree import Tree
from brutha.util import uprint
from brutha.output import PRINTERS


def main():
    parser = argparse.ArgumentParser(
        description='Sync FLAC music files to Ogg Vorbis (or keep lossy as-is).')
    parser.add_argument('-q', '--quality', default=8, type=int,
                        help='Ogg Vorbis quality, -1 to 10, default 8')
    parser.add_argument('-g', '--gain', action='store_true',
                        help='Compute ReplayGain if missing')
    parser.add_argument('-d', '--delete', action='store_true',
                        help='Delete extraneous files in destination')
    parser.add_argument('-o', '--output', default='sh', choices=PRINTERS.keys(),
                        help='Command list type, default sh')
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
    outf = PRINTERS[args.output]
    outf(p, tree.commands(), args.echo)

if __name__ == '__main__':
    main()

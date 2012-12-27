#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
from StringIO import StringIO

from brutha.tree import Tree
from brutha.util import uprint, detect_cores, default_output
from brutha.output import PRINTERS, EXECUTORS


def main():
    cores = detect_cores()
    output = default_output(cores)

    parser = argparse.ArgumentParser(
        description='Sync FLAC music files to Ogg Vorbis (or keep lossy as-is).')
    parser.add_argument('-q', '--quality', default=8, type=int,
                        help='Ogg Vorbis quality, -1 to 10, default 8')
    parser.add_argument('-g', '--gain', action='store_true',
                        help='Compute ReplayGain if missing')
    parser.add_argument('-d', '--delete', action='store_true',
                        help='Delete extraneous files in destination')
    parser.add_argument('-o', '--output', default=output, choices=PRINTERS.keys(),
                        help='Command list type, default %s' % output)
    parser.add_argument('-R', '--maxrate', type=int,
                        help='Maximum sample rate allowed (e.g. 44100)', metavar='RATE')
    parser.add_argument('-B', '--maxbits', type=int,
                        help='Maximum bit depth allowed (e.g. 16)', metavar='BITS')
    parser.add_argument('-L', '--lossycheck', action='store_true',
                        help='Ignore lossy files with too high sample rate or bit depth')
    parser.add_argument('-e', '--echo', action='store_true',
                        help='Show started commands')
    parser.add_argument('-x', '--execute', action='store_true',
                        help='Execute the script instead of printing it')
    parser.add_argument('-j', '--jobs', type=int, default=cores,
                        help='Number of concurrent jobs, default %s' % cores)
    parser.add_argument('src', help='Source directory', metavar='SOURCE')
    parser.add_argument('dest', help='Destination directory', metavar='DESTINATION')
    args = parser.parse_args()

    tree = Tree(args.src, args.dest,
                {'quality': args.quality, 'gain': args.gain, 'delete': args.delete,
                 'maxrate': args.maxrate, 'maxbits': args.maxbits, 'lossycheck': args.lossycheck})
    if args.execute:
        s = StringIO()
        p = uprint(s)
    else:
        p = uprint(sys.stdout)
    outf = PRINTERS[args.output]
    outf(p, tree.commands(), args.echo, args.jobs)

    if args.execute:
        jobs = args.jobs if args.output in ('parallel', 'make') else 1
        print >>sys.stderr, 'Synchronizing %s to %s, using %s concurrent jobs.' % (args.src, args.dest, jobs)
        exef = EXECUTORS[args.output]
        sys.exit(exef(s, args.jobs))


if __name__ == '__main__':
    main()

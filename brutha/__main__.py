#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import argparse
import sys
from StringIO import StringIO

from .output import OUTPUTS
from .tree import Tree
from .util import default_output, detect_cores


def main():
    cores = detect_cores()
    output = default_output(cores)

    parser = argparse.ArgumentParser(
        description="Sync FLAC music files to Ogg Vorbis (or keep lossy as-is).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-q', '--quality', default=8, type=int,
                        help="Ogg Vorbis quality, -1 to 10")
    parser.add_argument('-g', '--gain', action='store_true',
                        help="Compute ReplayGain if missing")
    parser.add_argument('-d', '--delete', action='store_true',
                        help="Delete extraneous files in destination")
    parser.add_argument('-o', '--output', default=output, choices=OUTPUTS.keys(),
                        help="Command list type")
    parser.add_argument('-R', '--maxrate', type=int,
                        help="Maximum sample rate allowed (e.g. 44100)", metavar="RATE")
    parser.add_argument('-B', '--maxbits', type=int,
                        help="Maximum bit depth allowed (e.g. 16)", metavar="BITS")
    parser.add_argument('-L', '--lossycheck', action='store_true',
                        help="Ignore lossy files with too high sample rate or bit depth")
    parser.add_argument('-e', '--echo', action='store_true',
                        help="Show started commands")
    parser.add_argument('-x', '--execute', action='store_true',
                        help="Execute the script instead of printing it")
    parser.add_argument('-j', '--jobs', type=int, default=cores,
                        help="Number of concurrent jobs")
    parser.add_argument('src', help="Source directory", metavar='SOURCE')
    parser.add_argument('dest', help="Destination directory", metavar='DESTINATION')
    args = parser.parse_args()

    log = sys.stderr
    tree = Tree(args.src, args.dest,
                {'quality': args.quality, 'gain': args.gain, 'delete': args.delete,
                 'maxrate': args.maxrate, 'maxbits': args.maxbits,
                 'lossycheck': args.lossycheck},
                log)
    if args.execute:
        stream = StringIO()
    else:
        stream = sys.stdout
    jobs = args.jobs if args.output in ('parallel', 'make') else 1
    out = OUTPUTS[args.output](args.echo, jobs)
    out.write(tree.commands(), stream)

    if args.execute:
        print >>log, "Synchronizing %s to %s, using %s concurrent jobs." % (args.src, args.dest, jobs)
        sys.exit(out.run(stream))


if __name__ == '__main__':
    main()

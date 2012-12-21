#!/usr/bin/env python
# -*- coding: utf-8 -*-
from brutha.tree import Tree
import argparse


def printall(stuff):
    if isinstance(stuff, basestring):
        print stuff
    else:
        for thing in stuff:
            printall(thing)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('src')
    parser.add_argument('dest')
    args = parser.parse_args()
    d = Tree(args.src, args.dest)
    printall(d.commands())

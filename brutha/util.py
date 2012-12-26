# -*- coding: utf-8 -*-


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


def uprint(stream):
    def p(text='', end='\n'):
        stream.write(text + end)
    return p

# -*- coding: utf-8 -*-
import subprocess

from .util import require_executable


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

    bar = int(pct/10) * '#'
    return "echo '%s[%-10s] (%s%%)%s'" % (BRIGHT, bar, pct, NORMAL)


class Output(object):
    NAME = NotImplemented

    def __init__(self, echo=False, jobs=None):
        self.echo = echo
        self.jobs = jobs

    def write(self, commands, stream):
        raise NotImplementedError()

    def run(self, stream):
        raise NotImplementedError()


class Shebang(object):
    def run(self, stream):
        """
        Extracts the shebang (#!) line and runs it, with the script provided as stdin.
        This is known to work at least with bash and GNU parallel.
        """
        stream.seek(0)
        line = stream.readline()
        assert line.startswith('#!')
        shebang = line[2:].split()
        p = subprocess.Popen(shebang, shell=False, stdin=subprocess.PIPE)
        p.communicate(stream.getvalue().encode())
        return p.returncode


class Shell(Shebang, Output):
    NAME = 'sh'

    def write(self, commands, stream):
        print('#!%s' % require_executable('sh', ['bash', 'zsh', 'dash', 'sh']), file=stream)
        print('set -eu', file=stream)
        if self.echo:
            print('set -x', file=stream)
        for i, subcommands in enumerate(commands):
            print("\n".join(subcommands), file=stream)
            if self.echo:
                print('( set +x ; %s ) 2>/dev/null' % pbar(i+1, len(commands)), file=stream)
            else:
                print(pbar(i+1, len(commands)), file=stream)
            print(file=stream)


class Parallel(Shebang, Output):
    NAME = 'parallel'

    def write(self, commands, stream):
        verbose = ' --verbose' if self.echo else ''
        jobs = ' --jobs %s' % self.jobs if self.jobs else ''
        print('#!%s --shebang --eta%s%s -- -' % (require_executable('parallel'), jobs, verbose), file=stream)
        for i, subcommands in enumerate(commands):
            print(" && ".join(subcommands + [pbar(i+1, len(commands))]), file=stream)


class Make(Output):
    NAME = 'make'

    def _escape(self, line):
        return line.replace('$', '$$')

    def write(self, commands, stream):
        prefix = '' if self.echo else '@'
        targets = ' '.join('d%s' % i for i in range(0, len(commands)))
        print('.PHONY: all %s' % targets, file=stream)
        print('all: %s' % targets, file=stream)
        print(file=stream)
        for i, subcommands in enumerate(commands):
            print('d%s:' % i, file=stream)
            for subcommand in subcommands:
                print('\t%s%s' % (prefix, self._escape(subcommand)), file=stream)
            print('\t@%s' % pbar(i+1, len(commands)), file=stream)

    def run(self, stream):
        if self.jobs:
            addon = ['-j', str(self.jobs)]
        else:
            addon = []
        p = subprocess.Popen([require_executable('make', ['gmake', 'make']), '-f', '-'] + addon,
                             shell=False, stdin=subprocess.PIPE)
        p.communicate(stream.getvalue().encode())
        return p.returncode


OUTPUTS = dict((c.NAME, c) for c in (Shell, Parallel, Make))

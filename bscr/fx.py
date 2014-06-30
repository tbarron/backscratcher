#!/usr/bin/python
"""
commnd effects

The simplest use is to apply a command to a sequence of files. For example,

  fx -c "echo %" file1 file2 file3

will expand to

  echo file1
  echo file2
  echo file3

USAGE

 fx [-n] [-q] -c <command> {file1 file2 ... filen | -i low:high}
 fx [-n] [-q] -x -c <command>
 fx [-n] [-q] -e s/foo/bar/ file1 file2 ... filen

If -i is used to specify a range of numbers instead of a list of
files, the numbers will be substituted for the '%' in the command. If
-x is used, strings from stdin will be collected into bundles and the
bundles will be substituted for '%' in the command.

If the -e option is used, the s/// operation is applied to each
filename in the list and the files are renamed.

If -n is used, the commands generated are displayed but not run.

If -q is used, the commands are run without being displayed first.

OPTIONS

 -c <command>

Specify the command to be run.

 -e s/<old>/<new>/

Specify a substitute operation to be applied to a list of filenames.

 -i <low>:<high>

Specify a list of numbers to be substituted for '%' in a command string.

 -n

Just do a dryrun.

 -q

Be quiet -- don't echo commands before running them.

 -x

Bundle strings from stdin into groups that won't overrun the shell
command buffer and substitute the bundles for '%' in the command. This
is like xargs, except it facilitates putting the list from stdin in
the middle of the command rather than only being able to put it at the
end.

LICENSE

Copyright (C) 1995 - <the end of time>  Tom Barron
  tom.barron@comcast.net
  177 Crossroads Blvd
  Oak Ridge, TN  37830

This software is licensed under the CC-GNU GPL. For the full text of
the license, see http://creativecommons.org/licenses/GPL/2.0/

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import glob
import optparse
import os
import pdb
import re
import sys
import StringIO
import textwrap
import unittest


# ---------------------------------------------------------------------------
def main(argv=None):
    """
    Select the function to apply based on the command line options.
    """
    if argv is None:
        argv = sys.argv

    p = optparse.OptionParser()
    p.add_option('-c', '--command',
                 action='store', default='', dest='cmd', type='string',
                 help='command to apply to all arguments')
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under the debugger')
    p.add_option('-e', '--edit',
                 action='store', default='', dest='edit', type='string',
                 help='file rename expression applied to all arguments')
    p.add_option('-i', '--integer',
                 action='store', default='', dest='irange', type='string',
                 help='low:high -- generate range of numbers')
    p.add_option('-n', '--dryrun',
                 action='store_true', default=False, dest='dryrun',
                 help='dryrun or execute')
    p.add_option('-q', '--quiet',
                 action='store_true', default=False, dest='quiet',
                 help="don't echo commands, just run them")
    p.add_option('-x', '--xargs',
                 action='store_true', default=False, dest='xargs',
                 help='batch input from stdin into command lines like xargs')
    (o, a) = p.parse_args(argv)

    if o.debug:
        pdb.set_trace()

    Home = os.getenv('HOME')

    if o.edit != '':
        SubstRename(o, a[1:])
    elif o.irange != '':
        IterateCommand(o, a[1:])
    elif o.xargs:
        BatchCommand(o, a[1:])
    elif o.cmd != '':
        SubstCommand(o, a[1:])
    else:
        Usage()


# ---------------------------------------------------------------------------
def expand(cmd):
    """
    Expand environment variables and user notation in a command string.
    """
    return os.path.expandvars(os.path.expanduser(cmd))


# ---------------------------------------------------------------------------
def BatchCommand(options, arglist):
    """
    Bundle arguments into command lines similarly to xargs.

    Unlink xargs, this version allows for static values following the
    list of arguments on each command line.
    """
    for cmd in xargs_wrap(options.cmd, sys.stdin):
        psys(cmd, options)


# ---------------------------------------------------------------------------
def IterateCommand(options, arglist):
    """
    Run a command once for each of a sequence of numbers.

    Possible enhancements would be to handle low/high/step tuples, and
    to handle an arbitrary comma delimited list of values.
    """
    (low, high) = options.irange.split(':')
    for idx in range(int(low), int(high)):
        cmd = expand(re.sub('%', str(idx), options.cmd))
        psys(cmd, options)


# ---------------------------------------------------------------------------
def psys(cmd, options):
    """
    Handle a command subject to the dryrun and quiet members of options.

    !dryrun & !quiet: Display the command, then run it
    !dryrun & quiet: Run the command without displaying it
    dryrun & !quiet: Display the command without running it
    dryrun & quiet: Do nothing - no display, no run
    """
    # print("psys: cmd = '%s', dryrun = %s, quiet = %s"
    #       % (cmd, options.dryrun, options.quiet))
    if options.dryrun:
        print("would do '%s'" % cmd)
    elif options.quiet:
        # os.system(cmd)
        f = os.popen(cmd, 'r')
        sys.stdout.write(f.read())
        f.close()
    else:
        print(cmd)
        # os.system(cmd)
        f = os.popen(cmd, 'r')
        sys.stdout.write(f.read())
        f.close()


# ---------------------------------------------------------------------------
def SubstCommand(options, arglist):
    """
    Run the command for each filename in arglist.
    """
    for filename in arglist:
        cmd = expand(re.sub('%', filename, options.cmd))
        psys(cmd, options)


# ---------------------------------------------------------------------------
def SubstRename(options, arglist):
    """
    Create and run a rename command based on a s/old/new/ expression.
    """
    p = options.edit
    s = p.split(p[1])
    for filename in arglist:
        newname = re.sub(s[1], s[2], filename)
        print("rename %s %s" % (filename, newname))
        if not options.dryrun:
            os.rename(filename, newname)


# ---------------------------------------------------------------------------
def Usage():
    """
    Report program usage.
    """
    print
    print('  fx [-n] -c <command> <files> (% in the command becomes filename)')
    print('          -e s/old/new/ <files> (rename file old to new name)')
    print('          -i low:high <command> (% ranges from low to high-1)')
    print


# ---------------------------------------------------------------------------
def xargs_wrap(cmd, input):
    """
    Do xargs wrapping to cmd, distributing args from file input across
    command lines.
    """
    tcmd = cmd
    rval = []
    for line in input:
        l = line.strip()
        for item in l.split(" "):
            tcmd = expand(re.sub('%', item + ' %', tcmd))
            pending = True

            if 240 < len(tcmd):
                tcmd = re.sub(r'\s*%\s*', '', tcmd)
                rval.append(tcmd)
                pending = False
                tcmd = cmd
    if pending:
        tcmd = re.sub(r'\s*%\s*', '', tcmd)
        rval.append(tcmd)
    return(rval)

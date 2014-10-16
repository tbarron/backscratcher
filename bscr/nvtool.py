#!/usr/bin/python
"""
nvtool - environment manipulations
"""

import os
import pdb
import re
import sys
import tempfile
import util

from optparse import *


# ---------------------------------------------------------------------------
def main(args=None):
    """
    Command line entry point
    """
    if args is None:
        args = sys.argv
    util.dispatch("bscr.nvtool", "nv", args)


# ---------------------------------------------------------------------------
def nv_decap(argv):
    """decap - remove the head of a PATH type variable
    """
    x = argv[0].split(':')
    print(':'.join(x[1:]))


# ---------------------------------------------------------------------------
def nv_dedup(argv):
    """dedup - display the contents of a PATH variable without duplicates

    The earliest occurrence of each path is preserved and subsequent
    occurrences are removed.
    """
    p = OptionParser()
    p.add_option('-j', '--join',
                 action='store_true', default=True, dest='join',
                 help='colon separated format (default)')
    p.add_option('-s', '--show',
                 action='store_true', default=False, dest='show',
                 help='newline separated format')
    (o, a) = p.parse_args(argv)

    dup = []
    for item in a[0].split(':'):
        if item not in dup:
            dup.append(item)

    if o.show:
        for item in dup:
            print "   " + item
    else:
        print ':'.join(dup)


# ---------------------------------------------------------------------------
def nv_deped(argv):
    """deped - remove the foot (last entry) of a PATH type variable
    """
    x = argv[0].split(':')
    print(':'.join(x[:-1]))


# ---------------------------------------------------------------------------
def nv_stash(argv):
    """stash - write an env var contents in a format suitable for editing

    usage: nvtool stash VARNAME > filename

    With load, stash can be used to edit environment variables like $PATH.
    For example,

        $ nvtool stash PATH > mypath
        $ vi mypath
        $ export PATH=`nvtool load mypath`
    """
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    (o, a) = p.parse_args(argv)

    if o.debug:
        pdb.set_trace()

    varname = a[0]
    val = os.getenv(varname)
    if val is None:
        print "No value for $%s" % varname
    else:
        for v in val.split(":"):
            print v


# ---------------------------------------------------------------------------
def nv_load(argv):
    """load - read a file to set the content of a variable

    usage: export PATH=`nvtool load <filename>`

    With stash, load can be used to edit environment variables like $PATH.
    For example,

        $ nvtool stash PATH > mypath
        $ vi mypath
        $ export PATH=`nvtool load mypath`
    """
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    (o, a) = p.parse_args(argv)

    if o.debug:
        pdb.set_trace()

    fname = a[0]
    f = open(fname, 'r')
    result = ":".join([x.strip() for x in f.readlines()])
    f.close()
    print result


# ---------------------------------------------------------------------------
def nv_show(argv):
    """show - display the contents of a PATH variable in an easy to read format
    """
    for item in argv[0].split(':'):
        print "   " + item


# ---------------------------------------------------------------------------
def nv_remove(argv):
    """remove - remove entries that match the argument
    """
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    p.add_option('-j', '--join',
                 action='store_true', default=True, dest='join',
                 help='colon separated format (default)')
    p.add_option('-s', '--show',
                 action='store_true', default=False, dest='show',
                 help='newline separated format')
    (o, a) = p.parse_args(argv)

    if o.debug:
        pdb.set_trace()

    A = argv[1].split(':')
    result = [x for x in A if argv[0] not in x]
    if o.join:
        print(":".join(result))
    elif o.show:
        for item in result:
            print "   " + item

# ---------------------------------------------------------------------------
# xtoolframe.tf_launch("nv")

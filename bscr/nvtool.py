#!/usr/bin/python
"""
nvtool - environment manipulations
"""

import optparse
import os
import pdb
import re
import sys
import tempfile
import util

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
    pieces = argv[0].split(':')
    print(':'.join(pieces[1:]))

# ---------------------------------------------------------------------------
def nv_dedup(argv):
    """dedup - display the contents of a PATH variable without duplicates

    The earliest occurrence of each path is preserved and subsequent
    occurrences are removed.
    """
    prs = optparse.OptionParser()
    prs.add_option('-j', '--join',
                   action='store_true', default=True, dest='join',
                   help='colon separated format (default)')
    prs.add_option('-s', '--show',
                   action='store_true', default=False, dest='show',
                   help='newline separated format')
    (opts, args) = prs.parse_args(argv)

    dup = []
    for item in args[0].split(':'):
        if item not in dup:
            dup.append(item)

    if opts.show:
        for item in dup:
            print "   " + item
    else:
        print ':'.join(dup)


# ---------------------------------------------------------------------------
def nv_deped(argv):
    """deped - remove the foot (last entry) of a PATH type variable
    """
    pieces = argv[0].split(':')
    print(':'.join(pieces[:-1]))


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
    prs = optparse.OptionParser()
    prs.add_option('-d', '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    (opts, args) = prs.parse_args(argv)

    if opts.debug:
        pdb.set_trace()

    varname = args[0]
    val = os.getenv(varname)
    if val is None:
        print "No value for $%s" % varname
    else:
        for piece in val.split(":"):
            print piece


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
    prs = optparse.OptionParser()
    prs.add_option('-d', '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    (opts, args) = prs.parse_args(argv)

    if opts.debug:
        pdb.set_trace()

    fname = args[0]
    rbl = open(fname, 'r')
    result = ":".join([_.strip() for _ in rbl.readlines()])
    rbl.close()
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
    prs = optparse.OptionParser()
    prs.add_option('-d', '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    prs.add_option('-j', '--join',
                   action='store_true', default=True, dest='join',
                   help='colon separated format (default)')
    prs.add_option('-s', '--show',
                   action='store_true', default=False, dest='show',
                   help='newline separated format')
    (opts, _) = prs.parse_args(argv)

    if opts.debug:
        pdb.set_trace()

    pieces = argv[1].split(':')
    result = [_ for _ in pieces if argv[0] not in _]
    if opts.join:
        print(":".join(result))
    elif opts.show:
        for item in result:
            print "   " + item

# ---------------------------------------------------------------------------
# xtoolframe.tf_launch("nv")

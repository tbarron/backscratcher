#!/usr/bin/python
"""
nvtool - environment manipulations

A 'pathish' is a PATH-formatted environment variable. Examples include $PATH,
$MANPATH, $PYTHONPATH, etc.

Usage:    nvtool help [COMMAND]
          nvtool decap [--show] VAR
          nvtool dedup [--show] VAR
          nvtool deped [--show] VAR
          nvtool load FILE
          nvtool remove [--show] SEGMENT VAR
          nvtool show VAR

nvtool examples:

    nvtool help
        Display this list of command descriptions

    export PATH=`nvtool decap $PATH`
        Remove the first element of $PATH

    export PATH=`nvtool dedup $PATH`
        Remove duplicate elements of $PATH

    export PATH=`nvtool deped $PATH`
        Remove the last element of $PATH

    export PATH=`nvtool remove local $PATH`
        Remove items matching 'local' from $PATH

    export PATH=`nvtool load FILE`
        Set PATH from FILE, one element per line

    nvtool show $PATH [> FILE]
        Display the contents of $PATH, one element per line for legibility, or
        write them to a file in a format suitable for later use with
        'nvtool load ...'
"""
from docopt_dispatch import dispatch
import optparse
import os
import pdb
import sys
import util


# ---------------------------------------------------------------------------
def main(args=None):                                    # pragma: no coverage
    """
    Command line entry point
    """
    dispatch(__doc__)


# ---------------------------------------------------------------------------
@dispatch.on('help')
def nv_help(**kwa):
    """
    Show the help information from __doc__
    """
    pring = False
    for line in __doc__.split("\n"):
        if pring:
            print line
        if "examples:" in line:
            print line
            pring = True


# ---------------------------------------------------------------------------
@dispatch.on('decap', '--show', 'VAR')
def nv_decap_show(**kwa):
    """
    Remove the head of a PATH type variable. Output in show format.
    """
    pieces = kwa['VAR'].split(':')
    print('\n   '.join(pieces[1:]))


# -----------------------------------------------------------------------------
@dispatch.on('decap', 'VAR')
def nv_decap(**kwa):
    """
    Remove the head of a PATH type variable. Output in colon-separated format.
    """
    pieces = kwa['VAR'].split(':')
    print(':'.join(pieces[1:]))


# -----------------------------------------------------------------------------
@dispatch.on('dedup', '--show', 'VAR')
def nv_dedup_show(**kwa):
    """
    Remove duplicates from a pathish. Output is in human-readable, \n-separated
    format
    """
    dup = []
    for item in kwa['VAR'].split(':'):
        if item not in dup:
            dup.append(item)
    for item in dup:
        print("   {}".format(item))


# -----------------------------------------------------------------------------
@dispatch.on('dedup', 'VAR')
def nv_dedup(**kwa):
    """dedup - display the contents of a PATH variable without duplicates

    The earliest occurrence of each path is preserved and subsequent
    occurrences are removed.
    """
    dup = []
    for item in kwa['VAR'].split(':'):
        if item not in dup:
            dup.append(item)
    print(':'.join(dup))


# ---------------------------------------------------------------------------
@dispatch.on('deped', '--show', 'VAR')
def nv_deped_show(**kwa):
    """
    Remove the foot (last entry) of a PATHISH. Output in show format
    """
    pieces = kwa['VAR'].split(':')
    print('\n   '.join(pieces[:-1]))


# ---------------------------------------------------------------------------
@dispatch.on('deped', 'VAR')
def nv_deped(**kwa):
    """deped - remove the foot (last entry) of a PATH type variable
    """
    pieces = kwa['VAR'].split(':')
    print(':'.join(pieces[:-1]))


# ---------------------------------------------------------------------------
# def nv_stash(argv):
#     """stash - write an env var contents in a format suitable for editing
#
#     usage: nvtool stash VARNAME > filename
#
#     With load, stash can be used to edit environment variables like $PATH.
#     For example,
#
#         $ nvtool stash PATH > mypath
#         $ vi mypath
#         $ export PATH=`nvtool load mypath`
#     """
#     prs = optparse.OptionParser()
#     prs.add_option('-d', '--debug',
#                    action='store_true', default=False, dest='debug',
#                    help='start the debugger')
#     (opts, args) = prs.parse_args(argv)
#
#     if opts.debug:               # pragma: no coverage
#         pdb.set_trace()
#
#     varname = args[0]
#     val = os.getenv(varname)
#     if val is None:
#         print "No value for $%s" % varname
#     else:
#         for piece in val.split(":"):
#             print piece


# ---------------------------------------------------------------------------
@dispatch.on('load', 'FILE')
def nv_load(**kwa):
    """load - read a file to set the content of a variable

    usage: export PATH=`nvtool load <filename>`

    With stash, load can be used to edit environment variables like $PATH.
    For example,

        $ nvtool stash PATH > mypath
        $ vi mypath
        $ export PATH=`nvtool load mypath`
    """
    with open(kwa['FILE'], 'r') as rbl:
        lines = rbl.readlines()
    result = ":".join([_.strip() for _ in lines])
    print result


# ---------------------------------------------------------------------------
@dispatch.on('show', 'VAR')
def nv_show(**kwa):
    """show - display the contents of a PATH variable in an easy to read format
    """
    for item in kwa['VAR'].split(':'):
        print "   " + item


# ---------------------------------------------------------------------------
@dispatch.on('remove', '--show', 'SEGMENT', 'VAR')
def nv_remove_show(**kwa):
    """
    Remove entries that match the argument. Output in show format.
    """
    pieces = kwa['VAR'].split(':')
    result = [_ for _ in pieces if kwa['SEGMENT'] not in _]
    for item in result:
        print "    " + item

# ---------------------------------------------------------------------------
@dispatch.on('remove', 'SEGMENT', 'VAR')
def nv_remove(**kwa):
    """
    Remove entries that match the argument. Output in join format.
    """
    pieces = kwa['VAR'].split(':')
    result = [_ for _ in pieces if kwa['SEGMENT'] not in _]
    print(":".join(result))


# ---------------------------------------------------------------------------
# xtoolframe.tf_launch("nv")

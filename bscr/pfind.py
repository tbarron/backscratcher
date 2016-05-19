#!/usr/bin/env python
"""
Replacement for find(1), like ack(1) for grep(1)
"""
import fnmatch
import os
import pdb
import sys


import docopt

# -----------------------------------------------------------------------------
def main(args):
    """
    pfind: walk a directory tree and find files

    Usage:
        pfind [options] [<dir> ...]

    Options:
        -d, --debug                  use the debugger
        -x <strs>, --exclude <strs>  skip paths containing any of <strs>
        -n, <name>, --name <name>    report files matching <name>
        -v, --verbose                noisy output

    If no path is given, '.' is assumed.

    The argument for the -x/--exclude option can be a comma separated list of
    string expressions. If any one of them matches a hit, it will be
    suppressed.
    """
    opts = docopt.docopt(main.__doc__, args)
    if opts['--debug']:
        pdb.set_trace()

    if opts['--verbose']:
        print(opts)

    match_str = opts['--name'] or '*'
    if opts['--exclude']:
        excl = opts['--exclude'].split(',')
    else:
        excl = []

    hitlist = []
    paths = opts['<dir>'] or ['.']
    for path in paths:
        hitlist.extend(get_hitlist(path, opts))
    for hit in hitlist:
        print hit

# -----------------------------------------------------------------------------
def get_hitlist(path=None, opts=None):
    """
    Walk *path* looking for filepaths that match *match* while excluding those
    that contain an *exclude* expression
    """
    path = path or '.'
    match = opts['--name'] or '*'
    if opts['--exclude']:
        exclude = opts['--exclude'].split(',')
    else:
        exclude = []

    rval = []
    for root, dirs, files in os.walk(path):
        hits = [_ for _ in dirs + files if fnmatch.fnmatch(_, match)]
        for hit in hits:
            hitpath = os.path.join(root, hit)
            if all([_ not in hitpath for _ in exclude]):
                rval.append(hitpath)
    return rval

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv[1:])

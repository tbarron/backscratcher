#!/usr/bin/env python
"""
Replacement for find(1), like ack(1) for grep(1)
"""
import fnmatch
import os
import pdb
import sys
import time

import docopt

# -----------------------------------------------------------------------------
def main(args=None):
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

    hitlist = []
    paths = opts['<dir>'] or ['.']
    for path in paths:
        hitlist.extend(get_hitlist(path, opts))
    for hit in hitlist:
        print hit

# ----------------------------------------------------------------------------
def digest_opts(opts):
    """
    Map options from the command line into a configuration structure for the
    rest of the program
    """
    def safe_del(dct, key):
        if key in dct:
            del dct[key]

    rval = {}

    rval['paths'] = opts.get('<dir>', ['.']) or ['.']
    safe_del(opts, '<dir>')

    excl = opts.get('--exclude', None)
    rval['exclude'] = [] if excl is None else [_.strip()
                                               for _ in excl.split(',')]
    safe_del(opts, '--exclude')

    if opts.get('--older', None):
        rval['older'] = parse_time(opts['--older'])
    else:
        rval['older'] = False
    safe_del(opts, '--older')

    if opts.get('--newer', None):
        rval['newer'] = parse_time(opts['--newer'])
    else:
        rval['newer'] = False
    safe_del(opts, '--newer')

    rval['verbose'] = opts.get('--verbose', False)
    safe_del(opts, '--verbose')

    for key in opts:
        nkey = key.replace('-', '')
        rval[nkey] = opts[key]

    return rval

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
def parse_time(dtstr):
    """
    Return an epoch time. If *dtstr* matches a path, return the mtime of the
    file or directory. Otherwise, treat *dtstr* as a date/time specification
    and apply time.strptime().
    """
    if os.path.exists(dtstr):
        pinfo = os.stat(dtstr)
        rval = pinfo.st_mtime
    else:
        try:
            _ = parse_time.fmt_l
        except AttributeError:
            parse_time.fmt_l = ['%Y.%m%d',
                                '%Y.%m%d %H:%M:%S',
                                '%Y.%m%d.%H%M%S',
                                'failure']

        for fmt in parse_time.fmt_l:
            try:
                tup = time.strptime(dtstr, fmt)
                break
            except ValueError as err:
                if fmt == 'failure':
                    msg = "time data {0} does not match any of the formats"
                    raise ValueError(msg.format(dtstr))
                else:
                    pass
        rval = time.mktime(tup)
    return rval

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv[1:])

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
        -N <name>, --name <name>     report files matching <name>
        -o <date>, --older <date>    report files older than <date>
        -n <date>, --newer <date>    report files newer than <date>
        -v, --verbose                noisy output

    If no <dir> path is given, '.' is assumed.

    The argument for the -x/--exclude option can be a comma separated list of
    string expressions. If any one of them matches a hit, it will be
    suppressed.
    """
    opts = docopt.docopt(main.__doc__, args)
    if opts['--debug']:
        pdb.set_trace()

    hitlist = get_hitlist(opts)
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
def get_hitlist(opts=None):
    """
    Walk *path* looking for filepaths that match *match* while excluding those
    that contain an *exclude* expression
    """
    dgst = digest_opts(opts)
    if not isinstance(dgst['paths'], list):
        sys.exit('programming error: paths must be a list')
    match = dgst.get('name', '*')

    rval = []
    for path in dgst['paths']:
        for root, dirs, files in os.walk(path):
            hits = [_ for _ in dirs + files if fnmatch.fnmatch(_, match)]
            for hit in hits:
                hitpath = os.path.join(root, hit)
                if keep(hitpath, dgst):
                    rval.append(hitpath)
    return rval


# -----------------------------------------------------------------------------
def keep(path, opts):
    """
    Decide whether to keep path based on opts
    """
    exclude = opts.get('exclude', [])
    if any([_ in path for _ in exclude]):
        return False
    stinfo = os.stat(path)
    if opts.get('older', False) and opts['older'] < stinfo.st_mtime:
        return False
    if opts.get('newer', False) and stinfo.st_mtime < opts['newer']:
        return False
    return True


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
        if not hasattr(parse_time, 'fmt_l'):
            parse_time.fmt_l = ['%Y.%m%d',
                                '%Y.%m%d %Z',
                                '%Y.%m%d %H:%M:%S',
                                '%Y.%m%d %H:%M:%S %Z',
                                '%Y.%m%d.%H%M%S',
                                '%Y.%m%d.%H%M%S %Z',
                                'failure']

        for fmt in parse_time.fmt_l:
            try:
                tup = time.strptime(dtstr, fmt)
                break
            except ValueError:
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

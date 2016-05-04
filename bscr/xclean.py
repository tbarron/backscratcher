"""
Clean stuff up
"""
import os
import pdb
import re
import sys
import util as U


# -----------------------------------------------------------------------------
def main(args=None):
    """
    Command line entrypoint
    """
    if args is None:
        args = sys.argv

    cmdl = U.cmdline([{'opts': ['-n', '--dry-run'],
                       'action': 'store_true',
                       'default': False,
                       'dest': 'dryrun',
                       'help': 'just report'},
                      {'opts': ['-p', '--pattern'],
                       'action': 'store',
                       'default': None,
                       'dest': 'pattern',
                       'help': 'file matching regexp'},
                      {'opts': ['-r', '--recursive'],
                       'action': 'store_true',
                       'default': False,
                       'dest': 'recursive',
                       'help': 'whether to descend directories'}
                      ],
                     usage=usage())
    (opts, args) = cmdl.parse(args)
    if 0 == len(args[1:]):
        cleanup('.', opts.dryrun, opts.pattern, opts.recursive)
    else:
        for directory in args[1:]:
            cleanup(directory, opts.dryrun, opts.pattern, opts.recursive)


# -----------------------------------------------------------------------------
def cleanup(directory, dryrun=False, pattern=None, recursive=False):
    """
    Payload routine
    """
    flist = find_files(directory, pattern, recursive)
    if dryrun:
        print("Without --dryrun, would remove:")
        for fname in flist:
            print("   %s" % fname)
    else:
        for fname in flist:
            print("   removing %s" % fname)
            os.unlink(fname)


# -----------------------------------------------------------------------------
def find_files(directory, pattern=None, recursive=False):
    """
    Helper for finding files
    """
    if pattern is None:
        pattern = '.*~'
    rval = []
    if recursive:
        for root, _, flist in os.walk(directory):
            fpath = [os.path.join(root, f) for f in flist if re.match(pattern, f)]
            rval.extend(fpath)
    else:
        rval = [os.path.join(directory, _) for _ in os.listdir(directory)
                if re.match(pattern, _)]

    return rval


# -----------------------------------------------------------------------------
def usage():
    """
    Usage
    """
    return("\n    xclean - remove files whose names match a regexp")

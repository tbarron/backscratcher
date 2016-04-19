"""
Error descriptions
"""
import errno
import optparse
import os
import pdb
import sys


# -----------------------------------------------------------------------------
def main(args=None):
    """
    CLEP
    """
    if args is None:
        args = sys.argv

    prs = optparse.OptionParser(usage=usage())
    prs.add_option('-a', '--all', dest='all',
                   action='store_true', default=False,
                   help='list all errno values')
    prs.add_option('-d', '--debug', dest='debug',
                   action='store_true', default=False,
                   help='run the debugger')
    (opts, argl) = prs.parse_args(args)

    if opts.debug:
        pdb.set_trace()

    if opts.all:
        for errn in errno.errorcode.keys():
            print etranslate(errn)
    for errval in argl[1:]:
        print etranslate(errval)


# -----------------------------------------------------------------------------
def etranslate(errval):
    """
    Get all the informatio about an error and format it for display
    """
    rval = ''
    fmt = "%5d  %-15s  %s"
    if isinstance(errval, int):
        nval = errval
        sval = errno.errorcode[nval]
    elif errval.isdigit():
        nval = int(errval)
        sval = errno.errorcode[nval]
    elif errval in dir(errno):
        nval = getattr(errno, errval)
        sval = errval

    rval = fmt % (nval, sval, os.strerror(nval))
    return rval


# -----------------------------------------------------------------------------
def usage():
    """
    usage message
    """
    return("""perrno {-a|--all|number ...|errname ...}

    report errno numeric and string values""")

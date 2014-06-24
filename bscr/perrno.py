import errno
import optparse
import os
import pdb

# -----------------------------------------------------------------------------
def main(args):
    p = optparse.OptionParser()
    p.add_option('-a', '--all', dest='all',
                 action='store_true', default=False,
                 help='list all errno values')
    p.add_option('-d', '--debug', dest='debug',
                 action='store_true', default=False,
                 help='run the debugger')
    p.add_option('-f', '--format', type='string', dest='format',
                 action='store', default='%Y.%m%d %H:%M:%S',
                 help='date format (see strftime(3))')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    if o.all:
        for errn in errno.errorcode.keys():
            print etranslate(errn)
    for errval in a[1:]:
        print etranslate(errval)

# -----------------------------------------------------------------------------
def etranslate(errval):
    rval = ''
    fmt = "%5d  %-15s  %s"
    if type(errval) == int:
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

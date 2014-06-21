import optparse
import os
import re
import sys

# -----------------------------------------------------------------------------
def main(args=None):

    if args is None:
        args = sys.argv
        
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under the debugger')
    p.add_option('-n', '--dry-run',
                 action='store_true', default=False, dest='dryrun',
                 help='just report')
    p.add_option('-r', '--recursive',
                 action='store_true', default=False, dest='recursive',
                 help='whether to descend directories')
    (o, a) = p.parse_args(args)

    if 0 == len(a):
        cleanup('.', o.dryrun)
    else:
        for dir in a:
            cleanup(dir, o.dryrun)

# -----------------------------------------------------------------------------
def cleanup(dir, dryrun=False):
    flist = find_files(dir, o.recursive)
    if dryrun:
        print("Without --dryrun, would remove:")
        for fname in flist:
            print("   %s" % fname)
    else:
        for fname in flist:
            print("   removing %s" % fname)
            os.unlink(fname)

# -----------------------------------------------------------------------------
def find_files(dir, recursive=False):
    rval = []
    if recursive:
        for root, dlist, flist in os.walk(dir):
            fl = [os.path.join(root, f) for f in flist if re.match('.*~', f)]
            rval.extend(fl)
    else:
        rval = [os.path.join(dir, f) for f in os.listdir(dir)
                if re.match('.*~', f)]

    return rval

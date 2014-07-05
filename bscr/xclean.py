import optparse
import os
import pdb
import re
import sys

# -----------------------------------------------------------------------------
def main(args=None):

    if args is None:
        args = sys.argv

    p = optparse.OptionParser(usage=usage())
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under the debugger')
    p.add_option('-n', '--dry-run',
                 action='store_true', default=False, dest='dryrun',
                 help='just report')
    p.add_option('-p', '--pattern',
                 action='store', default=None, dest='pattern',
                 help='file matching regexp')
    p.add_option('-r', '--recursive',
                 action='store_true', default=False, dest='recursive',
                 help='whether to descend directories')
    (o, a) = p.parse_args(args)

    if 0 == len(a[1:]):
        cleanup('.', o.dryrun, o.pattern, o.recursive)
    else:
        for dir in a[1:]:
            cleanup(dir, o.dryrun, o.pattern, o.recursive)

# -----------------------------------------------------------------------------
def cleanup(dir, dryrun=False, pattern=None, recursive=False):
    flist = find_files(dir, pattern, recursive)
    if dryrun:
        print("Without --dryrun, would remove:")
        for fname in flist:
            print("   %s" % fname)
    else:
        for fname in flist:
            print("   removing %s" % fname)
            os.unlink(fname)

# -----------------------------------------------------------------------------
def find_files(dir, pattern=None, recursive=False):
    if pattern is None:
        pattern = '.*~'
    rval = []
    if recursive:
        for root, dlist, flist in os.walk(dir):
            fl = [os.path.join(root, f) for f in flist if re.match(pattern, f)]
            rval.extend(fl)
    else:
        rval = [os.path.join(dir, f) for f in os.listdir(dir)
                if re.match(pattern, f)]

    return rval

# -----------------------------------------------------------------------------
def usage():
    return("\n    xclean - remove files whose names match a regexp")

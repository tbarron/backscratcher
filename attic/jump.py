#!/bin/env python
"""
Consider replacing call to find(1) with the recipe outlined at
http://code.activestate.com/recipes/577027-find-file-in-subdirectory/:

    def findInSubdirectory(filename, subdirectory=''):
        if subdirectory:
            path = subdirectory
        else:
            path = os.getcwd()
        for root, dirs, names in os.walk(path):
            if filename in names:
                return os.path.join(root, filename)
        raise 'File not found'

"""
import optparse
import os
import pdb
import sys
import toolframe


# ---------------------------------------------------------------------------
def main(argv):
    p = optparse.OptionParser()
    p.add_option('-a', '--all',
                 action='store_true', default=False, dest='all',
                 help='show all hits')
    p.add_option('-D', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='debug')
    p.add_option('-i', '--into',
                 action='store', default=None, dest='tdir',
                 help='jump to dir TDIR')
    p.add_option('-r', '--root',
                 action='store', default='.', dest='root',
                 help='where to start looking')
    p.add_option('-t', '--to',
                 action='store', default=None, dest='tfile',
                 help='jump to dir containing TFILE')
    p.add_option('-w', '--which',
                 action='store', default=0, dest='which', type='int',
                 help='select from the full list of hits')
    (o, a) = p.parse_args(argv)

    if o.debug:
        pdb.set_trace()

    if o.tfile is not None:
        target = o.tfile
    elif o.tdir is not None:
        target = o.tdir
    else:
        raise StandardError("One of -t/--to or -i/--into is required.")

    f = os.popen('find %s -name %s 2>/dev/null' % (o.root, target))
    l = f.readlines()
    f.close()
    if len(l) < 1:
        raise StandardError("target %s not found in the specified directory"
                            % target)

    l.sort()
    if o.all:
        count = 0
        for item in l:
            print "%d: %s" % (count, item)
            count += 1
    elif o.tfile is not None:
        print(os.path.dirname(l[o.which]))
    elif o.tdir is not None:
        print(l[o.which])

# ---------------------------------------------------------------------------
toolframe.ez_launch(__name__, main)

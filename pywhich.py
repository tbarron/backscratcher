#!/usr/bin/env python

from optparse import *
import os
import pdb
import re
import sys
import toolframe

# ---------------------------------------------------------------------------
def main(args):
    p = OptionParser()
    p.add_option('-a', '--all',
                 action='store_true', default=False, dest='all',
                 help='show all hits, not just the first')
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under debugger')
    (o, a) = p.parse_args(args)

    if o.debug: pdb.set_trace()
    for looking_for in a[1:]:
        lfstem = re.sub('\.py$', '', looking_for)
        indent = '\n'
        for dname in sys.path:
            libname = dname + '/' + lfstem + '.py'
            if os.path.exists(libname):
                print indent + libname
                indent = '  '
                if not o.all:
                    break
    print('')
    
# ---------------------------------------------------------------------------
toolframe.ez_launch(main)

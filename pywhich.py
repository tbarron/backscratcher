#!/usr/bin/env python
"""
pywhich - Which python library will import load?

Given a list of python libraries, report which will be loaded by
an import statement based on sys.path (which is influenced by
$PYTHONPATH).

For example, on my Mac,

    $ pywhich optparse

reports

    /Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/optparse.py

OPTIONS
    -a/--all   Report all hits, not just the first one

    -d/--debug Run under the python debugger

LICENSE
    Copyright (C) 2012 - <the end of time>  Tom Barron
        tom.barron@comcast.net
        177 Crossroads Blvd
        Oak Ridge, TN  37830

    This software is licensed under the CC-GNU GPL. For the full text of
    the license, see http://creativecommons.org/licenses/GPL/2.0/

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
"""
__author__ = "Tom Barron <tom.barron@comcast.net>"
__date__ = "2012.1020"
__version__ = "$Revision: $"
__credits__ = """Guido van Rossum, for my favorite programming language.
The author of the Unix command which(1), for the inspiration.
"""

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

    if o.debug:
        pdb.set_trace()
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

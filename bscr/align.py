#!/usr/bin/python
"""
align

Take as input a file of partially formatted columns and align them
neatly in columns of minimal width.

Example:
    $ cal | align
    November  2013
    Su        Mo    Tu  We  Th  Fr  Sa
           1     2
           3     4   5   6   7   8   9
          10    11  12  13  14  15  16
          17    18  19  20  21  22  23
          24    25  26  27  28  29  30


Note that numbers are right-aligned while words are left-aligned.

Copyright (C) 1995 - <the end of time>  Tom Barron
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
import optparse
import pdb
import re
import sys


# ---------------------------------------------------------------------------
def main(A=None):
    """
    Program entry point
    """
    if A is None:
        A = sys.argv
    p = optparse.OptionParser(usage=usage())
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under the debugger')
    (o, a) = p.parse_args(A)

    if o.debug:
        pdb.set_trace()

    if 1 < len(A):
        input = open(A[1], 'r')
    else:
        input = sys.stdin
    align(input)


# ---------------------------------------------------------------------------
def align(input):
    lines = [l.strip() for l in input.readlines()]
    width = []
    for l in lines:
        f = l.split()
        w = [len(f) for f in l.split()]
        for idx in range(0, min(len(w), len(width))):
            width[idx] = max(w[idx], width[idx])
        if len(width) < len(w):
            width.extend(w[len(width):])

    for l in lines:
        f = l.split()
        oline = ''
        for i in range(0, len(f)):
            if re.search(r'\d+', f[i]):
                fmt = '%%%ds  ' % width[i]
            else:
                fmt = '%%-%ds  ' % width[i]
            oline = oline + fmt % f[i]
        print oline


# ---------------------------------------------------------------------------
def usage():
    return """align

    Align columns from input."""

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
import re
import sys
import util as U


# ---------------------------------------------------------------------------
def main(argl=None):
    """
    Program entry point
    """
    if argl is None:
        argl = sys.argv
    cmd = U.cmdline([], usage=usage())
    (_, args) = cmd.parse(argl)

    if 1 < len(args):
        src = open(args[1], 'r')
    else:
        src = sys.stdin
    align(src)


# ---------------------------------------------------------------------------
def align(src):
    """
    Payload routine
    """
    lines = [l.strip() for l in src.readlines()]
    max_width = []
    for line in lines:
        # flds = line.split()
        cur_width = [len(_) for _ in line.split()]
        for idx in range(0, min(len(cur_width), len(max_width))):
            max_width[idx] = max(cur_width[idx], max_width[idx])
        if len(max_width) < len(cur_width):
            max_width.extend(cur_width[len(max_width):])

    for line in lines:
        flds = line.split()
        oline = ''
        for idx in range(0, len(flds)):
            if re.search(r'\d+', flds[idx]):
                fmt = '%%%ds  ' % max_width[idx]
            else:
                fmt = '%%-%ds  ' % max_width[idx]
            oline = oline + fmt % flds[idx]
        print oline


# ---------------------------------------------------------------------------
def usage():
    """
    Report usage
    """
    return """align

    Align columns from input."""

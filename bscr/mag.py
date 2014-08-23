#!/usr/bin/python
"""
Report the magnitude of large numbers.

SYNOPSIS

   mag [-b] <number>

EXAMPLES
   $ mag 17
   17 = 17.00 b

   $ mag -b 72346
   72346 = 70.65 Kib

   $ mag 23482045
   23482045 = 23.48 Mb

   $ mag 2348291384 -b
   2348291384 = 2.19 Gib

Copyright (C) 2010 - <the end of time>  Tom Barron
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
import sys
import toolframe
import unittest


# ---------------------------------------------------------------------------
def main(argv=None, testing=False):
    """
    CLEP
    """
    if argv is None:
        argv = sys.argv

    p = optparse.OptionParser(usage=usage())
    # define options here
    p.add_option('-b', '--binary',
                 action='store_true', default=False, dest='binary',
                 help='div=1024 rather than 1000')
    (o, a) = p.parse_args(argv)

    if o.binary:
        divisor = 1024
        units = ['b', 'Kib', 'Mib', 'Gib', 'Tib', 'Pib', 'Eib', 'Zib', 'Yib']
    else:
        divisor = 1000
        units = ['b', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb']

    units.reverse()

    if len(a) < 2:
        rval = usage()
    else:
        val = float(a[1])
        u = units.pop()
        while divisor <= val:
            val /= divisor
            u = units.pop()

        rval = "%s = %3.2f %s" % (a[1], val, u)

    if testing:
        return(rval)
    else:
        print rval


# ---------------------------------------------------------------------------
def usage():
    """
    usage
    """
    return """mag [-b] <number>

    Report the order of magnitude of <number>
    With -b, use a divisor of 1024. Otherwise, use 1000."""

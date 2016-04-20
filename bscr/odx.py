#!/usr/bin/python
"""
odx

Take as input a number. It can be hex (prefixed with '0x'), octal
(prefixed with '0'), or decimal (no prefix). The response will show
the same value in all three formats.

EXAMPLES

   $ odx 017     # (octal)
   017 -> 15 / 0xf / 017

   $ odx 95      # (decimal)
   95 -> 95 / 0x5f / 0137

   $ odx 0x33    # (hexadecimal)
   0x33 -> 51 / 0x33 / 063

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
import sys


# -----------------------------------------------------------------------------
def main(args=None):
    """
    Where the action starts
    """
    if args is None:
        args = sys.argv
    prs = optparse.OptionParser(usage=usage())
    prs.add_option('-d', '--debug',
                   action='store_true', default=False, dest='debug',
                   help='run under debugger')
    (opts, argl) = prs.parse_args(args)

    if opts.debug:
        pdb.set_trace()
    print argl
    for aval in argl[1:]:
        result = odx(aval)
        print(result)


# -----------------------------------------------------------------------------
def odx(org):
    """
    Figure out the format of the input and compute the value
    """
    if org.startswith("0x"):
        val = int(org, 16)
    elif org.startswith("0"):
        val = int(org, 8)
    else:
        val = int(org)
    return "%s -> 0%o / %d / 0x%x" % (org, val, val, val)


# -----------------------------------------------------------------------------
def usage():
    """
    usage
    """
    return """odx {0<octal-value>|<decimal-value>|0x<hex-value>} ...

    report each argument in octal, decimal, and hex format"""

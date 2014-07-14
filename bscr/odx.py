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
#import toolframe


# -----------------------------------------------------------------------------
def main(args):
    p = optparse.OptionParser(usage=usage())
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under debugger')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()
    print a
    for str in a[1:]:
        result = odx(str)
        print(result)

# -----------------------------------------------------------------------------
def odx(str):
    if str.startswith("0x"):
        val = int(str, 16)
    elif str.startswith("0"):
        val = int(str, 8)
    else:
        val = int(str)
    return "%s -> 0%o / %d / 0x%x" % (str, val, val, val)

# -----------------------------------------------------------------------------
def usage():
    return """odx {0<octal-value>|<decimal-value>|0x<hex-value>} ...

    report each argument in octal, decimal, and hex format"""

# -----------------------------------------------------------------------------
#toolframe.ez_launch(__name__, main)

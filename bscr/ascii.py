#!/usr/bin/python
"""
ascii - Display ASCII collating sequence.

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
import sys
import util as U


# ---------------------------------------------------------------------------
def main(argv=None):
    """
    Entry point for ascii(1) command.
    """
    if argv is None:
        argv = sys.argv

    cmd = U.cmdline([], usage=usage())
    (opts, args) = cmd.parse(argv)

    asc = ['NUL', 'SOH', 'STX', 'ETX', 'EOT', 'ENQ', 'ACK', 'BEL', 'BS',
           'TAB', 'LF', 'VT', 'FF', 'CR', 'SO', 'SI', 'DLE', 'DC1', 'DC2',
           'DC3', 'DC4', 'NAK', 'SYN', 'ETB', 'CAN', 'EM', 'SUB', 'ESC',
           'FS', 'GS', 'RS', 'US', 'SPC']

    for i in range(33):
        sys.stdout.write('0x%02x %-3s ' % (i, asc[i]))
        if (i+1) % 8 == 0:
            sys.stdout.write('\n')

    for i in range(33, 127):
        sys.stdout.write('0x%02x %-3c ' % (i, i))
        if (i+1) % 8 == 0:
            sys.stdout.write('\n')

    sys.stdout.write("\n")


# ---------------------------------------------------------------------------
def usage():
    """
    Report usage
    """
    return """ascii

    Display ASCII collating sequence."""

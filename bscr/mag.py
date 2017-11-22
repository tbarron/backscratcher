#!/usr/bin/python
"""
Report the magnitude of large numbers.

Usage:
    mag [-d] [-b] NUMBER

Options:
    -b          use radix 1024 rather than 1000
    -d          use the debugger

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
import docopt
import pdb
import sys


# ---------------------------------------------------------------------------
def main(argv=None, testing=False):
    """
    Entry point
    """
    argv = argv or sys.argv
    opts = docopt.docopt(__doc__, argv)
    if opts['-d']:
        pdb.set_trace()

    if opts['-b']:
        divisor = 1024
        units = ['b', 'Kib', 'Mib', 'Gib', 'Tib', 'Pib', 'Eib', 'Zib', 'Yib']
    else:
        divisor = 1000
        units = ['b', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb']

    units.reverse()

    if len(argv) < 1:
        rval = usage()

    try:
        val = float(opts['NUMBER'])
        unit = units.pop()
        while divisor <= val:
            val /= divisor
            unit = units.pop()
        rval = "{} = {:3.2f} {}".format(opts['NUMBER'], val, unit)
    except ValueError:
        _ = docopt.docopt(__doc__, ["-x"])        # noqa: ignore=F841

    if testing:
        return(rval)
    else:
        print(rval)


# ---------------------------------------------------------------------------
def usage():
    """
    usage
    """
    return """mag [-b] <number>

    Report the order of magnitude of <number>
    With -b, use a divisor of 1024. Otherwise, use 1000."""

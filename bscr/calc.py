#!/usr/bin/python
"""
A simple command line calculator in Python.

Whatever you type at the prompt, calc will attempt to evaluate using
the Python interpreter.

Type 'sys.exit()' or hit ^C or ^D to exit.


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
    Command line entry point
    """
    if argv is None:
        argv = sys.argv

    cmd = U.cmdline([])
    (_, _) = cmd.parse(argv)

    try:
        results = []
        while True:
            expr = raw_input("> ")
            results.append(eval(expr))
            if isinstance(results[-1], int):
                print("r[%d] = %d" % (len(results)-1, results[-1]))
            elif isinstance(results[-1], float):
                print("r[%d] = %f" % (len(results)-1, results[-1]))
            elif isinstance(results[-1], str):
                print("r[%d] = %s" % (len(results)-1, results[-1]))
            else:
                print("r[%d] = %s" % (len(results)-1, str(results[-1])))
    except EOFError:
        print ''
        sys.exit(0)

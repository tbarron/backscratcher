#!/usr/bin/python
'''
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
'''

import getopt
import pexpect
import sys
import toolframe
import unittest

from optparse import *


# ---------------------------------------------------------------------------
def main(argv=None):
    if argv is None:
        argv = sys.argv

    p = OptionParser()
    # define options here
    # p.add_option('-s', '--long',
    #              action='', default='',
    #              dest='', type='',
    #              help='')
    (o, a) = p.parse_args(argv)

    try:
        r = []
        while True:
            expr = raw_input("> ")
            r.append(eval(expr))
            if type(r[-1]) == int:
                print("r[%d] = %d" % (len(r)-1, r[-1]))
            elif type(r[-1]) == float:
                print("r[%d] = %f" % (len(r)-1, r[-1]))
            elif type(r[-1]) == str:
                print("r[%d] = %s" % (len(r)-1, r[-1]))
            else:
                print("r[%d] = %s" % (len(r)-1, str(r[-1])))
    except EOFError:
        print ''
        sys.exit(0)


# ---------------------------------------------------------------------------
class CalcTest(unittest.TestCase):
    def test_example(self):
        S = pexpect.spawn("./calc")
        # S.logfile = sys.stdout
        S.expect("> ")

        S.sendline("7 + 12")
        S.expect("> ")

        assert("19" in S.before)

        S.sendline("7.988 + 28.576")
        S.expect("> ")

        assert("36.564000" in S.before)

        S.sendline("\"zap\" * 2")
        S.expect("> ")

        assert("zapzap" in S.before)

        S.sendline("exit()")
        S.expect(pexpect.EOF)
        S.close()

# ---------------------------------------------------------------------------
toolframe.ez_launch(main)

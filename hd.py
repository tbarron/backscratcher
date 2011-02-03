#!/usr/bin/python
"""
hexdump a file or data stream

Display the contents of <filename> in mixed hexadecimal / alphanumeric
format, 16 bytes to a line.

SYNOPSIS

 hd.pl <filename>

LICENSE

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
import os
import re
import sys
import unittest

from optparse import *

def main(argv = None):
    if argv == None:
        argv = sys.argv

    p = OptionParser()
    # define options here
    # p.add_option('-s', '--long',
    #              action='', default='',
    #              dest='', type='',
    #              help='')
    (o, a) = p.parse_args(argv)

    if 0 < len(a[1:]):
        for filename in a[1:]:
            if filename == '-':
                hexdump(sys.stdin)
            else:
                f = open(filename, 'r')
                hexdump(f)
                f.close()
    else:
        hexdump(sys.stdin)

def hexdump(input):
    d = input.read()
    for b in range(0, len(d), 16):
        for o in range(0, min(len(d)-b, 16)):
            if 0 == o % 4:
                sys.stdout.write(" ")
            sys.stdout.write("%02x " % ord(d[b+o]))
        for o in range(min(len(d)-b, 16), 16):
            if 0 == o % 4:
                sys.stdout.write(" ")
            sys.stdout.write("   ")
        sys.stdout.write("  ")
        for o in range(0, min(len(d)-b, 16)):
            if 0 == o % 8:
                sys.stdout.write(" ")
            if d[b+o] < ' ':
                sys.stdout.write(".")
            else:
                sys.stdout.write("%c" % d[b+o])
        for o in range(min(len(d)-b, 16), 16):
            if 0 == o % 8:
                sys.stdout.write(" ")
            sys.stdout.write(" ")
        sys.stdout.write("\n")
        
# ---------------------------------------------------------------------------
class HdTest(unittest.TestCase):
    def test_example(self):
        pass

# ---------------------------------------------------------------------------
sname = sys.argv[0]
if sname.endswith('.py') and '-L' in sys.argv:
    pname = re.sub('.py$', '', sname)
    print("creating symlink: %s -> %s" % (pname, sname))
    os.symlink(sname, pname)
elif sname.endswith('.py') and __name__ == '__main__':
    if not testhelp.main(sys.argv):
        cleanup_tests()
elif not sname.endswith('.py'):
    main(sys.argv)

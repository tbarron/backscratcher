#!/usr/bin/python
"""
list - set arithmetic on lists (subtraction, union, intersection)

   list <op> <cmdA> <cmdB>

   <op> := { minus | union | intersect }
   <cmdA> := command to produce list A (may include '|')
   <cmdB> := command to produce list B (may include '|')

EXAMPLES

   list minus "ls a*" "ls ab*"

   would produce a list of files beginning with "a" but not having "b" in
   the second position.

   list union "ls a*" "ls b*"

   would produce a list of files beginging with "a" or "b"

   list intersect "ls *g*" "ls *h*"

   would produce a list of files with both "g" and "h" in the name.

DESCRIPTION

   The program accepts an operation and two commands. Each of the
   commands are assumed to produce a list of strings. The operation is
   applied to the lists. Note that the result of the 'minus' operation
   varies with the order of cmdA and cmdB while 'union' and
   'intersection' are both commutative.

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
import pprint
import re
import sys
import unittest

# ---------------------------------------------------------------------------
def main(args):
    operation = args[1]
    Acmd = args[2]
    Bcmd = args[3]

    if (operation == "") or (Acmd == "") or (Bcmd == ""):
        usage()

    A = generate_list(Acmd)
    B = generate_list(Bcmd)

    eval("result = list_%s(A, B)" % operation)
    p = PrettyPrinter()
    p.pprint(result)
    
# ---------------------------------------------------------------------------
def generate_list(cmd):
    f = os.popen(cmd, 'r')
    rval = [x.strip() for x in f.readlines()]
    f.close()
    return rval

# ---------------------------------------------------------------------------
def list_minus(listA, listB):
    rval = listA
    for item in listB:
        if item in rval:
            rval.remove(item)
    return rval

# ---------------------------------------------------------------------------
def list_union(listA, listB):
    m = {}
    for x in listA:
        m[x] = 1
    for x in listB:
        m[x] = 1
    rval = m.keys()
    return rval

# ---------------------------------------------------------------------------
def list_intersect(listA, listB):
    rval = []
    for x in listA:
        if x in listB:
            rval.append(x)
    return rval

# ---------------------------------------------------------------------------
class ListTests(unittest.TestCase):
    # -----------------------------------------------------------------------
    def test_generate_list(self):
        a = generate_list("sysctl -a")
        assert("kern.ostype = Darwin" in a)
        assert("appleprofile.pmcs.max_thread_reservations: 20" in a)
        try:
            assert(len(a) == 635)
        except AssertionError:
            print("len(a) = %d" % len(a))

    # -----------------------------------------------------------------------
    def test_list_minus(self):
        a = list_minus(['one', 'two', 'three', 'four', 'five'],
                       ['two', 'four', 'six', 'eight'])
        assert(a == ['one', 'three', 'five'])

    # -----------------------------------------------------------------------
    def test_list_union(self):
        a = list_union(['one', 'three', 'five'],
                       ['two', 'four', 'five', 'six', 'two'])
        a.sort()
        assert(a == ['five', 'four', 'one', 'six', 'three', 'two'])

    # -----------------------------------------------------------------------
    def test_list_intersect(self):
        a = list_intersect(['one', 'two', 'three', 'four', 'five'],
                           ['two', 'four', 'six', 'eight', 'ten'])
        assert(a == ['two', 'four'])
        
# ---------------------------------------------------------------------------
global d
d = dir()
        
sname = sys.argv[0]
if sname.endswith('.py') and '-L' in sys.argv:
    pname = re.sub('.py$', '', sname)
    print("creating symlink: %s -> %s" % (pname, sname))
    os.symlink(sname, pname)
elif sname.endswith('.py') and __name__ == '__main__':
    unittest.main()
elif not sname.endswith('.py') and __name__ == '__main__':
    main(sys.argv)
                                

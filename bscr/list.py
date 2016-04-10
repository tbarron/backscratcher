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

import toolframe

# ---------------------------------------------------------------------------
def main(args=None):
    """
    CLEP
    """
    if args is None:
        args = sys.argv
    try:
        operation = args[1]
        a_cmd = args[2]
        b_cmd = args[3]
    except IndexError:
        usage()

    if (operation == "") or (a_cmd == "") or (b_cmd == ""):
        usage()

    a_list = generate_list(a_cmd)
    b_list = generate_list(b_cmd)

    lfunc = getattr(sys.modules[__name__], "list_" + operation)
    result = lfunc(a_list, b_list)
    pprint.pprint(result)


# ---------------------------------------------------------------------------
def usage():
    """
    usage
    """
    print(" ")
    print("   usage: list {minus|union|intersect} <list-1> <list-2>")
    print(" ")
    sys.exit(1)


# ---------------------------------------------------------------------------
def generate_list(cmd):
    """
    Run a command and turn its output into a list
    """
    rbl = os.popen(cmd, 'r')
    rval = [_.strip() for _ in rbl.readlines()]
    rbl.close()
    return rval


# ---------------------------------------------------------------------------
def list_minus(a_l, b_l):
    """
    compute the difference of two lists
    """
    rval = [_ for _ in a_l if _ not in b_l]
    return rval


# ---------------------------------------------------------------------------
def list_union(a_l, b_l):
    """
    compute the union of two lists

    @test: what if there are repeated values in a_l or b_l? should they be
    repeated in the result or uniquified?
    """
    rval = list(set(a_l).union(set(b_l)))
    return rval


# ---------------------------------------------------------------------------
def list_intersect(a_l, b_l):
    """
    compute the intersection of two lists
    """
    rval = []
    rval = [_ for _ in a_l if _ in b_l]
    return rval

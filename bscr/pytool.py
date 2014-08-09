#!/usr/bin/python
"""
pytool - produce skeletons for python programs

Usage:
   pytool <function> <arguments>
   'pytool help' for details

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
import os
import pdb
import pexpect
import re
import sys
import testhelp
import time
import toolframe
import util as U
import unittest


# ---------------------------------------------------------------------------
def main(args=None):
    if args is None:
        args = sys.argv
    U.dispatch(__name__, 'pt', args)


# ---------------------------------------------------------------------------
def pt_newpy(args):
    '''newpy - Create a new python program

    usage: pytool newpy <program-name>

    Creates executable file <program-name>.py with skeletal
    contents. Run "<program-name>.py -L" to create link <program-name>.
    '''

    p = optparse.OptionParser()
    (o, a) = p.parse_args(args)

    if a == []:
        raise Exception('usage: pytool newpy <program-name>')
    else:
        lname = a[0]
        pname = lname + '.py'
        are_we_overwriting([lname, '%s.py' % pname])

        f = open(pname, 'w')
        f.writelines(['#!/usr/bin/env python\n',
                      '"""\n',
                      '%s - program description\n' % lname,
                      '"""\n',
                      '\n',
                      'import optparse\n',
                      'import pdb\n',
                      'import sys\n',
                      'from bscr import toolframe\n',
                      'import unittest\n',
                      '\n',
                      'def main(argv = None):\n',
                      '    if argv == None:\n',
                      '        argv = sys.argv\n',
                      '\n',
                      '    p = optparse.OptionParser()\n',
                      "    p.add_option('-d', '--debug',\n",
                      "                 action='store_true', default=False,\n",
                      "                 dest='debug',\n",
                      "                 help='run the debugger')\n",
                      '    (o, a) = p.parse_args(argv)\n',
                      '\n',
                      '    if o.debug:\n',
                      '        pdb.set_trace()',
                      '\n',
                      '\n',
                      '    # process arguments\n',
                      '    for a in args:\n',
                      '        process(a)\n',
                      '\n',
                      'class %sTest(unittest.TestCase):\n' %
                      lname.capitalize(),
                      '    def test_example(self):\n',
                      '        pass\n',
                      '\n',
                      'toolframe.ez_launch(__name__, main)\n'])
        f.close()

        os.chmod(pname, 0755)
        os.symlink(os.path.abspath(pname), lname)


# ---------------------------------------------------------------------------
def pt_newtool(args):
    '''newtool - Create a new tool-style program

    usage: pytool newtool <program-name> <prefix>

    Creates executable file <program-name>.py with skeletal
    contents. The structure of the program is such that it is easy
    to add and describe new subfunctions.
    '''

    p = optparse.OptionParser()
    (o, a) = p.parse_args(args)

    if a == [] or len(a) != 2:
        U.fatal('usage: pytool newtool <program-name> <prefix>')
    else:
        lname = a[0]
        pname = lname + '.py'
        prefix = a[1]
        are_we_overwriting([lname, pname])

        f = open(pname, 'w')
        f.writelines(['#!/usr/bin/env python\n',
                      '"""\n',
                      '%s - program description\n' % lname,
                      '"""\n',
                      '\n',
                      'from bscr import util as U\n',
                      'import optparse\n',
                      'import os\n',
                      'import re\n',
                      'import sys\n',
                      '\n',
                      '# ----------------------------------------------------'
                      + '-----------------------\n',
                      'def %s_example(argv):\n' % prefix,
                      '    print("this is an example")\n',
                      "\n",
                      '# ----------------------------------------------------'
                      + '-----------------------\n',
                      "if __name__ == '__main__':\n",
                      "    U.dispatch('__main__', '%s', sys.argv)\n" % prefix,
                      ])
        f.close()

        os.chmod(pname, 0755)
        os.symlink(os.path.abspath(pname), lname)


# ---------------------------------------------------------------------------
def are_we_overwriting(flist):
    already = []
    for f in flist:
        if os.path.exists(f):
            already.append(f)

    if len(already) < 1:
        return
    elif len(already) < 2:
        report = '%s already exists' % already[0]
    elif len(already) < 3:
        report = '%s and %s already exist' % (already[0], already[1])
    else:
        report = ', '.join(already)

        sep = ', and '
        for a in already:
            report = sep + a + report
            sep = ', '
        report = report[2:]

    answer = raw_input('%s. Are you sure? > ' % report)

    if not re.search(r'^\s*[Yy]', answer):
        sys.exit(1)

    U.safe_unlink(already)

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

import os
import pdb
import pexpect
import re
import sys
import testhelp
import time
import toolframe
import unittest

from optparse import *
from tpbtools import *

# ---------------------------------------------------------------------------
def pt_newpy(args):
    '''newpy - Create a new python program

    usage: pytool newpy <program-name>

    Creates executable file <program-name>.py with skeletal
    contents. Run "<program-name>.py -L" to create link <program-name>.
    '''

    p = OptionParser()
    (o, a) = p.parse_args(args)

    if a == []:
        raise Exception('usage: pytool newpy <program-name>')
    else:
        pname = a[0]
        are_we_overwriting([pname, '%s.py' % pname])

        f = open('%s.py' % pname, 'w')
        f.writelines(['#!/usr/bin/python\n',
                      '"""\n',
                      '%s - program description\n' % pname,
                      '"""\n',
                      '\n',
                      # 'import getopt\n',
                      'import sys\n',
                      'import toolframe\n',
                      '\n',
                      'from optparse import *\n',
                      '\n',
                      'def main(argv = None):\n',
                      '    if argv == None:\n',
                      '        argv = sys.argv\n',
                      '\n',
                      '    p = OptionParser()\n',
                      '    # define options here\n',
                      "    # p.add_option('-s', '--long',\n",
                      "    #              action='', default='',\n",
                      "    #              dest='', type='',\n",
                      "    #              help='')\n",
                      '    (o, a) = p.parse_args(argv)\n',
                      '\n',
                      '    # process arguments\n',
                      '    for a in args:\n',
                      '        process(a)\n',
                      '\n',
                      'class %sTest(unittest.TestCase):\n' %
                          pname.capitalize(),
                      '    def test_example(self):\n',
                      '        pass\n',
                      '\n',
                      'toolframe.ez_launch(main)\n'])
        f.close()

        os.chmod('%s.py' % pname, 0755)

# ---------------------------------------------------------------------------
def pt_newtool(args):
    '''newtool - Create a new tool-style program

    usage: pytool newtool <program-name> <prefix>

    Creates executable file <program-name>.py with skeletal
    contents. The structure of the program is such that it is easy
    to add and describe new subfunctions.
    '''

    p = OptionParser()
    (o, a) = p.parse_args(args)

    if a == [] or len(a) != 2:
        raise Exception('usage: pytool newtool <program-name> <prefix>')
    else:
        pname = a[0]
        prefix = a[1]
        are_we_overwriting([pname, '%s.py' % pname])

        f = open('%s.py' % pname, 'w')
        f.writelines(['#!/usr/bin/python\n',
                      '"""\n',
                      '%s - program description\n' % pname,
                      '"""\n',
                      '\n',
                      'import os\n',
                      'import re\n',
                      'import sys\n',
                      'import toolframe\n',
                      '\n',
                      'from optparse import *\n',
                      '\n',
                      '# ----------------------------------------------------'
                      + '-----------------------\n',
                      'def tt_example(argv):\n',
                      '    print("this is an example")\n',
                      "\n",
                      '# ----------------------------------------------------'
                      + '-----------------------\n',
                      "toolframe.tf_launch(\"tt\")"
                      ])
        f.close()

        os.chmod('%s.py' % pname, 0755)

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
                           
# ---------------------------------------------------------------------------
class PytoolTest(unittest.TestCase):
    # -----------------------------------------------------------------------
    def test_newpy_x(self):
        '''
        Run "pytool newpy xyzzy". Verify that xyzzy and xyzzy.py are created
        and have the right contents.
        '''
        prepare_tests()
        safe_unlink(['xyzzy', 'xyzzy.py'])
        S = pexpect.spawn('../pytool newpy xyzzy')
        try:
            S.expect(pexpect.EOF)
        except pexpect.TIMEOUT:
            fail('pytool should not prompt in this case')
        assert(not os.path.exists('xyzzy'))
        assert(os.path.exists('xyzzy.py'))
        
        got = contents('xyzzy.py')
        expected = expected_xyzzy_py()
        testhelp.expectVSgot(expected, got)

    # -----------------------------------------------------------------------
    def test_newpy_overwriting_no(self):
        '''
        Run "pytool newpy xyzzy" when xyzzy already exists. Verify
        that confirmation is requested. Answer "no" and verify that
        the existing file is not overwritten.
        '''
        prepare_tests()
        safe_unlink(['xyzzy', 'xyzzy.py'])
        writefile('xyzzy', ['original xyzzy\n'])
        writefile('xyzzy.py', ['original xyzzy.py\n'])
        S = pexpect.spawn('../pytool newpy xyzzy')
        which = S.expect([r'you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')
        else:
            self.fail('should have asked about overwriting xyzzy')
            
        expected = ['original xyzzy\n']
        got = contents('xyzzy')
        assert(expected == got)

        expected = ['original xyzzy.py\n']
        got = contents('xyzzy.py')
        assert(expected == got)

    # -----------------------------------------------------------------------
    def test_newpy_overwriting_yes(self):
        '''
        Run "pytool newpy xyzzy" when xyzzy, xyzzy.py already exist.
        Verify that confirmation is requested. Answer "yes" and verify
        that the existing file IS overwritten.
        '''
        prepare_tests()
        safe_unlink(['xyzzy', 'xyzzy.py'])
        writefile('xyzzy.py', ['original xyzzy\n'])
        S = pexpect.spawn('../pytool newpy xyzzy')
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('yes')
            S.expect(pexpect.EOF)
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')
        else:
            self.fail('should have asked about overwriting xyzzy')
            
        assert(not os.path.exists('xyzzy'))
        
        expected = expected_xyzzy_py()
        got = contents('xyzzy.py')
        testhelp.expectVSgot(expected, got)

    # -----------------------------------------------------------------------
    def test_newtool(self):
        '''
        Run "pytool newtool testtool tt". Verify that testtool.py
        is created and has the right contents.
        '''
        prepare_tests()
        safe_unlink(['testtool', 'testtool.py'])
        S = pexpect.spawn('../pytool newtool testtool tt')
        S.logfile = sys.stdout
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
            self.fail('should not have asked about overwriting')
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')
            
        assert(not os.path.exists('testtool'))

        expected = expected_testtool_py()
        got = contents('testtool.py')
        testhelp.expectVSgot(expected, got)

    # -----------------------------------------------------------------------
    def test_help(self):
        '''
        Run "pytool help". Verify that the output is correct
        '''
        prepare_tests()
        outputs = ['testtool', 'testtool.py', 'xyzzy', 'xyzzy.py']
        safe_unlink(outputs)
        S = pexpect.spawn('../pytool help')
        # S.logfile = sys.stdout
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
            self.fail('should not have asked about overwriting')
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')
            
        # !@! check that none of the outputs exist
        for file in outputs:
            assert(not os.path.exists(file))
            
    # -----------------------------------------------------------------------
    def test_help_newpy(self):
        '''
        Run "pytool help newpy". Verify that the output is correct.
        '''
        prepare_tests()
        S = pexpect.spawn('../pytool help newpy')
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
            self.fail('should not have asked about overwriting')
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')

        got = S.before.split('\r\n')
        expected = ['newpy - Create a new python program',
                    '',
                    '    usage: pytool newpy <program-name>',
                    '',
                    '    Creates executable file <program-name>.py'
                       + ' with skeletal',
                    '    contents. Run "<program-name>.py -L" to create'
                       + ' link <program-name>.',
                    '    ',
                    '']
        testhelp.expectVSgot(expected, got)
        
    # -----------------------------------------------------------------------
    def test_help_newtool(self):
        '''
        Run "pytool help newtool". Verify that the output is correct.
        '''
        prepare_tests()
        S = pexpect.spawn('../pytool help newtool')
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
            self.fail('should not have asked about overwriting')
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')

        got = S.before.split('\r\n')
        expected = ['newtool - Create a new tool-style program',
                    '',
                    '    usage: pytool newtool <program-name> <prefix>',
                    '',
                    '    Creates executable file <program-name>.py'
                        + ' with skeletal',
                    '    contents. The structure of the program is such'
                        + ' that it is easy',
                    '    to add and describe new subfunctions.',
                    '    ',
                    '']
        testhelp.expectVSgot(expected, got)
        
# ---------------------------------------------------------------------------
def cleanup():
    global testdir
    if testdir == os.path.basename(os.getcwd()):
        os.chdir("..")
    if os.path.isdir(testdir):
        rmrf(testdir)

# ---------------------------------------------------------------------------
def expected_testtool_py():
    expected = ['#!/usr/bin/python\n',
                '"""\n',
                'testtool - program description\n',
                '"""\n',
                '\n',
                'import os\n',
                'import re\n',
                'import sys\n',
                'import toolframe\n',
                '\n',
                'from optparse import *\n',
                '\n',
                '# ----------------------------------------------------'
                    + '-----------------------\n',
                'def tt_example(argv):\n',
                '    print("this is an example")\n',
                "\n",
                '# ----------------------------------------------------'
                    + '-----------------------\n',
                "toolframe.tf_launch(\"tt\")"]
    
    return expected

# ---------------------------------------------------------------------------
def expected_xyzzy_py():
    expected = ['#!/usr/bin/python\n',
                '"""\n',
                'xyzzy - program description\n',
                '"""\n',
                '\n',
                # 'import getopt\n',
                'import sys\n',
                'import toolframe\n',
                '\n',
                'from optparse import *\n',
                '\n',
                'def main(argv = None):\n',
                '    if argv == None:\n',
                '        argv = sys.argv\n',
                '\n',
                '    p = OptionParser()\n',
                '    # define options here\n',
                "    # p.add_option('-s', '--long',\n",
                "    #              action='', default='',\n",
                "    #              dest='', type='',\n",
                "    #              help='')\n",
                '    (o, a) = p.parse_args(argv)\n',
                '\n',
                '    # process arguments\n',
                '    for a in args:\n',
                '        process(a)\n',
                '\n',
                'class XyzzyTest(unittest.TestCase):\n',
                '    def test_example(self):\n',
                '        pass\n',
                '\n',
                'toolframe.ez_launch(main)\n',]

    return expected

# ---------------------------------------------------------------------------
def prepare_tests():
    global testdir
    testdir = testhelp.into_test_dir()

# ---------------------------------------------------------------------------
toolframe.tf_launch('pt', cleanup)

import os
import pdb
import pexpect
import shutil
from nose.plugins.skip import SkipTest
import sys
from bscr import testhelp as th
from bscr import util as U


class TestPytool(th.HelpedTestCase):
    testdir = "/tmp/test_pytool"

    # -----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(TestPytool.testdir):
            os.mkdir(TestPytool.testdir)

    # -----------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        kf = os.getenv("KEEPFILES")
        if kf is None or not int(kf):
            shutil.rmtree(TestPytool.testdir)

    # -----------------------------------------------------------------------
    def test_newpy_x(self):
        '''
        Run "pytool newpy xyzzy". Verify that xyzzy and xyzzy.py are created
        and have the right contents.
        '''
        with U.Chdir(self.testdir):
            U.safe_unlink(['xyzzy', 'xyzzy.py'])
            cmd = pexpect.which("pytool")
            r = pexpect.run('%s newpy xyzzy' % cmd)
            assert(not os.path.exists('xyzzy'))
            assert(os.path.exists('xyzzy.py'))

            got = U.contents('xyzzy.py')
            exp = self.expected_xyzzy_py()
            th.expectVSgot(exp, got)

    # -----------------------------------------------------------------------
    def test_newpy_overwriting_no(self):
        '''
        Run "pytool newpy xyzzy" when xyzzy already exists. Verify
        that confirmation is requested. Answer "no" and verify that
        the existing file is not overwritten.
        '''
        with U.Chdir(self.testdir):
            U.safe_unlink(['xyzzy', 'xyzzy.py'])
            U.writefile('xyzzy', ['original xyzzy\n'])
            U.writefile('xyzzy.py', ['original xyzzy.py\n'])
            cmd = pexpect.which("pytool")
            S = pexpect.spawn('%s newpy xyzzy' % cmd)
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

            expected = ['original xyzzy']
            got = U.contents('xyzzy')
            assert(expected == got)

            expected = ['original xyzzy.py']
            got = U.contents('xyzzy.py')
            assert(expected == got)

    # -----------------------------------------------------------------------
    def test_newpy_overwriting_yes(self):
        '''
        Run "pytool newpy xyzzy" when xyzzy, xyzzy.py already exist.
        Verify that confirmation is requested. Answer "yes" and verify
        that the existing file IS overwritten.
        '''
        with U.Chdir(self.testdir):
            U.safe_unlink(['xyzzy', 'xyzzy.py'])
            U.writefile('xyzzy.py', ['original xyzzy\n'])
            cmd = pexpect.which('pytool')
            S = pexpect.spawn('%s newpy xyzzy' % cmd)
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

            expected = self.expected_xyzzy_py()
            got = U.contents('xyzzy.py')
            th.expectVSgot(expected, got)

    # -----------------------------------------------------------------------
    def test_newtool(self):
        '''
        Run "pytool newtool testtool tt". Verify that testtool.py
        is created and has the right contents.
        '''
        with U.Chdir(self.testdir):
            U.safe_unlink(['testtool', 'testtool.py'])
            cmd = pexpect.which("pytool")
            if cmd is None:
                raise SkipTest
            S = pexpect.spawn('%s newtool testtool tt' % cmd)
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

            expected = self.expected_testtool_py()
            got = U.contents('testtool.py')
            th.expectVSgot(expected, got)

    # -----------------------------------------------------------------------
    def test_help(self):
        '''
        Run "pytool help". Verify that the output is correct
        '''
        with U.Chdir(self.testdir):
            outputs = ['testtool', 'testtool.py', 'xyzzy', 'xyzzy.py']
            U.safe_unlink(outputs)
            cmd = pexpect.which('pytool')
            S = pexpect.spawn('%s help' % cmd)
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
        with U.Chdir(self.testdir):
            cmd = pexpect.which('pytool')
            S = pexpect.spawn('%s help newpy' % cmd)
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
            th.expectVSgot(expected, got)

    # -----------------------------------------------------------------------
    def test_help_newtool(self):
        '''
        Run "pytool help newtool". Verify that the output is correct.
        '''
        with U.Chdir(self.testdir):
            cmd = pexpect.which('pytool')
            S = pexpect.spawn('%s help newtool' % cmd)
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
            th.expectVSgot(expected, got)

    # -------------------------------------------------------------------------
    def expected_testtool_py(self):
        expected = ['#!/usr/bin/python',
                    '"""',
                    'testtool - program description',
                    '"""',
                    '',
                    'import os',
                    'import re',
                    'import sys',
                    'import toolframe',
                    '',
                    'from optparse import *',
                    '',
                    '# ----------------------------------------------------'
                    + '-----------------------',
                    'def tt_example(argv):',
                    '    print("this is an example")',
                    "",
                    '# ----------------------------------------------------'
                    + '-----------------------',
                    "toolframe.tf_launch(\"tt\")"]

        return expected

    # -------------------------------------------------------------------------
    def expected_xyzzy_py(self):
        expected = ['#!/usr/bin/python',
                    '"""',
                    'xyzzy - program description',
                    '"""',
                    '',
                    # 'import getopt',
                    'import sys',
                    'import toolframe',
                    'import unittest',
                    '',
                    'from optparse import *',
                    '',
                    'def main(argv = None):',
                    '    if argv == None:',
                    '        argv = sys.argv',
                    '',
                    '    p = OptionParser()',
                    '    # define options here',
                    "    # p.add_option('-s', '--long',",
                    "    #              action='', default='',",
                    "    #              dest='', type='',",
                    "    #              help='')",
                    '    (o, a) = p.parse_args(argv)',
                    '',
                    '    # process arguments',
                    '    for a in args:',
                    '        process(a)',
                    '',
                    'class XyzzyTest(unittest.TestCase):',
                    '    def test_example(self):',
                    '        pass',
                    '',
                    'toolframe.ez_launch(__name__, main)', ]

        return expected

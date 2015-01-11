import os
import pdb
import pexpect
import shutil
import sys
from bscr import testhelp as th
from bscr import util as U


class TestPytool(th.HelpedTestCase):
    testdir = "/tmp/test_pytool"

    # -----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """
        Called before each test
        """
        if not os.path.exists(TestPytool.testdir):
            os.mkdir(TestPytool.testdir)

    # -----------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        """
        Called after each test
        """
        kf = os.getenv("KEEPFILES")
        if kf is None or not int(kf):
            shutil.rmtree(TestPytool.testdir)

    # -----------------------------------------------------------------------
    def test_newpy_x(self):
        """
        Run 'pytool newpy xyzzy'. Verify that xyzzy and xyzzy.py are created
        and have the right contents.
        """
        with U.Chdir(self.testdir):
            lname = 'xyzzy'
            pname = lname + '.py'
            U.safe_unlink([lname, pname])
            cmd = pexpect.which("pytool")
            r = pexpect.run('%s newpy %s' % (cmd, lname))

            self.assertTrue(os.path.exists(pname))
            exp = os.path.abspath(pname)
            act = os.readlink(lname)
            self.assertEqual(exp, act,
                             "\nExpected '%s'\n     got '%s'" %
                             (exp, act))

            got = U.contents(pname)
            exp = self.expected_xyzzy_py()
            self.assertEq(exp, got)

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
        lname = "xyzzy"
        pname = lname + ".py"
        name_l = [lname, pname]
        with U.Chdir(self.testdir):
            U.safe_unlink(name_l)
            for name in name_l:
                U.writefile(name, ['original %s\n' % name])
            cmd = pexpect.which('pytool')
            S = pexpect.spawn('%s newpy %s' % (cmd, lname))
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

            exp = os.path.abspath(pname)
            got = os.readlink(lname)
            self.assertEqual(exp, got,
                             "\nExpected '%s',\n     got '%s'" %
                             (exp, got))

            expected = self.expected_xyzzy_py()
            got = U.contents(pname)
            self.assertEq(expected, got)

    # -----------------------------------------------------------------------
    def test_newtool(self):
        '''
        Run "pytool newtool testtool tt" while testtool.py does not exist.
        Verify that testtool.py is created and has the right contents.
        '''
        toolname = "testtool.py"
        toollink = "testtool"
        with U.Chdir(self.testdir):
            U.safe_unlink([toollink, toolname])
            cmd = pexpect.which("pytool")
            if cmd is None:
                pytest.skip("pytool not found")
            S = pexpect.spawn('%s newtool %s tt' % (cmd, toollink))
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

            # assert(not os.path.exists('testtool'))
            exp = os.path.abspath(toolname)
            actual = os.readlink(toollink)
            self.assertEqual(exp, actual,
                             "\nExpected '%s'\n     got '%s'" %
                             (exp, actual))

            expected = self.expected_testtool_py()
            got = U.contents('testtool.py')
            self.assertEq(expected, got)

    # -----------------------------------------------------------------------
    def test_newtool_overwriting_no(self):
        """
        Run "pytool newtool testtool tt" while testtool.py does exist. Verify
        that we are prompted about overwriting. Answer "no" and verify that the
        original file is not overwritten.
        """
        tlink = "testtool"
        tname = tlink + ".py"
        with U.Chdir(self.testdir):
            U.safe_unlink([tlink, tname])
            U.writefile(tname, ["original %s\n" % tname])
            U.writefile(tlink, ["original %s\n" % tlink])
            cmd = pexpect.which("pytool")
            if cmd is None:
                pytest.skip("pytool not found")
            S = pexpect.spawn('%s newtool %s tt' % (cmd, tlink))
            which = S.expect([r'Are you sure\? >',
                              'Error:',
                              pexpect.EOF])
            if which == 0:
                S.sendline('no')
                S.expect(pexpect.EOF)
                # self.fail('should not have asked about overwriting')
            elif which == 1:
                print S.before + S.after
                self.fail('unexpected exception')
            else:
                self.fail("should have asked about overwriting %s" % tname)

            for fname in [tlink, tname]:
                exp = ["original %s" % fname]
                got = U.contents(fname)
                self.assertEqual(exp, got,
                                 "\nExpected '%s'\n     got '%s'" %
                                 (exp, got))

    # -----------------------------------------------------------------------
    def test_newtool_overwriting_yes(self):
        """
        Run 'pytool newtool testtool tt' while testtool.py exists. Verify that
        we are prompted about overwriting. Answer 'yes' and verify that the
        original file is overwritten.
        """
        tlink = "testtool"
        tname = tlink + ".py"
        with U.Chdir(self.testdir):
            U.safe_unlink([tlink, tname])
            U.writefile(tname, ["original %s\n" % tname])
            U.writefile(tlink, ["original %s\n" % tlink])
            cmd = pexpect.which("pytool")
            if cmd is None:
                pytest.skip("pytool not found")
            S = pexpect.spawn('%s newtool %s tt' % (cmd, tlink))
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
                self.fail("should have asked about overwriting %s" % tname)

            exp = os.path.abspath(tname)
            actual = os.readlink(tlink)
            self.assertEqual(exp, actual,
                             "\nExpected '%s'\n     got '%s'" %
                             (exp, actual))

            expected = self.expected_testtool_py()
            got = U.contents(tname)
            self.assertEq(expected, got)

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
            self.assertEq(expected, got)

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
            self.assertEq(expected, got)

    # -------------------------------------------------------------------------
    def expected_testtool_py(self):
        """
        The expected output of a new tool request
        """
        expected = ['#!/usr/bin/env python',
                    '"""',
                    'testtool - program description',
                    '"""',
                    '',
                    'from bscr import util as U',
                    'import optparse',
                    'import os',
                    'import re',
                    'import sys',
                    '',
                    '# ----------------------------------------------------'
                    + '-----------------------',
                    'def tt_example(argv):',
                    '    print("this is an example")',
                    "",
                    '# ----------------------------------------------------'
                    + '-----------------------',
                    "if __name__ == '__main__':",
                    "    U.dispatch('__main__', 'tt', sys.argv)",
                    ]

        return expected

    # -------------------------------------------------------------------------
    def expected_xyzzy_py(self):
        """
        The expected output of a new py request
        """
        expected = ['#!/usr/bin/env python',
                    '"""',
                    'xyzzy - program description',
                    '"""',
                    '',
                    'import optparse',
                    'import pdb',
                    'import sys',
                    'from bscr import toolframe',
                    'import unittest',
                    '',
                    'def main(argv = None):',
                    '    if argv == None:',
                    '        argv = sys.argv',
                    '',
                    '    p = optparse.OptionParser()',
                    "    p.add_option('-d', '--debug',",
                    "                 action='store_true', default=False,",
                    "                 dest='debug',",
                    "                 help='run the debugger')",
                    '    (o, a) = p.parse_args(argv)',
                    "",
                    "    if o.debug:",
                    "        pdb.set_trace()",
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

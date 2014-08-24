#!/usr/bin/env python
import pdb
from bscr import fl
from bscr import util
import os
import pexpect
import random
import shutil
from nose.plugins.skip import SkipTest
import stat
from bscr import testhelp as th
import time
import unittest


# ---------------------------------------------------------------------------
def setUpModule():
    """
    Run once before any of the tests in this module
    """
    if os.path.basename(os.getcwd()) == 'fl_tests':
        return

    if not os.path.exists('fl_tests'):
        os.mkdir('fl_tests')
        os.mkdir('fl_tests/old')


# ---------------------------------------------------------------------------
def tearDownModule():
    """
    Run once after all the tests in this module
    """
    kf = os.getenv('KEEPFILES')
    if not kf:
        shutil.rmtree('fl_tests')


# ---------------------------------------------------------------------------
class TestFL(th.HelpedTestCase):
    # tests needed:
    #   'fl' -- test_command_line
    #   'fl help' -- test_fl_help
    #   'fl help help' -- test_fl_help_help
    #   'fl help rm_cr'
    #   'fl times'
    #   'fl nosuchcmd'
    # -----------------------------------------------------------------------
    def test_command_line(self):
        """
        Running the command with no arguments should get help output
        """
        thisone = util.script_location("fl")

        # print(thisone)
        result = pexpect.run(thisone)
        self.assertNotIn("Traceback", result)
        self.assertIn("diff", result)
        self.assertIn("save", result)
        self.assertIn("times", result)

    # -------------------------------------------------------------------------
    def test_fl_help(self):
        """
        'fl help' should get help output
        """
        cmd = util.script_location("fl")
        result = pexpect.run('%s help' % cmd)
        self.assertFalse('Traceback' in result)
        for f in [x for x in dir(fl) if x.startswith('bscr_')]:
            subc = f.replace('bscr_', '')
            self.assertTrue('%s - ' % subc in result)

    # -------------------------------------------------------------------------
    def test_fl_help_help(self):
        """
        'fl help help' should get help for the help command
        """
        cmd = pexpect.which('fl')
        result = pexpect.run('%s help help' % cmd)
        self.assertFalse('Traceback' in result)
        for f in ['help - show a list of available commands',
                  'With no arguments, show a list of commands',
                  'With a command as argument, show help for that command',
                  ]:
            self.assertTrue(f in result)

    # -----------------------------------------------------------------------
    def test_most_recent_prefix_match(self):
        """
        Test the routine most_recent_prefix_match()
        """
        with util.Chdir("fl_tests"):
            util.writefile('mrpm1', ['this is a test file'])
            util.writefile('mrpm2', ['this is another test file'])
            os.system('cp mrpm1 mrpm1.2009-10-01')
            os.system('cp mrpm2 old/mrpm2.2009-08-31')

            a = fl.most_recent_prefix_match('.', 'mrpm1')
            th.expectVSgot('./mrpm1.2009-10-01', a)

            a = fl.most_recent_prefix_match('.', 'mrpm2')
            th.expectVSgot('./old/mrpm2.2009-08-31', a)

    # -----------------------------------------------------------------------
    def test_diff(self):
        """
        Test diff
        """
        with util.Chdir("fl_tests"):
            util.writefile('mrpm1', ['this is a test file\n'])
            util.writefile('mrpm2', ['this is another test file\n'])
            util.writefile('mrpm1.2009-10-01', ['copy of test file\n'])
            util.writefile('old/mrpm2.2009-08-31',
                           ['copy of another test file\n'])

            expected = ['diff ./mrpm1.2009-10-01 mrpm1\r',
                        '1c1\r',
                        '< copy of test file\r',
                        '---\r',
                        '> this is a test file\r',
                        '']
            cmd = util.script_location("fl")
            got = pexpect.run("%s diff mrpm1" % cmd).split("\n")
            self.assertEqual(expected, got)

            expected = ['diff ./old/mrpm2.2009-08-31 mrpm2\r',
                        '1c1\r',
                        '< copy of another test file\r',
                        '---\r',
                        '> this is another test file\r',
                        '']
            got = pexpect.run("%s diff mrpm2" % cmd).split("\n")
            self.assertEqual(expected, got)

    # -----------------------------------------------------------------------
    def test_revert(self):
        """
        Test revert
        """
        with util.Chdir("fl_tests"):
            util.writefile('mrpm1', ['this is a test file\n'])
            util.writefile('mrpm2', ['this is another test file\n'])
            util.writefile('mrpm1.2009-10-01', ['reverted\n'])
            util.writefile('old/mrpm2.2009-08-31',
                           ['REVERTED\n'])

            fl = util.script_location("fl")
            os.system('%s revert mrpm1' % fl)
            assert(os.path.exists('mrpm1.new'))
            assert(os.path.exists('mrpm1'))
            assert(not os.path.exists('mrpm1.2009-10-01'))
            assert(util.contents('mrpm1') == ['reverted'])

            os.system('%s revert mrpm2' % fl)
            assert(os.path.exists('mrpm2.new'))
            assert(os.path.exists('mrpm2'))
            assert(not os.path.exists('old/mrpm2.2009-08-31'))
            assert(util.contents('mrpm2') == ['REVERTED'])

    # -----------------------------------------------------------------------
    def test_atom(self):
        """
        Test set_atime_to_mtime
        """
        with util.Chdir("fl_tests"):
            filename = 'atom'
            open(filename, 'w').close()
            os.utime(filename, (time.time() - random.randint(1000, 2000),
                                time.time() + random.randint(1000, 2000)))
            s = os.stat(filename)
            assert(s[stat.ST_ATIME] != s[stat.ST_MTIME])
            fl.fl_set_atime_to_mtime([filename])
            s = os.stat(filename)
            assert(s[stat.ST_ATIME] == s[stat.ST_MTIME])

    # -----------------------------------------------------------------------
    def test_mtoa(self):
        """
        Test set_mtime_to_atime
        """
        with util.Chdir("fl_tests"):
            filename = 'mtoa'
            open(filename, 'w').close()
            os.utime(filename, (time.time() - random.randint(1000, 2000),
                                time.time() + random.randint(1000, 2000)))
            s = os.stat(filename)
            assert(s[stat.ST_ATIME] != s[stat.ST_MTIME])
            fl.fl_set_mtime_to_atime([filename])
            s = os.stat(filename)
            assert(s[stat.ST_ATIME] == s[stat.ST_MTIME])

    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.fl', __file__)

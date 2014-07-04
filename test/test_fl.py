#!/usr/bin/env python
import pdb
from bscr import fl
from bscr import util
import os
import pexpect
import random
import shutil
import stat
import testhelp
import time
import unittest

# ---------------------------------------------------------------------------
def setUpModule():
    if os.path.basename(os.getcwd()) == 'fl_tests':
        return

    if not os.path.exists('fl_tests'):
        os.mkdir('fl_tests')
        os.mkdir('fl_tests/old')
        
# ---------------------------------------------------------------------------
def tearDownModule():
    kf = os.getenv('KEEPFILES')
    if not kf:
        shutil.rmtree('fl_tests')

# ---------------------------------------------------------------------------
class TestFL(unittest.TestCase):
    # tests needed:
    #   'fl' -- test_command_line
    #   'fl help' -- test_fl_help
    #   'fl help help' -- test_fl_help_help
    #   'fl help rm_cr'
    #   'fl times'
    #   'fl nosuchcmd'
    # -----------------------------------------------------------------------
    def test_command_line(self):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.path.basename(here) == 'bscr':
            sp = os.path.dirname(here)
            f = util.contents("%s/backscratcher-learn-py2.7.egg-info/installed-files.txt" %
                              sp)
            for each in f:
                if each.endswith("bin/%s" % fl):
                    thisone = each
        else:
            thisone = "%s/bin/fl" % here

        # print(thisone)
        result = pexpect.run(thisone)
        self.assertNotIn("Traceback", result)
        self.assertIn("diff", result)
        self.assertIn("save", result)
        self.assertIn("times", result)

    # -------------------------------------------------------------------------
    def test_fl_help(self):
        where = pexpect.which('fl')
        here = os.path.basename(os.getcwd())
        if where is None or here == 'backscratcher':
            cmd = "bin/fl"
        else:
            cmd = "fl"
            
        result = pexpect.run('%s help' % cmd)
        self.assertFalse('Traceback' in result)
        for f in [x for x in dir(fl) if x.startswith('bscr_')]:
            subc = f.replace('bscr_', '')
            self.assertTrue('%s - ' % subc in result)
        
    # -------------------------------------------------------------------------
    def test_fl_help_help(self):
        where = pexpect.which('fl')
        here = os.path.basename(os.getcwd())
        if where is None or here == 'backscratcher':
            cmd = "bin/fl"
        else:
            cmd = "fl"
            
        result = pexpect.run('%s help help' % cmd)
        self.assertFalse('Traceback' in result)
        for f in ['help - show a list of available commands',
                  'With no arguments, show a list of commands',
                  'With a command as argument, show help for that command',]:
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
            testhelp.expectVSgot('./mrpm1.2009-10-01', a)

            a = fl.most_recent_prefix_match('.', 'mrpm2')
            testhelp.expectVSgot('./old/mrpm2.2009-08-31', a)

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
            
            expected = ['diff ./mrpm1.2009-10-01 mrpm1\n',
                        '1c1\n',
                        '< copy of test file\n',
                        '---\n',
                        '> this is a test file\n']
            f = os.popen('fl diff mrpm1')
            got = f.readlines()
            f.close()
            self.assertEqual(expected, got)
            
            expected = ['diff ./old/mrpm2.2009-08-31 mrpm2\n',
                        '1c1\n',
                        '< copy of another test file\n',
                        '---\n',
                        '> this is another test file\n']
            f = os.popen('fl diff mrpm2')
            got = f.readlines()
            f.close()
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
            
            os.system('fl revert mrpm1')
            assert(os.path.exists('mrpm1.new'))
            assert(os.path.exists('mrpm1'))
            assert(not os.path.exists('mrpm1.2009-10-01'))
            assert(util.contents('mrpm1') == ['reverted\n'])
            
            os.system('fl revert mrpm2')
            assert(os.path.exists('mrpm2.new'))
            assert(os.path.exists('mrpm2'))
            assert(not os.path.exists('old/mrpm2.2009-08-31'))
            assert(util.contents('mrpm2') == ['REVERTED\n'])

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
    @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.fail("construction")
        
    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_which_script(self):
        """
        Verify that we're running the right script
        """
        self.fail('construction')

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/python
"""
perrno tests
"""
from bscr import perrno
from bscr import util as U
import pexpect
import sys
from bscr import testhelp as th
import unittest

# -----------------------------------------------------------------------------
class TestPerrno(unittest.TestCase):
    def test_all(self):
        with th.StdoutExcursion() as getval:
            perrno.main(["bin/perrno", "--all"])
            result = getval()
        self.assertIn("13  EACCES           Permission denied", result)
        self.assertNotIn("['EACCES']", result)

    def test_mnemonic(self):
        result = perrno.etranslate("EBADF")
        self.assertEqual("    9  EBADF            Bad file descriptor", result)

    def test_numeric(self):
        result = perrno.etranslate("3")
        self.assertEqual("    3  ESRCH            No such process", result)

    # -------------------------------------------------------------------------
    def test_perrno_help(self):
        """
        Verify that 'perrno --help' does the right thing
        """
        exp = ["Usage: perrno {-a|--all|number ...|errname ...}",
               "    report errno numeric and string values",
               "",
               "Options:",
               "  -h, --help   show this help message and exit",
               "  -a, --all    list all errno values",
               "  -d, --debug  run the debugger",
               ]
        cmd = U.script_location("perrno")
        actual = pexpect.run("%s --help" % cmd)
        for line in exp:
            self.assertTrue(line in actual,
                            "Expected '%s' in %s" %
                            (line, U.lquote(actual)))
    
    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        idir = U.bscr_root(sys.modules['bscr.perrno'].__file__)
        exp = U.bscr_test_root(__file__)
        self.assertEqual(exp, idir,
                         "Expected '%s', got '%s'" % (exp, idir))

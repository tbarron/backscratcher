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
class TestPerrno(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_all(self):
        """
        Test 'perrno --all'
        """
        with th.StdoutExcursion() as getval:
            perrno.main(["bin/perrno", "--all"])
            result = getval()
        self.assertIn("13  EACCES           Permission denied", result)
        self.assertNotIn("['EACCES']", result)

    # -------------------------------------------------------------------------
    def test_mnemonic(self):
        """
        Calling perrno for a particular error name
        """
        result = perrno.etranslate("EBADF")
        self.assertEqual("    9  EBADF            Bad file descriptor", result)

    # -------------------------------------------------------------------------
    def test_numeric(self):
        """
        Calling perrno for a particular error number
        """
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
        self.assertModule('bscr.perrno', __file__)

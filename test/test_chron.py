#!/usr/bin/env python
from bscr import chron
from bscr import testhelp as th
from bscr import util as U
import pexpect
import unittest


# -----------------------------------------------------------------------------
class TestChron(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_hms_seconds(self):
        """
        Converting %H:%M:%S to an epoch time
        """
        exp = 3923
        act = chron.hms_seconds("1:05:23")
        self.assertEqual(exp, act,
                         "Expected %d, got %d" % (exp, act))

    # -------------------------------------------------------------------------
    def test_chron_help(self):
        """
        Verify that 'chron --help' does the right thing
        """
        self.assertOptionHelp("chron",
                              "chronometer/stopwatch")

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.chron', __file__)
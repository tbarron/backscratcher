#!/usr/bin/python
"""
jcal tests
"""
from bscr import jcal
from nose.plugins.skip import SkipTest
import pexpect
from bscr import testhelp as th
from bscr import util as U
import unittest


# -----------------------------------------------------------------------------
class JcalTest(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_EMPTY(self):
        pass

    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_jcal_help(self):
        """
        Verify that 'jcal --help' does the right thing
        """
        cmd = U.script_location("jcal")
        result = pexpect.run("%s help" % cmd)
        exp = "help - show this list"
        self.assertTrue(exp in result, "Expected '%s' in %s" %
                        (exp, U.lquote(result)))

    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.jcal', __file__)

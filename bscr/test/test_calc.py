#!/usr/bin/env python
from bscr import calc
import pexpect
from nose.plugins.skip import SkipTest
import sys
import unittest
from bscr import testhelp as th
from bscr import util as U


# -----------------------------------------------------------------------------
def setUpModule():
    U.pythonpath_bscrroot()


# -----------------------------------------------------------------------------
class TestCalc(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_example(self):
        calc = U.script_location("calc")
        S = pexpect.spawn(calc)
        # S.logfile = sys.stdout
        S.expect("> ")

        S.sendline("7 + 12")
        S.expect("> ")

        assert("19" in S.before)

        S.sendline("7.988 + 28.576")
        S.expect("> ")

        assert("36.564000" in S.before)

        S.sendline("\"zap\" * 2")
        S.expect("> ")

        assert("zapzap" in S.before)

        S.sendline("exit()")
        S.expect(pexpect.EOF)
        S.close()

    # -------------------------------------------------------------------------
    def test_calc_help(self):
        """
        Verify that 'calc --help' does the right thing
        """
        cmd = U.script_location("calc")
        result = pexpect.run("%s --help" % cmd)
        nexp = "Traceback"
        self.assertFalse(nexp in result,
                         "Not expecting '%s' in %s" %
                         (nexp, U.lquote(result)))
        exp = "Usage: calc [options]"
        self.assertTrue(exp in result,
                        "Expected '%s' in %s" %
                        (exp, U.lquote(result)))

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.calc', __file__)

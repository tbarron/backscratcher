"""
jcal tests
"""
from bscr import jcal                          # noqa: ignore=F401
import pexpect
from bscr import testhelp as th
from bscr import util as U
import pytest


# -----------------------------------------------------------------------------
def test_standalone():
def test_jcal_help():
    """
    Make these tests stand-alone
    Verify that 'jcal --help' does the right thing
    """
    pytest.fail("Make {} tests stand-alone".format(__file__))


# -----------------------------------------------------------------------------
class JcalTest(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_EMPTY(self):
        """
        Nothing to test yet
        """
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
    result = pexpect.run("jcal help")
    exp = "help - show this list"
    assert exp in result

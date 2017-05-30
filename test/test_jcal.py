"""
jcal tests
"""
from bscr import jcal                          # noqa: ignore=F401
import pexpect
from bscr import testhelp as th
from bscr import util as U
import pytest


# -----------------------------------------------------------------------------
def test_jcal_help():
    """
    Verify that 'jcal --help' does the right thing
    """
    result = pexpect.run("jcal help")
    exp = "help - show this list"
    assert exp in result

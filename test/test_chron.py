from bscr import chron
import pexpect
import pytest


# -------------------------------------------------------------------------
def test_hms_seconds():
    """
    Converting %H:%M:%S to an epoch time
    """
    pytest.debug_func()
    exp = 3923
    act = chron.hms_seconds("1:05:23")
    assert exp == act


# -------------------------------------------------------------------------
def test_chron_help():
    """
    Verify that 'chron --help' does the right thing
    """
    pytest.debug_func()
    result = pexpect.run("chron --help")
    assert "Usage: chron" in result
    assert "chronometer/stopwatch" in result

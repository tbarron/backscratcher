"""
Tests for replay
"""
import pexpect
import pytest


# -----------------------------------------------------------------------------
def test_prompt():
    """
    'replay -p CMD' should run CMD and show its output when user hits ENTER
    """
    pytest.debug_func()
    S = pexpect.spawn("replay -p ls")
    S.expect("Hit ENTER...")
    assert "bscr" in S.before
    S.sendline("")
    S.expect("Hit ENTER...")
    S.close()
    pass


# -----------------------------------------------------------------------------
def test_prompt():
    """
    'replay -p CMD' should run CMD and show its output when user hits ENTER
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_change():
    """
    'replay CMD' should display the output of CMD when it changes
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_filepath():
    """
    'replay -t FILENAME CMD' should run CMD when timetamp on FILENAME changes
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_replayNeedsTests():
    """
    Need tests for replay
    """
    pytest.fail("replay needs tests")

"""
Tests for replay
"""
# import pexpect
import pytest


# -----------------------------------------------------------------------------
def test_interval():
    """
    'replay -i 7 CMD' should run CMD and show its output every 7 seconds
    """
    pytest.fail('construction')


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

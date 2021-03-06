"""
This file checks for best practice compliance.
 - Does my code conform to PEP8?
 - Do I have any inadvertent duplicate routines?
 - Do I have routines with no __doc__?

Conveniently, pylint takes care of all of this
"""
import pexpect
import pytest


# -----------------------------------------------------------------------------
def test_pylint():
    """
    Run pylint to check the quality of the code
    """
    # result = pexpect.run("pylint -rn bscr")
    pytest.debug_func()
    result = pexpect.run("flake8 bscr test")
    assert result == ''

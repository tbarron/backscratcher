"""
Tests for pstrack
"""
import os
import pytest

import pexpect

from bscr import pstrack


# -----------------------------------------------------------------------------
def test_get_process_list():
    """
    The dict returned by get_process_list should contain the current process
    and its parent process
    """
    pytest.debug_func()
    procl = pstrack.get_process_list()
    spid = str(os.getpid())
    assert spid in procl
    assert spid == procl[spid]['pid']
    assert str(os.getppid()) == procl[spid]['ppid']


# -----------------------------------------------------------------------------
def test_docopt():
    """
    Check that pstrack.__doc__ contains what docopt requires
    """
    pytest.debug_func()
    reqs = ["Usage:",
            "pstrack [-d] [-v]",
            "Options:",
            "-d          debug",
            "-v          verbose"]
    for strval in reqs:
        assert any([strval in line for line in pstrack.__doc__.split("\n")])


# -----------------------------------------------------------------------------
def test_execution():
    """
    Does pstrack run successfully?
    """
    pytest.debug_func()
    result = pexpect.run('pstrack')
    assert 'Traceback' not in result

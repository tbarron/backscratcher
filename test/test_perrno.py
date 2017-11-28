"""
perrno tests
"""
from bscr import perrno
import pexpect
import pytest


# -----------------------------------------------------------------------------
def test_all(capsys):
    """
    Test 'perrno --all'
    """
    pytest.debug_func()
    perrno.main(["bin/perrno", "--all"])
    result, _ = capsys.readouterr()
    assert "13  EACCES           Permission denied" in result
    assert "['EACCES']" not in result


# -----------------------------------------------------------------------------
def test_mnemonic():
    """
    Calling perrno for a particular error name
    """
    pytest.debug_func()
    result = perrno.etranslate("EBADF")
    assert "    9  EBADF            Bad file descriptor" == result


# -------------------------------------------------------------------------
def test_numeric():
    """
    Calling perrno for a particular error number
    """
    pytest.debug_func()
    result = perrno.etranslate("3")
    assert "    3  ESRCH            No such process" == result


# -------------------------------------------------------------------------
def test_perrno_help():
    """
    Verify that 'perrno --help' does the right thing
    """
    pytest.debug_func()
    exp = ["Usage: perrno {-a|--all|number ...|errname ...}",
           "",
           "    report errno numeric and string values",
           "",
           "Options:",
           "  -h, --help   show this help message and exit",
           "  -a, --all    list all errno values",
           "  -d, --debug  run the debugger",
           ]
    actual = pexpect.run("perrno --help")
    expstr = "\r\n".join(exp) + "\r\n"
    assert expstr == actual

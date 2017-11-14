import bscr
from bscr import util as U
import os
import pytest
import re
import stat
import time


# -----------------------------------------------------------------------------
def test_standalone():
    """
    Make these tests stand-alone
    """
    pytest.fail("Make {} tests stand-alone".format(__file__))


# -----------------------------------------------------------------------------
    """
    """


# -----------------------------------------------------------------------------
    """
    """


# -----------------------------------------------------------------------------
def test_cmdline_help(capsys):
    """
    Test the cmdline class for command line parsing
    """
    pytest.debug_func()
    c = U.cmdline(cmdline_arg_list())
    try:
        c.parse(['cmd', '-h'])
    except SystemExit:
        pass
    o, e = capsys.readouterr()
    assert 'Usage:' in o
    assert '-h, --help     show this help message and exit' in o
    assert '-t, --test     help string' in o
    assert '-s, --special  help string' in o
    assert '-d, --debug    run under the debugger' in o


# -----------------------------------------------------------------------------
def test_cmdline_usage(capsys):
    """
    Test the cmdline class for command line parsing
    """
    pytest.debug_func()
    c = U.cmdline(cmdline_arg_list(), usage="This is a usage test message")
    try:
        c.parse(['cmd', '-h'])
    except SystemExit:
        pass
    o, e = capsys.readouterr()
    assert 'Usage:' in o
    assert 'This is a usage test message' in o
    assert '-h, --help     show this help message and exit' in o
    assert '-t, --test     help string' in o
    assert '-s, --special  help string' in o
    assert '-d, --debug    run under the debugger' in o


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_arg_specified():
    """
    Example argument structure for testing U.cmdline(), specify everything
    """
    clargs = [{'opts': ['-t', '--test'],
               'action': 'store_true',
               'default': False,
               'dest': 'fribble',
               'help': 'help string'
               },
              {'opts': ['-s', '--special'],
               'action': 'store_true',
               'default': False,
               'dest': 'special',
               'help': 'help string'
               }
              ]
    return clargs


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_arg_defaulted():
    """
    Example argument structure for testing U.cmdline(), take lots of defaults
    """
    clargs = [{'name': 'first',
               'help': 'first option'},
              {'name': 'second',
               'action': 'append',
               'help': 'second option'},
              {'name': 'third',
               'default': False,
               'help': 'third option'},
              {'name': 'Fourth',
               'dest': 'forward',
               'help': 'fourth option'},
              ]
    return clargs

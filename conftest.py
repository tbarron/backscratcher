import os
import pdb
import pytest
import time
from bscr.version import __version__


# -----------------------------------------------------------------------------
def pytest_addoption(parser):
    """
    Add the --logpath option to the command line
    """
    parser.addoption("--logpath", action="store", default="",
                     help="where to write a test log")
    parser.addoption("--dbg", action="append", default=[],
                     help="start debugger on test named or ALL")

# -----------------------------------------------------------------------------
def pytest_report_header(config):
    """
    Put marker in the log file to show where the test run started
    """
    
    bscr_writelog(config, "-" * 60)
    return("Backscratcher version %s" % __version__)

# -----------------------------------------------------------------------------
def pytest_unconfigure(config):
    bscr_writelog(config,
                  "passed: %d; FAILED: %d" % (bscr_writelog._passcount,
                                              bscr_writelog._failcount))


# -----------------------------------------------------------------------------
@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    """
    Write a line to the log file for this test
    """
    rep = __multicall__.execute()
    if rep.when != 'call':
        return rep

    if rep.outcome == 'failed':
        status = ">>>>FAIL"
        bscr_writelog._failcount += 1
    else:
        status = "--pass"
        bscr_writelog._passcount += 1

    parent = item.parent
    msg = "%-8s %s:%s.%s" % (status,
                             os.path.basename(parent.fspath.strpath),
                             parent.name,
                             item.name)
    bscr_writelog(item.config, msg)
    return rep


# -----------------------------------------------------------------------------
def bscr_writelog(config, loggable):
    """
    Here's where we actually write to the log file is one was specified
    """
    logpath = config.getoption("logpath")
    if logpath == "":
        return
    f = open(logpath, 'a')
    msg = "%s %s\n" % (time.strftime("%Y.%m%d %H:%M:%S"),
                     loggable)
    f.write(msg)
    f.close()


bscr_writelog._passcount = 0
bscr_writelog._failcount = 0

#!/usr/bin/python
"""
pytool - produce skeletons for python programs

Usage:
    pytool help [COMMAND]
    pytool newdir [-d] PATH
    pytool newpy [-d] PROGRAM
    pytool newtool [-d] PROGRAM PREFIX

---
pytool examples:

    pytool help
        Display this list of command descriptions

    pytool newdir PATH
        Create a python project in PATH

    pytool newpy PROGRAM
        Create a new python program named PROGRAM

    pytool newtool PROGRAM PREFIX
        Create a new python tool-type program based on docopt_dispatch named
        PROGRAM
---

Copyright (C) 1995 - <the end of time>  Tom Barron
  tom.barron@comcast.net
  177 Crossroads Blvd
  Oak Ridge, TN  37830

This software is licensed under the CC-GNU GPL. For the full text of
the license, see http://creativecommons.org/licenses/GPL/2.0/

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
from docopt_dispatch import dispatch
import os
import pdb
import pexpect
import py
import re
import sys

import util as U

BSCR = U.package_module(__name__)


# ---------------------------------------------------------------------------
def main(args=None):
    """
    Where the action starts
    """
    dispatch(__doc__)


# ---------------------------------------------------------------------------
@dispatch.on('help')
def help(**kwa):
    """
    Show the help information from __doc__
    """
    printing = False
    for line in __doc__.split("\n"):
        if printing:
            if line.strip() == "---":
                printing = False
            else:
                print line
        if "examples:" in line:
            print line
            printing = True


# -----------------------------------------------------------------------------
@dispatch.on('newdir', 'PATH')
def pt_newdir(**kwa):
    """newdir - Create a new python project
    """
    if kwa['d']:
        pdb.set_trace()
    root = py.path.local(kwa['PATH'])
    if root.isdir():
        msg = " ".join([root.strpath,
                        "already exists, please remove it first"])
        sys.exit(msg)
    pkgname = root.basename
    root.ensure(dir=True)
    root.join(pkgname).ensure(dir=True)
    root.join('test').ensure(dir=True)

    venv = root.join("venv")
    pexpect.run("virtualenv {}".format(venv.strpath))

    setup = root.join("setup.py")
    setup.write(setup_content_s(pkgname))

    env = root.join(".env")
    env.write(env_content_s(pkgname))

    conftest = root.join("conftest.py")
    conftest.write(conftest_content())
    pass


# ---------------------------------------------------------------------------
@dispatch.on('newpy', 'PROGRAM')
def pt_newpy(**kwa):
    """newpy - Create a new python program

    usage: pytool newpy <program-name>

    Creates executable file <program-name>.py with skeletal
    contents. Run '<program-name>.py -L' to create link <program-name>.
    """
    if kwa['d']:
        pdb.set_trace()
    lname = kwa['PROGRAM']
    pname = lname + '.py'
    are_we_overwriting([lname, '{}.py'.format(pname)])

    basename = U.basename(lname)

    wbl = open(pname, 'w')
    wbl.writelines(["#!/usr/bin/env python\n",
                    "\"\"\"\n",
                    "%s - program description\n" % basename,
                    "\"\"\"\n",
                    "\n",
                    "import optparse\n",
                    "import pdb\n",
                    "import sys\n",
                    "from bscr import toolframe\n",
                    "import unittest\n",
                    "\n",
                    "def main(argv = None):\n",
                    "    if argv == None:\n",
                    "        argv = sys.argv\n",
                    "\n",
                    "    prs = optparse.OptionParser()\n",
                    "    prs.add_option('-d', '--debug',\n",
                    "                   action='store_true', "
                    "default=False,\n",
                    "                   dest='debug',\n",
                    "                   help='run the debugger')\n",
                    "    (opts, args) = prs.parse_args(argv)\n",
                    "\n",
                    "    if opts.debug:\n",
                    "        pdb.set_trace()",
                    "\n",
                    "\n",
                    "    # process arguments\n",
                    "    for arg in args:\n",
                    "        process(arg)\n",
                    "\n",
                    "class %sTest(unittest.TestCase):\n"
                    % basename.capitalize(),
                    "    def test_example(self):\n",
                    "        pass\n",
                    "\n",
                    "toolframe.ez_launch(__name__, main)\n"])
    wbl.close()

    os.chmod(pname, 0755)
    os.symlink(os.path.abspath(pname), lname)


# ---------------------------------------------------------------------------
@dispatch.on('newtool', 'PROGRAM', 'PREFIX')
def pt_newtool(**kwa):
    """newtool - Create a new tool-style program

    usage: pytool newtool <program-name> <prefix>

    Creates executable file <program-name>.py with skeletal
    contents. The structure of the program is such that it is easy
    to add and describe new subfunctions.
    """
    lname = kwa["PROGRAM"]
    pname = lname + '.py'
    prefix = kwa["PREFIX"]
    are_we_overwriting([lname, pname])

    basename = U.basename(lname)
    wbl = open(pname, 'w')
    wbl.writelines(["#!/usr/bin/env python\n",
                    "\"\"\"\n",
                    "{} - program description\n".format(basename),
                    "\"\"\"\n",
                    "\n",
                    "from bscr import util as U\n",
                    "import optparse\n",
                    "import os\n",
                    "import re\n",
                    "import sys\n",
                    "\n",
                    "# ---------------------------------------"
                    "------------------------------------\n",
                    "def {}_example(argv):\n".format(prefix),
                    "    print('this is an example')\n",
                    "\n",
                    "# ---------------------------------------"
                    "------------------------------------\n",
                    "if __name__ == '__main__':\n",
                    "    U.dispatch('__main__',"
                    " '{}', sys.argv)".format(prefix)])
    wbl.close()

    os.chmod(pname, 0755)
    os.symlink(os.path.abspath(pname), lname)


# ---------------------------------------------------------------------------
def are_we_overwriting(flist):
    """
    Check for whether we are overwriting the program or creating it new
    """
    already = []
    for filename in flist:
        if os.path.exists(filename):
            already.append(filename)

    if len(already) < 1:
        return
    elif len(already) < 2:
        report = '%s already exists' % already[0]
    elif len(already) < 3:
        report = '%s and %s already exist' % (already[0], already[1])
    else:
        report = ', '.join(already)

        sep = ', and '
        for item in already:
            report = sep + item + report
            sep = ', '
        report = report[2:]

    answer = raw_input('%s. Are you sure? > ' % report)

    if not re.search(r'^\s*[Yy]', answer):
        sys.exit(1)

    U.safe_unlink(already)


# ---------------------------------------------------------------------------
def conftest_content():
    """
    Generate the standard content for conftest.py
    """
    txt = """
import os
import pdb
import pytest
import time
from bscr.version import __version__


# -----------------------------------------------------------------------------
def pytest_addoption(parser):
    \"\"\"
    Add the --logpath option to the command line
    \"\"\"
    parser.addoption(\"--skip\", action=\"append\", default=[],
                     help=\"don't run the named test(s)\")
    parser.addoption(\"--logpath\", action=\"store\", default=\"\",
                     help=\"where to write a test log\")
    parser.addoption(\"--dbg\", action=\"append\", default=[],
                     help=\"start debugger on test named or ALL\")
    parser.addoption(\"--all\", action=\"store_true\", default=False,
                     help=\"start debugger on test named or ALL\")


# -----------------------------------------------------------------------------
def pytest_report_header(config):
    \"\"\"
    Put marker in the log file to show where the test run started
    \"\"\"

    pytest_writelog(config, \"-\" * 60)
    return(\"Package version %s\" % __version__)


# -----------------------------------------------------------------------------
def pytest_configure(config):
    \"\"\"
    If --all, turn off --exitfirst
    \"\"\"
    # pdb.set_trace()
    if config.getoption(\"--all\"):
        config.option.__dict__['exitfirst'] = False
        config.option.__dict__['maxfail'] = 2000


# -----------------------------------------------------------------------------
def pytest_runtest_setup(item):
    \"\"\"
    For each test, just before it runs...
    \"\"\"
    skipl = item.config.getoption(\"--skip\")
    if any([item.name in skipl,
            any([_ in item.name for _ in skipl])]):
        pytest.skip()
    if any([item.name in item.config.getoption(\"--dbg\"),
            'all' in item.config.getoption(\"--dbg\")] +
           [_ in item.name for _ in item.config.getoption('--dbg')]):
        pytest.debug_func = pdb.set_trace
    else:
        pytest.debug_func = lambda: None


# -----------------------------------------------------------------------------
def pytest_unconfigure(config):
    \"\"\"
    At the end of the run, log a summary
    \"\"\"
    pytest_writelog(config,
                    \"passed: %d; FAILED: %d\" % (pytest_writelog._passcount,
                                                  pytest_writelog._failcount))


# -----------------------------------------------------------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    \"\"\"
    Write a line to the log file for this test
    \"\"\"
    ctx = yield
    rep = ctx.result
    if rep.when != 'call':
        return

    if rep.outcome == 'failed':
        status = \">>>>FAIL\"
        pytest_writelog._failcount += 1
    elif rep.outcome == 'passed':
        status = \"--pass\"
        pytest_writelog._passcount += 1
    elif rep.outcome == 'skipped':
        status = '**skip'
    else:
        status = 'other '

    parent = item.parent
    msg = \"%-8s %s:%s.%s\" % (status,
                             os.path.basename(parent.fspath.strpath),
                             parent.name,
                             item.name)
    pytest_writelog(item.config, msg)


# -----------------------------------------------------------------------------
def pytest_writelog(config, loggable):
    \"\"\"
    Here's where we actually write to the log file is one was specified
    \"\"\"
    logpath = config.getoption(\"logpath\")
    if logpath == \"\":
        return
    f = open(logpath, 'a')
    msg = \"%s %s\n\" % (time.strftime(\"%Y.%m%d %H:%M:%S\"),
                     loggable)
    f.write(msg)
    f.close()


pytest_writelog._passcount = 0
pytest_writelog._failcount = 0
    """
    return txt


# -----------------------------------------------------------------------------
def env_content_s(pkgname):
    """
    Return the correct content for .env
    """
    txt = [
        "export PKG=\"{}\"".format(pkgname),
        "source venv/bin/activate",
        "function chpwd() {",
        "    deactivate",
        "    unset -f chpwd",
        "}",
        "",
        "export PTMP=/private/var/folders/4g/xhhsjk953jd8sqnvqq3fhxsc0000gp"
        "/T/pytest-of-tbarron/pytest-tbarron"
        ]
    return "\n".join(txt) + "\n"


# -----------------------------------------------------------------------------
def setup_content_s(pkgname):
    """
    Return the correct content for setup.py
    """
    txt = [
        "from setuptools import setup",
        "",
        "setup(name='{}',".format(pkgname),
        "    packages=['{}']".format(pkgname),
        ")"
        ]
    return "\n".join(txt) + "\n"

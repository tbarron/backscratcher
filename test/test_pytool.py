import os
import pdb
import shutil
import sys

import pexpect
import pytest

from bscr import pytool
from bscr import testhelp as th
from bscr import util as U

# -----------------------------------------------------------------------
def test_newpy_nothing():
    """
    Run 'pytool newpy' with no other arguments. Should produce pytool's
    'Usage:' message.
    """
    result = pexpect.run("pytool newpy")
    for exp in ["Usage:",
                "pytool help [COMMAND]",
                "pytool newpy PROGRAM",
                "pytool newtool PROGRAM"]:
        assert exp in result


# -----------------------------------------------------------------------------
def test_newpy_prog_dir(tmpdir, fx_nopred):
    """
    Run 'pytool.pt_newpy(**{'newpy': True, 'PROGRAM': 'xyzzy'})'. Verify that
    xyzzy and xyzzy.py are created and have the right contents.
    """
    pytest.debug_func()
    pytool.pt_newpy(**{"newpy": True, "PROGRAM": "xyzzy"})

    assert os.path.exists(fx_nopred.pname)
    exp = os.path.abspath(fx_nopred.pname)
    act = os.readlink(fx_nopred.lname)
    assert exp == act

    got = U.contents(fx_nopred.pname)
    exp = expected_xyzzy_py()
    assert exp == got


# -----------------------------------------------------------------------------
def test_newpy_prog_pxr(tmpdir, fx_nopred):
    """
    Run 'pytool newpy xyzzy'. Verify that xyzzy and xyzzy.py are created
    and have the right contents.
    """
    pytest.debug_func()
    r = pexpect.run("pytool newpy {}".format(fx_nopred.lname))

    assert os.path.exists(fx_nopred.pname)
    exp = os.path.abspath(fx_nopred.pname)
    act = os.readlink(fx_nopred.lname)
    assert exp == act

    got = U.contents(fx_nopred.pname)
    exp = expected_xyzzy_py()
    assert exp == got


            self.assertEqual(exp, got,
                             "\nExpected '%s',\n     got '%s'" %
                             (exp, got))

                    '',
                    'import optparse',
                    'import pdb',
                    'import sys',
                    'from bscr import toolframe',
                    'import unittest',
                    '',
                    'def main(argv = None):',
                    '    if argv == None:',
                    '        argv = sys.argv',
                    '',
                    '    prs = optparse.OptionParser()',
                    "    prs.add_option('-d', '--debug',",
                    "                   action='store_true', default=False,",
                    "                   dest='debug',",
                    "                   help='run the debugger')",
                    '    (opts, args) = prs.parse_args(argv)',
                    "",
                    "    if opts.debug:",
                    "        pdb.set_trace()",
                    '',
                    '    # process arguments',
                    '    for arg in args:',
                    '        process(arg)',
                    '',
                    'class XyzzyTest(unittest.TestCase):',
                    '    def test_example(self):',
                    '        pass',
                    '',
                    'toolframe.ez_launch(__name__, main)', ]

        return expected

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


# -----------------------------------------------------------------------------
def test_newpy_overwriting_no(tmpdir):
    """
    Run 'pytool newpy xyzzy' when xyzzy already exists. Verify
    that confirmation is requested. Answer 'no' and verify that
    the existing file is not overwritten.
    """
    xyzzy = testfile(tmpdir, "xyzzy", content="original xyzzy\n")
    xyzzy_py = testfile(tmpdir, "xyzzy.py", content="original xyzzy.py\n")
    with U.Chdir(tmpdir.strpath):
        cmd = pexpect.which("pytool")
        S = pexpect.spawn("{} newpy xyzzy".format(cmd))
        which = S.expect([r'you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
        elif which == 1:
            print S.before + S.after
            pytest.fail('unexpected exception')
        else:
            pytest.fail('should have asked about overwriting xyzzy')

        expected = ['original xyzzy']
        got = U.contents(xyzzy.strpath)
        assert(expected == got)

        expected = ['original xyzzy.py']
        got = U.contents(xyzzy_py.strpath)
        assert(expected == got)


# -----------------------------------------------------------------------------
def test_newpy_overwriting_yes(tmpdir):
    """
    Run 'pytool newpy xyzzy' when xyzzy, xyzzy.py already exist.
    Verify that confirmation is requested. Answer 'yes' and verify
    that the existing file IS overwritten.
    """
    xyzzy = testfile(tmpdir, "xyzzy", content="original xyzzy")
    xyzzy_py = testfile(tmpdir, "xyzzy.py", content="original xyzzy.py")
    with U.Chdir(tmpdir.strpath):
        cmd = pexpect.which('pytool')
        S = pexpect.spawn('%s newpy %s' % (cmd, xyzzy.strpath))
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('yes')
            S.expect(pexpect.EOF)
        elif which == 1:
            print S.before + S.after
            pytest.fail('unexpected exception')
        else:
            pytest.fail('should have asked about overwriting xyzzy')

        exp = os.path.abspath(xyzzy_py.strpath)
        got = os.readlink(xyzzy.strpath)
        assert exp == got

        expected = expected_xyzzy_py()
        got = U.contents(xyzzy_py.strpath)
        assert expected == got


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

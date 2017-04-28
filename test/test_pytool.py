import os

import pexpect
import pytest

from bscr import pytool
from bscr import util as U


# -----------------------------------------------------------------------------
def test_newpy_nothing():
    """
    Run 'pytool newpy' with no other arguments. Should produce pytool's
    'Usage:' message.
    """
    result = pexpect.run("pytool newpy")
    for exp in ["Usage:",
                "pytool help [COMMAND]",
                "pytool newpy [-d] PROGRAM",
                "pytool newtool [-d] PROGRAM"]:
        assert exp in result


# -----------------------------------------------------------------------------
def test_newpy_prog_dir(tmpdir, fx_nopred):
    """
    Run 'pytool.pt_newpy(**{'newpy': True, 'PROGRAM': 'xyzzy'})'. Verify that
    xyzzy and xyzzy.py are created and have the right contents.
    """
    pytest.debug_func()
    pytool.pt_newpy(**{"newpy": True, "PROGRAM": "xyzzy", "d": False})

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
    assert r == ""

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
    xyzzy = toyfile(tmpdir, "xyzzy", content="original xyzzy\n")
    xyzzy_py = toyfile(tmpdir, "xyzzy.py", content="original xyzzy.py\n")
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
    xyzzy = toyfile(tmpdir, "xyzzy", content="original xyzzy")
    xyzzy_py = toyfile(tmpdir, "xyzzy.py", content="original xyzzy.py")
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


# -----------------------------------------------------------------------------
def test_newtool(tmpdir):
    """
    Run 'pytool newtool testtool' while testtool.py does not exist.
    Verify that testtool.py is created and has the right contents.
    """
    pytest.debug_func()
    toolname = toyfile(tmpdir, "testtool.py")
    toollink = toyfile(tmpdir, "testtool")
    with U.Chdir(tmpdir.strpath):
        cmd = pexpect.which("pytool")
        if cmd is None:
            pytest.skip("pytool not found")
        S = pexpect.spawn("{} newtool {} tt".format(cmd, toollink.strpath))
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
            pytest.fail('should not have asked about overwriting')
        elif which == 1:
            print S.before + S.after
            pytest.fail('unexpected exception')

        assert toolname.strpath == toollink.readlink()

        expected = expected_testtool_py()
        got = toolname.read().split("\n")
        assert expected == got


# -----------------------------------------------------------------------------
def test_newtool_overwriting_no(tmpdir):
    """
    Run 'pytool newtool testtool tt' while testtool.py does exist. Verify
    that we are prompted about overwriting. Answer 'no' and verify that the
    original file is not overwritten.
    """
    pytest.debug_func()
    tname = toyfile(tmpdir, "testtool.py", content=["original testtool.py"])
    tlink = toyfile(tmpdir, "testtool", content=["original testtool"])
    with U.Chdir(tmpdir.strpath):
        cmd = pexpect.which("pytool")
        if cmd is None:
            pytest.skip("pytool not found")
        S = pexpect.spawn("{} newtool {} tt".format(cmd, tlink))
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
        elif which == 1:
            print S.before + S.after
            pytest.fail('unexpected exception')
        else:
            pytest.fail("should have asked about overwriting {}".format(tname))

        for fname in [tlink, tname]:
            exp = "original %s" % fname.basename
            got = fname.read()
            assert exp == got


# -----------------------------------------------------------------------------
def test_newtool_overwriting_yes(tmpdir):
    """
    Run 'pytool newtool testtool tt' while testtool.py exists. Verify that
    we are prompted about overwriting. Answer 'yes' and verify that the
    original file is overwritten.
    """
    pytest.debug_func()
    tname = toyfile(tmpdir, "testtool.py", content=["original testtool.py"])
    tlink = toyfile(tmpdir, "testtool", content=["original testtool"])
    with U.Chdir(tmpdir.strpath):
        cmd = pexpect.which("pytool")
        if cmd is None:
            pytest.skip("pytool not found")
        S = pexpect.spawn("{} newtool {} tt".format(cmd, tlink))
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
            pytest.fail("should have asked about overwriting {}".format(tname))

        exp = tname.strpath
        actual = tlink.readlink()
        assert exp == actual

        expected = expected_testtool_py()
        got = tname.read().split("\n")
        assert expected == got


# -----------------------------------------------------------------------------
def test_help(tmpdir):
    """
    Run 'pytool help'. Verify that the output is correct
    """
    with U.Chdir(tmpdir.strpath):
        outputs = ["testtool", "testtool.py", "xyzzy", "xyzzy.py"]
        U.safe_unlink(outputs)
        cmd = pexpect.which("pytool")
        S = pexpect.spawn("{} help".format(cmd))
        which = S.expect([r"Are you sure\? >",
                          "Error:",
                          pexpect.EOF])
        if which == 0:
            S.sendline("no")
            S.expect(pexpect.EOF)
            pytest.fail("should not have asked about overwriting")
        elif which == 1:
            print S.before + S.after
            pytest.fail("unexpected exception")

        for file in outputs:
            assert(not os.path.exists(file))


# -----------------------------------------------------------------------------
def test_help_newpy(tmpdir):
    """
    Run 'pytool help newpy'. Verify that the output is correct.
    """
    with U.Chdir(tmpdir.strpath):
        cmd = pexpect.which("pytool")
        S = pexpect.spawn("{} help newpy".format(cmd))
        which = S.expect([r"Are you sure\? >",
                          "Error:",
                          pexpect.EOF])
        if which == 0:
            S.sendline("no")
            S.expect(pexpect.EOF)
            pytest.fail("should not have asked about overwriting")
        elif which == 1:
            print S.before + S.after
            pytest.fail("unexpected exception")

        got = S.before.split("\r\n")
        exp = expected_help()
        assert exp == got


# -----------------------------------------------------------------------------
def test_help_newtool(tmpdir):
    """
    Run 'pytool help newtool'. Verify that the output is correct.
    """
    with U.Chdir(tmpdir.strpath):
        cmd = pexpect.which("pytool")
        S = pexpect.spawn("{} help newtool".format(cmd))
        which = S.expect([r"Are you sure\? >",
                          "Error:",
                          pexpect.EOF])
    if which == 0:
        S.sendline("no")
        S.expect(pexpect.EOF)
        pytest.fail("should not have asked about overwriting")
    elif which == 1:
        print S.before + S.after
        pytest.fail("unexpected exception")

    got = S.before.split("\r\n")
    exp = expected_help()
    assert exp == got


# -------------------------------------------------------------------------------
def expected_testtool_py():
    """
    The expected output of a new tool request
    """
    expected = ["#!/usr/bin/env python",
                "\"\"\"",
                "testtool - program description",
                "\"\"\"",
                "",
                "from bscr import util as U",
                "import optparse",
                "import os",
                "import re",
                "import sys",
                "",
                "# ----------------------------------------------------"
                + "-----------------------",
                "def tt_example(argv):",
                "    print('this is an example')",
                "",
                "# ----------------------------------------------------"
                + "-----------------------",
                "if __name__ == '__main__':",
                "    U.dispatch('__main__', 'tt', sys.argv)"]

    return expected


# -----------------------------------------------------------------------------
def expected_xyzzy_py():
    """
    The expected output of a new py request
    """
    expected = ["#!/usr/bin/env python",
                "\"\"\"",
                "xyzzy - program description",
                "\"\"\"",
                "",
                "import optparse",
                "import pdb",
                "import sys",
                "from bscr import toolframe",
                "import unittest",
                "",
                "def main(argv = None):",
                "    if argv == None:",
                "        argv = sys.argv",
                "",
                "    prs = optparse.OptionParser()",
                "    prs.add_option('-d', '--debug',",
                "                   action='store_true', default=False,",
                "                   dest='debug',",
                "                   help='run the debugger')",
                "    (opts, args) = prs.parse_args(argv)",
                "",
                "    if opts.debug:",
                "        pdb.set_trace()",
                "",
                "    # process arguments",
                "    for arg in args:",
                "        process(arg)",
                "",
                "class XyzzyTest(unittest.TestCase):",
                "    def test_example(self):",
                "        pass",
                "",
                "toolframe.ez_launch(__name__, main)"]

    return expected


# -----------------------------------------------------------------------------
def expected_help():
    """
    The expected output of 'pytool help'
    """
    expected = ["pytool examples:",
                "",
                "    pytool help",
                "        Display this list of command descriptions",
                "",
                "    pytool newpy PROGRAM",
                "        Create a new python program named PROGRAM",
                "",
                "    pytool newtool PROGRAM PREFIX",
                "        Create a new python tool-type program based on "
                "docopt_dispatch named",
                "        PROGRAM",
                "",
                ]
    return expected


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_nopred(tmpdir):
    """
    Fixture for newpy test with no predecessor to the new program
    """
    with U.Chdir(tmpdir.strpath):
        fx_nopred.lname = 'xyzzy'
        fx_nopred.pname = fx_nopred.lname + '.py'
        assert not os.path.exists(fx_nopred.lname)
        assert not os.path.exists(fx_nopred.pname)

        yield fx_nopred


# -----------------------------------------------------------------------------
def toyfile(where, name, exists=False, content=None):
    """
    Create a thing for a test to play with. Verify where.strpath/name does not
    exist. If *exists*, create it. If *content* != None, put content in it.
    Return the py.path.local object.
    """
    rval = where.join(name)
    assert not rval.exists()
    if exists:
        rval.ensure()
    if content:
        if isinstance(content, str):
            rval.write(content)
        elif isinstance(content, list):
            rval.write(''.join(content))
        else:
            rval.write(str(content))
    return rval

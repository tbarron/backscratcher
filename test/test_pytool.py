import os

import pexpect
import pytest

from bscr import pytool
from bscr import util as U


# -----------------------------------------------------------------------------
def test_newdir(tmpdir, fx_ndexp):
    """
    Verify that 'pytool newdir ...' does the right thing
    """
    pytest.debug_func()
    root = fx_ndexp[0]["arg"]
    cmd = "pytool newdir {}".format(root.strpath)
    pexpect.run(cmd)
    for item in fx_ndexp:
        item["op"](item["arg"])


# -----------------------------------------------------------------------------
def test_newdir_already(tmpdir, fx_ndexp):
    """
    If the target directory already exists, exit with an error
    """
    pytest.debug_func()
    root = fx_ndexp[0]["arg"]
    root.ensure(dir=True)
    result = pexpect.run("pytool newdir {}".format(root.strpath))
    msg = "{} already exists, please remove it first".format(root.strpath)
    assert msg in result
    for item in fx_ndexp[1:]:
        assert not item["arg"].exists()


# -----------------------------------------------------------------------------
def test_newdir_noarg(tmpdir, fx_ndexp):
    """
    Verify that 'pytool newdir' with no argument produces a help message
    """
    pytest.debug_func()
    result = pexpect.run("pytool newdir")
    assert "Usage:" in result
    assert "pytool newdir [-d] PATH" in result


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
                "    pytool newdir PATH",
                "        Create a python project in PATH",
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
@pytest.fixture
def fx_ndexp(request, tmpdir):
    """
    Set up a structure to hold expected data for a newdir test
    """
    testname = request._pyfuncitem.name
    cmdl = []
    root = tmpdir.join(testname)
    cmdl.append({"op": vfy_dir, "arg": root})
    cmdl.append({"op": vfy_dir, "arg": root.join("test")})
    cmdl.append({"op": vfy_dir, "arg": root.join("venv")})
    cmdl.append({"op": vfy_file, "arg": root.join("venv/bin/activate")})
    cmdl.append({"op": vfy_setup, "arg": root.join("setup.py")})
    cmdl.append({"op": vfy_env, "arg": root.join(".env")})
    cmdl.append({"op": vfy_conftest, "arg": root.join("conftest.py")})
    return cmdl


# -----------------------------------------------------------------------------
def vfy_conftest(pathobj):
    """
    Check that pathobj represents the conftest.py we want
    """
    assert pathobj.isfile()
    assert "pytest_configure" in pathobj.read()
    assert "pytest.debug_func" in pathobj.read()


# -----------------------------------------------------------------------------
def vfy_dir(pathobj):
    """
    Check that pathobj represents a directory
    """
    assert pathobj.isdir()


# -----------------------------------------------------------------------------
def vfy_env(pathobj):
    """
    Check that pathobj represents a directory
    """
    assert pathobj.isfile()
    pkgname = os.path.basename(pathobj.dirname)
    assert "export PKG=\"{}\"".format(pkgname) in pathobj.read()
    assert "source venv/bin/activate" in pathobj.read()
    assert "export PTMP=" in pathobj.read()


# -----------------------------------------------------------------------------
def vfy_file(pathobj):
    """
    Check that pathobj represents a file
    """
    assert pathobj.isfile()


# -----------------------------------------------------------------------------
def vfy_setup(pathobj):
    """
    Check that pathobj represents the setup.py we want
    """
    assert pathobj.isfile()
    nub = os.path.basename(pathobj.dirname)
    assert "setup(name='{}'".format(nub) in pathobj.read()
    assert "from setuptools import setup" in pathobj.read()


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

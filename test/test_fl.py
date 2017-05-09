#!/usr/bin/env python
from bscr import fl
from bscr import util
import os
import pexpect
import py
import pytest
import random
import re
import shutil
import stat
import tempfile
from bscr import testhelp as th
import time
from bscr import util as U


# -----------------------------------------------------------------------------
def test_amtime_atom_dir(tmpdir):
    """
    Test fl_set_atime_to_mtime()
    """
    pytest.debug_func()
    atime = int(time.time() - random.randint(1000, 2000))
    mtime = int(time.time() + random.randint(1000, 2000))
    atom = makefile(tmpdir, "atom", content="This is the test file",
                    atime=atime, mtime=mtime)
    fl.fl_set_atime_to_mtime(**{"FILE": [atom.strpath], "d": False})
    s = os.stat(atom.strpath)
    assert mtime == s[stat.ST_MTIME]
    assert mtime == s[stat.ST_ATIME]
    assert s[stat.ST_ATIME] == s[stat.ST_MTIME]


# -----------------------------------------------------------------------------
def test_amtime_atom_pxr(tmpdir):
    """
    Test fl_set_atime_to_mtime()
    """
    pytest.debug_func()
    atime = int(time.time() - random.randint(1000, 2000))
    mtime = int(time.time() + random.randint(1000, 2000))
    atom = makefile(tmpdir, "atom", content="This is the test file",
                    atime=atime, mtime=mtime)
    result = pexpect.run("fl set_atime_to_mtime {}".format(atom.strpath))
    assert result == ""
    s = os.stat(atom.strpath)
    assert mtime == s[stat.ST_MTIME]
    assert mtime == s[stat.ST_ATIME]
    assert s[stat.ST_ATIME] == s[stat.ST_MTIME]


# -----------------------------------------------------------------------------
def test_amtime_mtoa_dir(tmpdir):
    """
    Test fl_set_mtime_to_atime()
    """
    atime = int(time.time() - random.randint(1000, 2000))
    mtime = int(time.time() + random.randint(1000, 2000))
    atom = makefile(tmpdir, "mtoa", content="This is the test file",
                    atime=atime, mtime=mtime)
    fl.fl_set_mtime_to_atime(**{"FILE": [atom.strpath], "d": False})
    s = os.stat(atom.strpath)
    assert s[stat.ST_ATIME] == atime
    assert s[stat.ST_MTIME] == atime
    assert s[stat.ST_ATIME] == s[stat.ST_MTIME]


# -----------------------------------------------------------------------------
def test_amtime_mtoa_pxr(tmpdir):
    """
    Test fl_set_mtime_to_atime()
    """
    atime = int(time.time() - random.randint(1000, 2000))
    mtime = int(time.time() + random.randint(1000, 2000))
    atom = makefile(tmpdir, "mtoa", content="This is the test file",
                    atime=atime, mtime=mtime)
    result = pexpect.run("fl set_mtime_to_atime {}".format(atom.strpath))
    s = os.stat(atom.strpath)
    assert result == ""
    assert s[stat.ST_ATIME] == atime
    assert s[stat.ST_MTIME] == atime
    assert s[stat.ST_ATIME] == s[stat.ST_MTIME]


# -----------------------------------------------------------------------------
def test_command_line():
    """
    Running the command with no arguments should get help output
    """
    thisone = util.script_location("fl")

    result = pexpect.run(thisone)
    assert "Traceback" not in result
    assert "diff" in result
    assert "save" in result
    assert "times" in result


# -----------------------------------------------------------------------------
def test_diff_match_dir(tmpdir, capsys, fx_match):
    """
    Test fl.fl_diff(**{'d': False, 'FILE': filename}) when a prefix match
    exists
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        fl.fl_diff(**{"d": False, "n": False,
                      "FILE": [fx_match.mrpm1.basename]})
        got, _ = capsys.readouterr()
        assert fx_match.mrpm1_diff_exp == got.split("\n")

        fl.fl_diff(**{"d": False, "n": False, "FILE": ["mrpm2"]})
        got, _ = capsys.readouterr()
        assert "\n".join(fx_match.mrpm2_diff_exp) == got


# -----------------------------------------------------------------------------
def test_diff_match_pxr(tmpdir, fx_match):
    """
    Test 'fl diff FILENAME' when a prefix match exists
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        cmd = "{} diff {}".format(U.script_location("fl"),
                                  fx_match.mrpm1.basename)
        got = pexpect.run(cmd).split("\n")
        assert fx_match.mrpm1_diff_exp == [_.rstrip() for _ in got]

        cmd = "{} diff {}".format(U.script_location("fl"),
                                  fx_match.mrpm2.basename)
        got = pexpect.run(cmd).split("\n")
        assert fx_match.mrpm2_diff_exp == [_.rstrip() for _ in got]


# -----------------------------------------------------------------------------
def test_diff_nomatch_dir(tmpdir, capsys):
    """
    Test fl.fl_diff(**{'d': False, 'FILE': [nomatch]}) when no prefix match
    exists
    """
    pytest.debug_func()
    nomatch = makefile(tmpdir, "nomatch", ensure=True)
    with U.Chdir(tmpdir.strpath):
        fl.fl_diff(**{"d": False, "FILE": [nomatch.basename]})
        exp = "No prefix match found for nomatch\n"
        got, _ = capsys.readouterr()
        assert exp == got


# -----------------------------------------------------------------------------
def test_diff_nomatch_pxr(tmpdir):
    """
    Test pexpect.run('fl diff nomatch') where there's no prefix match for the
    file
    """
    pytest.debug_func()
    nomatch = makefile(tmpdir, "nomatch", ensure=True)
    with U.Chdir(tmpdir.strpath):
        cmd = "fl diff {}".format(nomatch.basename)
        result = pexpect.run(cmd)
        exp = "No prefix match found for nomatch\r\n"
        assert exp == result


# -----------------------------------------------------------------------------
def test_editfile_delete(tmpdir, fx_edit):
    """
    fl.editfile('legit', 's', 'foo', '', None)
    """
    pytest.debug_func()
    xdata = [re.sub('^foo', '', z) for z in fx_edit.tdata]
    fx_edit.fp.write("\n".join(fx_edit.tdata))

    fl.editfile(fx_edit.fp.strpath, 's', '^foo', '', None)

    assert fx_edit.fp.exists()
    assert fx_edit.forig.exists()
    assert "\n".join(xdata) == fx_edit.fp.read()
    assert "\n".join(fx_edit.tdata) == fx_edit.forig.read()


# -----------------------------------------------------------------------------
def test_editfile_empty(tmpdir, fx_edit):
    """
    fl.editfile('emptyfile', 's', 'foo', 'bar', None)
    => rename emptyfile emptyfile.original, both empty
    """
    pytest.debug_func()
    fx_edit.fp.ensure()

    fl.editfile(fx_edit.fp.strpath, 's', 'foo', 'bar', None)

    assert fx_edit.fp.exists()
    assert fx_edit.forig.exists()
    assert "" == fx_edit.fp.read()
    assert "" == fx_edit.forig.read()


# -----------------------------------------------------------------------------
def test_editfile_legit(tmpdir, fx_edit):
    """
    fl.editfile('legit', 's', 'foo', 'bar', None)
    """
    pytest.debug_func()
    xdata = [z.replace('foo', 'bar') for z in fx_edit.tdata]
    fx_edit.fp.write("\n".join(fx_edit.tdata))

    fl.editfile(fx_edit.fp.strpath, 's', 'foo', 'bar', None)

    assert fx_edit.fp.exists()
    assert fx_edit.forig.exists()
    assert "\n".join(xdata) == fx_edit.fp.read()
    assert "\n".join(fx_edit.tdata) == fx_edit.forig.read()


# -----------------------------------------------------------------------------
def test_editfile_nosuch(tmpdir, fx_edit):
    """
    fl.editfile('nosuchfile', 'foo', 'bar', None)
    => should throw an exception
    """
    with pytest.raises(IOError) as err:
        fl.editfile(fx_edit.fp.strpath, 's', 'foo', 'bar', None)
    exp = "No such file or directory: '{}'".format(fx_edit.fp.strpath)
    assert exp in str(err)


# -----------------------------------------------------------------------------
def test_editfile_rgx(tmpdir, fx_edit):
    """
    fl.editfile('legit', 's', 'foo', 'bar', None)
    """
    xdata = [re.sub('^foo', 'bar', z) for z in fx_edit.tdata]
    fx_edit.fp.write("\n".join(fx_edit.tdata))

    fl.editfile(fx_edit.fp.strpath, 's', '^foo', 'bar', None)

    assert fx_edit.fp.exists()
    assert fx_edit.forig.exists()
    assert "\n".join(xdata) == fx_edit.fp.read()
    assert "\n".join(fx_edit.tdata) == fx_edit.forig.read()


# -----------------------------------------------------------------------------
def test_editfile_suffix(tmpdir, fx_edit):
    """
    fl.editfile('legit', 's', 'foo', 'bar', 'old')
    """
    fold = tmpdir.join(fx_edit.fp.basename + ".old")
    xdata = [z.replace('foo', 'bar') for z in fx_edit.tdata]
    fx_edit.fp.write("\n".join(fx_edit.tdata))

    fl.editfile(fx_edit.fp.strpath, 's', 'foo', 'bar', 'old')

    assert fx_edit.fp.exists()
    assert fold.exists()
    assert not fx_edit.forig.exists()
    assert "\n".join(xdata) == fx_edit.fp.read()
    assert "\n".join(fx_edit.tdata) == fold.read()


# -----------------------------------------------------------------------------
def test_fl_help_pxr():
    """
    'fl help' should get help output
    """
    cmd = util.script_location("fl")
    result = pexpect.run('{} help'.format(cmd))
    assert "Traceback" not in result
    for f in [x for x in dir(fl) if x.startswith('bscr_')]:
        subc = f.replace('bscr_', '')
        assert "{} - ".format(subc) in result


# -----------------------------------------------------------------------------
def test_mrpm_cwd_hit(tmpdir):
    """
    Test for most_recent_prefix_match() with no matches in the current
    directory
    """
    pytest.debug_func()
    testfile = makefile(tmpdir, "mrpm", ensure=True)
    match = makefile(tmpdir, "mrpm.2009.0217", ensure=True)
    result = fl.most_recent_prefix_match(tmpdir.strpath, testfile.basename)
    assert result == match.strpath


# -----------------------------------------------------------------------------
def test_mrpm_cwd_none(tmpdir):
    """
    Test for most_recent_prefix_match() with no matches in the current
    directory
    """
    pytest.debug_func()
    testfile = makefile(tmpdir, "mrpm", ensure=True)
    result = fl.most_recent_prefix_match(tmpdir.strpath, testfile.basename)
    assert result is None


# -----------------------------------------------------------------------------
def test_mrpm_cwd_nosuch_hit(tmpdir):
    """
    Test for most_recent_prefix_match() with non-existent stem file but a valid
    match in the current directory
    """
    pytest.debug_func()
    testfile = tmpdir.join("mrpm")
    mfile = makefile(tmpdir, "mrpm.suffix", content="This is the backup")
    result = fl.most_recent_prefix_match(tmpdir.strpath, testfile.basename)
    assert result == mfile.strpath


# -----------------------------------------------------------------------------
def test_mrpm_cwd_nosuch_none(tmpdir):
    """
    Test for most_recent_prefix_match() with non-existent stem file and no
    matches in the current directory
    """
    pytest.debug_func()
    testfile = tmpdir.join("mrpm")
    result = fl.most_recent_prefix_match(tmpdir.strpath, testfile.basename)
    assert result is None


# -----------------------------------------------------------------------------
def test_mrpm_old_hit(tmpdir):
    """
    Test for most_recent_prefix_match() with a ./old directory and no matches
    in . or ./old
    """
    pytest.debug_func()
    olddir = makefile(tmpdir, "old", ensure=True, dir=True)
    testfile = makefile(tmpdir, "mrpm", ensure=True)
    match = makefile(olddir, "mrpm.abc.def", ensure=True)
    result = fl.most_recent_prefix_match(tmpdir.strpath, testfile.basename)
    assert result == match.strpath


# -----------------------------------------------------------------------------
def test_mrpm_old_none(tmpdir):
    """
    Test for most_recent_prefix_match() with a ./old directory and no matches
    in . or ./old
    """
    pytest.debug_func()
    makefile(tmpdir, "old", ensure=True, dir=True)
    testfile = makefile(tmpdir, "mrpm", ensure=True)
    result = fl.most_recent_prefix_match(tmpdir.strpath, testfile.basename)
    assert result is None


# -----------------------------------------------------------------------------
def test_mrpm_old_nosuch_hit(tmpdir):
    """
    Test for most_recent_prefix_match() with non-existent stem file, a ./old
    directory, and no matches in . or ./old
    """
    olddir = makefile(tmpdir, "old", ensure=True, dir=True)
    tfile = makefile(tmpdir, "mrpm", ensure=False)
    mfile = makefile(olddir, "mrpm.suffix", ensure=True)
    result = fl.most_recent_prefix_match(tmpdir.strpath, tfile.basename)
    assert mfile.strpath == result


# -----------------------------------------------------------------------------
def test_mrpm_old_nosuch_none(tmpdir):
    """
    Test for most_recent_prefix_match() with non-existent stem file, a ./old
    directory, and no matches in . or ./old
    """
    olddir = makefile(tmpdir, "old", ensure=True, dir=True)
    tfile = makefile(tmpdir, "mrpm", ensure=False)
    makefile(olddir, "mrpm.suffix", ensure=False)
    result = fl.most_recent_prefix_match(tmpdir.strpath, tfile.basename)
    assert result is None


# ---------------------------------------------------------------------------
def test_revert_cdx(tmpdir, fx_match, capsys):
    """
    nomatch/cwd/old = c ; dir/pxr = d ; exec/noexec = x

    Test 'fl.fl_revert()' with a prefix match in the current directory
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm1.new")
    with U.Chdir(tmpdir.strpath):
        fl.fl_revert(**{"FILE": [fx_match.mrpm1.basename],
                        "d": False, "n": False})
        result, _ = capsys.readouterr()
        for exp in fx_match.mrpm1_rvt_exp:
            assert exp in result
        assert fx_match.mrpm1.read() == "copy of test file\n"
        assert new.read() == "this is a test file\n"


# ---------------------------------------------------------------------------
def test_revert_cdn(tmpdir, fx_match, capsys):
    """
    nomatch/cwd/old = c ; dir/pxr = d ; exec/noexec = n

    Test 'fl.fl_revert('n': True)' with a prefix match in the current directory
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm1.new")
    with U.Chdir(tmpdir.strpath):
        fl.fl_revert(**{"FILE": [fx_match.mrpm1.basename],
                        "d": False, "n": True})
        result, _ = capsys.readouterr()
        for exp in fx_match.mrpm1_rvt_exp:
            assert "would do '{}'".format(exp) in result
        assert not new.exists()
        assert fx_match.mrpm1.read() == "this is a test file\n"


# ---------------------------------------------------------------------------
def test_revert_cpx(tmpdir, fx_match):
    """
    nomatch/cwd/old = c ; dir/pxr = p ; exec/noexec = x

    Test pexpect.run('fl revert FILE') with a prefix match in the current
    directory
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm1.new")
    with U.Chdir(tmpdir.strpath):
        result = pexpect.run("fl revert {}".format(fx_match.mrpm1.basename))
        for exp in fx_match.mrpm1_rvt_exp:
            assert exp in result
        assert fx_match.mrpm1.read() == "copy of test file\n"
        assert new.read() == "this is a test file\n"


# ---------------------------------------------------------------------------
def test_revert_cpn(tmpdir, fx_match):
    """
    nomatch/cwd/old = c ; dir/pxr = p ; exec/noexec = n

    Test pexpect.run('fl revert -n FILE') with a prefix match in the current
    directory
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm1.new")
    with U.Chdir(tmpdir.strpath):
        result = pexpect.run("fl revert -n {}".format(fx_match.mrpm1.basename))
        assert "would do 'os.rename(" in result
        for exp in fx_match.mrpm1_rvt_exp:
            assert "would do '{}'".format(exp) in result
        assert not new.exists()
        assert fx_match.mrpm1.read() == "this is a test file\n"


# ---------------------------------------------------------------------------
def test_revert_odx(tmpdir, fx_match, capsys):
    """
    nomatch/cwd/old = o ; dir/pxr = d ; exec/noexec = x

    Test fl.fl_revert(**{'FILE': [fx_match.mrpm2.basename], ... }) with a
    prefix match in ./old
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm2.new")
    with U.Chdir(tmpdir.strpath):
        fl.fl_revert(**{"FILE": [fx_match.mrpm2.basename],
                        "d": False, "n": False})
        result, _ = capsys.readouterr()
        for exp in fx_match.mrpm2_rvt_exp:
            assert exp in result
        assert new.exists()
        assert fx_match.mrpm2.read() == "copy of another test file\n"


# ---------------------------------------------------------------------------
def test_revert_odn(tmpdir, fx_match, capsys):
    """
    nomatch/cwd/old = o ; dir/pxr = d ; exec/noexec = n

    Test fl.fl_revert(**{'FILE': [fx_match.mrpm2.basename], 'n': True, ... })
    with a prefix match in ./old
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm2.new")
    with U.Chdir(tmpdir.strpath):
        fl.fl_revert(**{"FILE": [fx_match.mrpm2.basename],
                        "d": False, "n": True})
        result, _ = capsys.readouterr()
        for exp in fx_match.mrpm2_rvt_exp:
            assert "would do '{}'".format(exp) in result
        assert not new.exists()
        assert fx_match.mrpm2.read() == "this is another test file\n"


# ---------------------------------------------------------------------------
def test_revert_opx(tmpdir, fx_match):
    """
    nomatch/cwd/old = o ; dir/pxr = p ; exec/noexec = x

    Test pexpect.run('fl revert FILE') with a prefix match in ./old
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm2.new")
    with U.Chdir(tmpdir.strpath):
        result = pexpect.run("fl revert {}".format(fx_match.mrpm2.basename))
        for exp in fx_match.mrpm2_rvt_exp:
            assert exp in result
        assert new.exists()
        assert fx_match.mrpm2.read() == "copy of another test file\n"


# ---------------------------------------------------------------------------
def test_revert_opn(tmpdir, fx_match):
    """
    nomatch/cwd/old = o ; dir/pxr = p ; exec/noexec = n

    Test pexpect.run('fl revert -n FILE') with a prefix match in ./old
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm2.new")
    with U.Chdir(tmpdir.strpath):
        result = pexpect.run("fl revert -n {}".format(fx_match.mrpm2.basename))
        for exp in fx_match.mrpm2_rvt_exp:
            assert "would do '{}'".format(exp) in result
        assert not new.exists()
        assert fx_match.mrpm2.read() == "this is another test file\n"


# ---------------------------------------------------------------------------
def test_revert_ndx(tmpdir, fx_match, capsys):
    """
    nomatch/cwd/old = n ; dir/pxr = d ; exec/noexec = x

    Test fl.fl_revert(**{'FILE': [fx_match.mrpm1.basename], ... }) with no
    prefix match in cwd or ./old
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm1.new")
    fx_match.mrpm1_dt.remove()

    with U.Chdir(tmpdir.strpath):
        fl.fl_revert(**{"FILE": [fx_match.mrpm1.basename],
                        "d": False, "n": False})
        result, _ = capsys.readouterr()
        assert not new.exists()
        exp = "No prefix match found for {}\n".format(fx_match.mrpm1.basename)
        assert exp in result
        for exp in fx_match.mrpm1_rvt_exp + fx_match.mrpm2_rvt_exp:
            assert exp not in result
        assert fx_match.mrpm1.read() == "this is a test file\n"


# ---------------------------------------------------------------------------
def test_revert_ndn(tmpdir, fx_match, capsys):
    """
    nomatch/cwd/old = n ; dir/pxr = d ; exec/noexec = n

    Test fl.fl_revert(**{'FILE': [fx_match.mrpm2.basename], 'n': True, ... })
    with no prefix match in cwd or ./old
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm1.new")
    fx_match.mrpm1_dt.remove()

    with U.Chdir(tmpdir.strpath):
        fl.fl_revert(**{"FILE": [fx_match.mrpm1.basename],
                        "d": False, "n": True})
        result, _ = capsys.readouterr()
        assert not new.exists()
        exp = "No prefix match found for {}\n".format(fx_match.mrpm1.basename)
        assert exp in result
        for exp in fx_match.mrpm1_rvt_exp:
            assert "would do '{}'".format(exp) not in result
        assert fx_match.mrpm1.read() == "this is a test file\n"


# ---------------------------------------------------------------------------
def test_revert_npx(tmpdir, fx_match):
    """
    nomatch/cwd/old = n ; dir/pxr = p ; exec/noexec = x

    Test pexpect.run('fl revert FILE') with no prefix match in cwd or ./old
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm1.new")
    fx_match.mrpm1_dt.remove()

    with U.Chdir(tmpdir.strpath):
        result = pexpect.run("fl revert {}".format(fx_match.mrpm1.basename))
        assert not new.exists()
        exp = "{} {}\r\n".format("No prefix match found for",
                                 fx_match.mrpm1.basename)
        assert exp in result
        for exp in fx_match.mrpm1_rvt_exp + fx_match.mrpm2_rvt_exp:
            assert exp not in result
        assert fx_match.mrpm1.read() == "this is a test file\n"


# ---------------------------------------------------------------------------
def test_revert_npn(tmpdir, fx_match):
    """
    nomatch/cwd/old = n ; dir/pxr = p ; exec/noexec = n

    Test pexpect.run('fl revert -n FILE') with no prefix match in cwd or ./old
    """
    pytest.debug_func()
    new = tmpdir.join("mrpm1.new")
    fx_match.mrpm1_dt.remove()

    with U.Chdir(tmpdir.strpath):
        result = pexpect.run("fl revert -n {}".format(fx_match.mrpm1.basename))
        assert not new.exists()
        exp = "{} {}\r\n".format("No prefix match found for",
                                 fx_match.mrpm1.basename)
        assert exp in result
        for exp in fx_match.mrpm1_rvt_exp:
            assert "would do '{}'".format(exp) not in result
        assert fx_match.mrpm1.read() == "this is a test file\n"


# ---------------------------------------------------------------------------
def setUpModule():
    """
    Run once before any of the tests in this module
    """
    if os.path.basename(os.getcwd()) == 'fl_tests':
        return

    if not os.path.exists('fl_tests'):
        os.mkdir('fl_tests')
        os.mkdir('fl_tests/old')


# ---------------------------------------------------------------------------
def tearDownModule():
    """
    Run once after all the tests in this module
    """
    kf = os.getenv('KEEPFILES')
    if not kf:
        shutil.rmtree('fl_tests')


# -----------------------------------------------------------------------------
class TestFL_edit(th.HelpedTestCase):
    testdir = tempfile.mkdtemp(dir="/tmp")
    testdata = ["one foo two foo three\n",
                "foo four five foo\n",
                "six seven eight foo nine\n"]

    # -------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        """
        Clean up test directory
        """
        shutil.rmtree(cls.testdir)

    # -------------------------------------------------------------------------
    def test_fl_edit_noarg(self):
        """
        fl edit                          => help msg
        """
        self.fl_edit_flawed("fl edit",
                            "usage: fl edit [-i <suffix>] -e <cmd> f1 f2 ...")

    # -------------------------------------------------------------------------
    def test_fl_edit_e_reqarg(self):
        """
        fl edit -e                       => -e requires argument
        check for
         - message that -e requires an argument
        """
        self.fl_edit_flawed("fl edit -e",
                            "-e option requires an argument")

    # -------------------------------------------------------------------------
    def test_fl_edit_i_reqarg(self):
        """
        fl edit -i                       => -i requires argument
        check for message that -i requires argument
        """
        self.fl_edit_flawed("fl edit -i",
                            "-i option requires an argument")

    # -------------------------------------------------------------------------
    def test_fl_edit_nofiles(self):
        """
        fl edit -e "s/foo/bar/"          => no files to edit
        check for message that there are no files to edit
        """
        self.fl_edit_flawed("fl edit -e 's/foo/bar/'",
                            "no files on command line to edit")

    # -------------------------------------------------------------------------
    def test_fl_edit_sub_mid(self):
        """
        fl edit -e "s/foo/bar/" f1 f2    => change "foo" to "bar" in f1, f2
        check for
         - f{1,2} edited correctly
         - f{1,2}.original exists with unchanged content
        """
        self.fl_edit_warn(eopt="s/foo/bar/",
                          files=2,
                          inp=self.testdata,
                          exp=["one bar two bar three",
                               "bar four five bar",
                               "six seven eight bar nine"],
                          warn=["/Users/tbarron/prj/github/backscratcher/bscr/"
                                "util.py:207: UserWarning: util.dispatch is "
                                "deprecated in favor of docopt_dispatch",
                                "  warnings.warn(\"util.dispatch is "
                                "deprecated in favor of docopt_dispatch\")"])

    # -------------------------------------------------------------------------
    def test_fl_edit_sub_bol(self):
        """
        fl edit -e "s/^foo/bar/" f1 f2   => edit at beginning of line
         - f1 edited correctly
         - f2 edited correctly
         - f{1,2}.original have unchanged content
        """
        self.fl_edit_warn(eopt="s/^foo/bar/",
                          files=2,
                          inp=self.testdata,
                          exp=["one foo two foo three",
                               "bar four five foo",
                               "six seven eight foo nine"],
                          warn=["/Users/tbarron/prj/github/backscratcher/bscr/"
                                "util.py:207: UserWarning: util.dispatch is "
                                "deprecated in favor of docopt_dispatch",
                                "  warnings.warn(\"util.dispatch is "
                                "deprecated in favor of docopt_dispatch\")"])

    # -------------------------------------------------------------------------
    def test_fl_edit_i_old(self):
        """
        fl edit -i old -e "s/x/y/" f1    => rename original to f1.old
         - f1 edited correctly
         - f1.old exists
         - f1.original does not exist
        """
        pytest.debug_func()
        self.fl_edit_warn(eopt="s/[rv]e/n/",
                          iopt="old",
                          files=1,
                          inp=self.testdata,
                          exp=["one foo two foo thne",
                               "foo four fin foo",
                               "six senn eight foo nine"],
                          warn=["/Users/tbarron/prj/github/backscratcher/bscr/"
                                "util.py:207: UserWarning: util.dispatch is "
                                "deprecated in favor of docopt_dispatch",
                                "  warnings.warn(\"util.dispatch is "
                                "deprecated in favor of docopt_dispatch\")"])

    # -------------------------------------------------------------------------
    def test_fl_edit_xlate_rot13(self):
        """
        fl edit -e "y/a-z/n-za-m/" f1 f2 => rot13
        check for
         - f{1,2} edited correctly
         - f{1,2}.original exist with correct content
        """
        prev = "abcdefghijklmnopqrstuvwxyz"
        post = "nopqrstuvwxyzabcdefghijklm"
        self.fl_edit_warn(eopt="y/%s/%s/" % (prev, post),
                          files=2,
                          inp=self.testdata,
                          exp=["bar sbb gjb sbb guerr",
                               "sbb sbhe svir sbb",
                               "fvk frira rvtug sbb avar"],
                          warn=["/Users/tbarron/prj/github/backscratcher/bscr/"
                                "util.py:207: UserWarning: util.dispatch is "
                                "deprecated in favor of docopt_dispatch",
                                "  warnings.warn(\"util.dispatch is "
                                "deprecated in favor of docopt_dispatch\")"])

    # -------------------------------------------------------------------------
    def test_fl_edit_xlate_ret(self):
        """
        fl edit -e "y/\r//" f1 f2        => remove \r characters
         - f{1,2} edited correctly
         - f{1,2}.original have correct original content
        """
        rdata = [x.rstrip() + "\r\n" for x in self.testdata]
        self.fl_edit_warn(eopt="y/\r//",
                          files=2,
                          inp=rdata,
                          exp=["one foo two foo three",
                               "foo four five foo",
                               "six seven eight foo nine"],
                          warn=["/Users/tbarron/prj/github/backscratcher/bscr/"
                                "util.py:207: UserWarning: util.dispatch is "
                                "deprecated in favor of docopt_dispatch",
                                "  warnings.warn(\"util.dispatch is "
                                "deprecated in favor of docopt_dispatch\")"])

    # -------------------------------------------------------------------------
    def fl_edit_flawed(self, cmd, exp):
        """
        Attempt to run an 'fl edit' command with something missing
        """
        result = pexpect.run(cmd)
        self.assertFalse("Traceback" in result,
                         "Traceback not expected in %s" % result)
        self.assertTrue(exp in result,
                        "\nExpected '%s' in \n%s" %
                        (exp, util.lquote(result)))

    # -------------------------------------------------------------------------
    def fl_edit_warn(self, eopt='', iopt='', files=0,
                     inp=None, exp=None, warn=None):
        """
        Common code for all the test_fl_edit_* routines
        """
        fl = []
        inp = inp or []
        exp = exp or []
        warn = warn or []
        for idx in range(files):
            (fd, fp) = tempfile.mkstemp(dir=self.testdir)
            os.close(fd)
            fl.append(fp)
            util.writefile(fp, inp)

        suffix = 'original'
        with util.Chdir(self.testdir):
            cmd = "fl edit "
            if eopt != '':
                cmd += '-e "%s" ' % eopt
            if iopt != '':
                cmd += '-i %s ' % iopt
                suffix = iopt
            if 0 < len(fl):
                cmd += " ".join(fl)
            result = pexpect.run(cmd)

            self.assertTrue(result == "\r\n".join(warn + [""]),
                            "Expected '%s' to contain '%s'"
                            % (result, "\r\n".join(warn + [""])))
            for fp in fl:
                forig = fp + "." + suffix
                self.assertTrue(util.exists(forig),
                                "Expected %s to exist" % forig)
                self.assertTrue("foo four five foo" in util.contents(forig),
                                "Contents of %s have changed" % forig)
                self.assertTrue(util.exists(fp),
                                "Expected %s to exist" % fp)
                self.assertEq(exp, util.contents(fp))

            for fp in fl:
                util.safe_unlink(fp)

    # -------------------------------------------------------------------------
    def fl_edit_ok(self, eopt='', iopt='', files=0, inp=[], exp=[]):
        """
        Common code for all the test_fl_edit_* routines
        """
        fl = []
        for idx in range(files):
            (fd, fp) = tempfile.mkstemp(dir=self.testdir)
            os.close(fd)
            fl.append(fp)
            util.writefile(fp, inp)

        suffix = 'original'
        with util.Chdir(self.testdir):
            cmd = "fl edit "
            if eopt != '':
                cmd += '-e "%s" ' % eopt
            if iopt != '':
                cmd += '-i %s ' % iopt
                suffix = iopt
            if 0 < len(fl):
                cmd += " ".join(fl)
            result = pexpect.run(cmd)

            self.assertTrue(result == "",
                            "Expected '%s' to be empty" % result)
            for fp in fl:
                forig = fp + "." + suffix
                self.assertTrue(util.exists(forig),
                                "Expected %s to exist" % forig)
                self.assertTrue("foo four five foo" in util.contents(forig),
                                "Contents of %s have changed" % forig)
                self.assertTrue(util.exists(fp),
                                "Expected %s to exist" % fp)
                self.assertEq(exp, util.contents(fp))

            for fp in fl:
                util.safe_unlink(fp)


# -----------------------------------------------------------------------------
def makefile(loc, basename, content=None, ensure=False, dir=False,
             copy=None, atime=0, mtime=0):
    """
    Return a py.path.local based on *loc*.join(*basename*). If *ensure*, touch
    it. If *dir*, make it a directory
    """
    rval = loc.join(basename)
    if copy:
        if dir:
            raise U.Error("*dir* must be false if *copy* is not None")
        if isinstance(copy, py.path.local):
            copy.copy(rval)
        elif isinstance(copy, str):
            copy = py.path.local(copy)
            copy.copy(rval)
        else:
            raise U.Error("*copy* must be a py.path.local or an str")
    elif content:
        if dir:
            raise U.Error("*dir* must be false if *content* is not None")
        if isinstance(content, str):
            rval.write(content)
        elif isinstance(content, list):
            rval.write("\n".join(content))
        else:
            rval.write(str(content))
    elif ensure:
        rval.ensure(dir=dir)

    if rval.exists():
        if atime != 0 or mtime != 0:
            atime = atime or time.time()
            mtime = mtime or time.time()
            os.utime(rval.strpath, (atime, mtime))

    return rval


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_edit(tmpdir, request):
    """
    Set up test data for editfile tests
    """
    # pdb.set_trace()
    fx_edit.tdata = ["foo bar",
                     "bar foo",
                     "barfoo",
                     "foobar foo",
                     "loofafool"]
    fx_edit.fp = tmpdir.join(request.function.func_name)
    fx_edit.forig = tmpdir.join(fx_edit.fp.basename + ".original")
    return fx_edit


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_match(tmpdir):
    """
    Set up some matching files for fl diff
    """
    this = fx_match
    this.mrpm1 = makefile(tmpdir, "mrpm1", content="this is a test file\n")
    this.mrpm2 = makefile(tmpdir, "mrpm2",
                          content="this is another test file\n")
    this.mrpm1_dt = makefile(tmpdir, "mrpm1.2009-10-01",
                             content="copy of test file\n")
    this.olddir = makefile(tmpdir, "old", dir=True, ensure=True)
    this.mrpm2_dt = makefile(this.olddir, "mrpm2.2009-08-31",
                             content="copy of another test file\n")

    this.mrpm1_diff_exp = [u'diff ./mrpm1.2009-10-01 mrpm1',
                           u'1c1',
                           u'< copy of test file',
                           u'---',
                           u'> this is a test file',
                           u'',
                           u'']

    this.mrpm2_diff_exp = [u'diff ./old/mrpm2.2009-08-31 mrpm2',
                           u'1c1',
                           u'< copy of another test file',
                           u'---',
                           u'> this is another test file',
                           u'',
                           u'']
    newname = this.mrpm1.basename + ".new"
    this.mrpm1_rvt_exp = ["os.rename({}, {})".format(this.mrpm1.basename,
                                                     newname),
                          "os.rename(./{}, {})".format(this.mrpm1_dt.basename,
                                                       this.mrpm1.basename)]
    newname = this.mrpm2.basename + ".new"
    this.mrpm2_rvt_exp = ["os.rename({}, {})".format(this.mrpm2.basename,
                                                     newname),
                          "{}/{}, {})".format("os.rename(./old",
                                              this.mrpm2_dt.basename,
                                              this.mrpm2.basename)]
    return this

from bscr import fl
from bscr import util
import os
import pexpect
import py
import pytest
import random
import re
import stat
import string
import time
from bscr import util as U


# -----------------------------------------------------------------------------
def test_amtime_atom_dir(tmpdir, fx_amtime):
    """
    Test fl_set_atime_to_mtime()
    """
    pytest.debug_func()
    fl.fl_set_atime_to_mtime(**{"FILE": [fx_amtime.testfile.strpath],
                                "d": False})
    fx_amtime.exptime = fx_amtime.mtime


# -----------------------------------------------------------------------------
def test_amtime_atom_pxr(tmpdir, fx_amtime):
    """
    Test fl_set_atime_to_mtime()
    """
    pytest.debug_func()
    cmd = "fl set_atime_to_mtime {}".format(fx_amtime.testfile.strpath)
    result = pexpect.run(cmd)
    assert result == ""
    fx_amtime.exptime = fx_amtime.mtime


# -----------------------------------------------------------------------------
def test_amtime_mtoa_dir(tmpdir, fx_amtime):
    """
    Test fl_set_mtime_to_atime()
    """
    pytest.debug_func()
    fl.fl_set_mtime_to_atime(**{"FILE": [fx_amtime.testfile.strpath],
                                "d": False})
    fx_amtime.exptime = fx_amtime.atime


# -----------------------------------------------------------------------------
def test_amtime_mtoa_pxr(tmpdir, fx_amtime):
    """
    Test fl_set_mtime_to_atime()
    """
    pytest.debug_func()
    cmd = "fl set_mtime_to_atime {}".format(fx_amtime.testfile.strpath)
    result = pexpect.run(cmd)
    assert result == ""
    fx_amtime.exptime = fx_amtime.atime


# -----------------------------------------------------------------------------
def test_command_line():
    """
    Running the command with no arguments should get help output
    """
    pytest.debug_func()
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
def test_edit_e_reqarg(fx_usg_no_trbk):
    """
    fl edit -e => -e requires an argument
    """
    pytest.debug_func()
    fx_usg_no_trbk.result = pexpect.run("fl edit -e")


# -----------------------------------------------------------------------------
def test_edit_i_old_dir(tmpdir, capsys, fx_orig2):
    """
    fl edit -i old -e 's/x/y' f1    => rename original to f1.old
    """
    pytest.debug_func()
    fx_orig2.xdata = [re.sub("^foo", "bar", _) for _ in fx_orig2.tdata]
    with U.Chdir(tmpdir.strpath):
        fl.fl_edit(**{"d": False,
                      "e": "s/^foo/bar/",
                      "i": "old",
                      "FILE": ["f1", "f2"]})
        result, _ = capsys.readouterr()
        fx_orig2.result = result

    fx_orig2.files['f1_orig'] = makefile(tmpdir, "f1.old")
    fx_orig2.files['f2_orig'] = makefile(tmpdir, "f2.old")


# -----------------------------------------------------------------------------
def test_edit_i_old_pxr(tmpdir, fx_orig):
    """
    fl edit -i old -e 's/x/y' f1    => rename original to f1.old
    """
    pytest.debug_func()
    fx_orig.xdata = [re.sub("[rv]e", "n", _) for _ in fx_orig.tdata]
    with U.Chdir(tmpdir.strpath):
        fname = fx_orig.files['f1'].basename
        cmd = "fl edit -e s/[rv]e/n/ -i old {}".format(fname)
        fx_orig.result = pexpect.run(cmd)
    fx_orig.files['f1_orig'] = makefile(tmpdir, "f1.old")


# -----------------------------------------------------------------------------
def test_edit_i_reqarg(fx_usg_no_trbk):
    """
    fl edit -i                       => -i requires argument
    check for message that -i requires argument
    """
    pytest.debug_func()
    fx_usg_no_trbk.result = pexpect.run("fl edit -i")


# -----------------------------------------------------------------------------
def test_edit_noarg(fx_usg_no_trbk):
    """
    fl edit                          => help msg
    """
    pytest.debug_func()
    fx_usg_no_trbk.result = pexpect.run("fl edit")


# -----------------------------------------------------------------------------
def test_edit_nofiles(fx_usg_no_trbk):
    """
    fl edit -e 's/foo/bar/'          => no files to edit
    check for message that there are no files to edit
    """
    pytest.debug_func()
    fx_usg_no_trbk.result = pexpect.run("fl edit -e \"s/foo/bar/\"")


# -----------------------------------------------------------------------------
def test_edit_sub_bol_dir(tmpdir, capsys, fx_orig2):
    """
    fl edit -e 's/^foo/bar/'f1 f2   => edit at beginning of line
     - f1 edited correctly
     - f2 edited correctly
     - f{1,2}.original have unchanged content
    """
    pytest.debug_func()
    fx_orig2.xdata = [re.sub("^foo", "bar", _) for _ in fx_orig2.tdata]
    with U.Chdir(tmpdir.strpath):
        fl.fl_edit(**{"d": False,
                      "e": "s/^foo/bar/",
                      "i": "",
                      "FILE": ["f1", "f2"]})
        fx_orig2.result, _ = capsys.readouterr()


# -----------------------------------------------------------------------------
def test_edit_sub_bol_pxr(tmpdir, fx_orig2):
    """
    fl edit -e 's/^foo/bar/'f1 f2   => edit at beginning of line
     - f1 edited correctly
     - f2 edited correctly
     - f{1,2}.original have unchanged content
    """
    pytest.debug_func()
    fx_orig2.xdata = [re.sub("^foo", "bar", _) for _ in fx_orig2.tdata]
    with U.Chdir(tmpdir.strpath):
        fx_orig2.result = pexpect.run("fl edit -e s/^foo/bar/ f1 f2")


# -------------------------------------------------------------------------
def test_edit_sub_mid_dir(tmpdir, capsys, fx_orig2):
    """
    fl edit -e 's/foo/bar/' f1 f2    => change 'foo' to 'bar' in f1, f2
    check for
     - f{1,2} edited correctly
     - f{1,2}.original exists with unchanged content
    """
    pytest.debug_func()
    fx_orig2.xdata = [re.sub("foo", "bar", _) for _ in fx_orig2.tdata]
    with U.Chdir(tmpdir.strpath):
        fl.fl_edit(**{"d": False,
                      "e": "s/foo/bar/",
                      "i": "",
                      "FILE": ["f1", "f2"]})
        fx_orig2.result, _ = capsys.readouterr()


# -------------------------------------------------------------------------
def test_edit_sub_mid_pxr(tmpdir, fx_orig2):
    """
    fl edit -e "s/foo/bar/" f1 f2    => change "foo" to "bar" in f1, f2
    check for
     - f{1,2} edited correctly
     - f{1,2}.original exists with unchanged content
    """
    pytest.debug_func()
    fx_orig2.xdata = [re.sub("foo", "bar", _) for _ in fx_orig2.tdata]
    with U.Chdir(tmpdir.strpath):
        fx_orig2.result = pexpect.run("fl edit -e s/foo/bar/ f1 f2")


# -------------------------------------------------------------------------
def test_edit_xlate_ret_dir(tmpdir, capsys, fx_seven):
    """
    fl edit -e "y/\r//" f1 f2        => remove \r characters
        - f{1,2} edited correctly
        - f{1,2}.original have correct original content
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        fl.fl_edit(**{"d": False,
                      "e": "y/\r//",
                      "i": "",
                      "FILE": ["f1", "f2"]})
        fx_seven.result, _ = capsys.readouterr()


# -------------------------------------------------------------------------
def test_edit_xlate_ret_pxr(tmpdir, fx_seven):
    """
    fl edit -e 'y/\r//' f1 f2        => remove \r characters
        - f{1,2} edited correctly
        - f{1,2}.original have correct original content
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        fx_seven.result = pexpect.run("fl edit -e \"y/\r//\" f1 f2")


# -----------------------------------------------------------------------------
def test_edit_xlate_rot13_dir(tmpdir, capsys, fx_rot13):
    """
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        fl.fl_edit(**{"d": False,
                      "e": "y/{}/{}/".format(fx_rot13.prev, fx_rot13.post),
                      "i": "",
                      "FILE": [_.basename for _ in fx_rot13.input_l]})
        fx_rot13.result, _ = capsys.readouterr()


# -----------------------------------------------------------------------------
def test_edit_xlate_rot13_pxr(tmpdir, fx_rot13):
    """
    fl edit -e 'y/ALPHA/ALPHA-13/' f1 f2
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        flist = " ".join([_.basename for _ in fx_rot13.input_l])
        cmd = "fl edit -e \"y/{}/{}/\" {}".format(fx_rot13.prev,
                                                  fx_rot13.post,
                                                  flist)
        fx_rot13.result = pexpect.run(cmd)


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
    pytest.debug_func()
    with pytest.raises(IOError) as err:
        fl.editfile(fx_edit.fp.strpath, 's', 'foo', 'bar', None)
    exp = "No such file or directory: '{}'".format(fx_edit.fp.strpath)
    assert exp in str(err)


# -----------------------------------------------------------------------------
def test_editfile_rgx(tmpdir, fx_edit):
    """
    fl.editfile('legit', 's', 'foo', 'bar', None)
    """
    pytest.debug_func()
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
    pytest.debug_func()
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
    pytest.debug_func()
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
    pytest.debug_func()
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
    pytest.debug_func()
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
def fx_amtime(tmpdir):
    """
    Set up some atime, mtime test data
    """
    fx_amtime.exptime = None
    atime = fx_amtime.atime = int(time.time() - random.randint(1000, 2000))
    mtime = fx_amtime.mtime = int(time.time() + random.randint(1000, 2000))
    fx_amtime.testfile = makefile(tmpdir, "testfile", atime=atime, mtime=mtime,
                                  content="This is the test file")
    yield fx_amtime
    s = os.stat(fx_amtime.testfile.strpath)
    assert fx_amtime.exptime == s[stat.ST_MTIME]
    assert fx_amtime.exptime == s[stat.ST_ATIME]
    assert s[stat.ST_ATIME] == s[stat.ST_MTIME]


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_edit(tmpdir, request):
    """
    Set up test data for editfile tests
    """
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


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_orig(tmpdir, fx_tdata):
    """
    """
    fx_orig.tdata = fx_tdata
    f1 = makefile(tmpdir, "f1", content="\n".join(fx_tdata))
    f1_original = makefile(tmpdir, "f1.original")
    fx_orig.files = {'f1': f1,
                     'f1_orig': f1_original}

    yield fx_orig

    assert fx_orig.result == ""
    for fkey in fx_orig.files:
        assert fx_orig.files[fkey].exists()
    for exp in fx_orig.xdata:
        assert exp in f1.read()
    for exp in fx_orig.tdata:
        assert exp in fx_orig.files['f1_orig'].read()


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_orig2(tmpdir, fx_tdata):
    """
    """
    fx_orig2.tdata = fx_tdata
    f1 = makefile(tmpdir, "f1", content="\n".join(fx_tdata))
    f2 = makefile(tmpdir, "f2", content="\n".join(fx_tdata))
    f1_original = makefile(tmpdir, "f1.original")
    f2_original = makefile(tmpdir, "f2.original")
    fx_orig2.files = {'f1': f1,
                      'f2': f2,
                      'f1_orig': f1_original,
                      'f2_orig': f2_original}

    yield fx_orig2

    assert fx_orig2.result == ""
    for fkey in fx_orig2.files:
        assert fx_orig2.files[fkey].exists()
    for exp in fx_orig2.xdata:
        assert exp in f1.read()
        assert exp in f2.read()
    for exp in fx_orig2.tdata:
        assert exp in fx_orig2.files['f1_orig'].read()
        assert exp in fx_orig2.files['f2_orig'].read()


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_rot13(tmpdir, fx_tdata):
    """
    Set up some test data
    """
    fx_rot13.result = None
    fx_rot13.tdata = fx_tdata
    fx_rot13.prev = string.lowercase
    fx_rot13.post = string.lowercase[13:]+string.lowercase[:13]
    table = string.maketrans(fx_rot13.prev, fx_rot13.post)
    fx_rot13.exp = [_.translate(table) for _ in fx_tdata]
    f1 = makefile(tmpdir, "f1", content="\n".join(fx_tdata))
    f2 = makefile(tmpdir, "f2", content="\n".join(fx_tdata))
    fx_rot13.input_l = [f1, f2]
    fx_rot13.orig_l = [tmpdir.join(f1.basename + ".original"),
                       tmpdir.join(f2.basename + ".original")]
    yield fx_rot13
    assert fx_rot13.result == ""
    for fh in fx_rot13.input_l:
        for line in fx_rot13.exp:
            assert line in fh.read()
    for fh in fx_rot13.orig_l:
        assert fh.exists()
        for line in fx_rot13.tdata:
            assert line in fh.read()


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_seven(tmpdir, fx_tdata):
    """
    Set up some test data
    """
    fx_seven.result = None
    fx_seven.tdata = fx_tdata
    f1 = makefile(tmpdir, "f1", content="\n\r".join(fx_tdata))
    f2 = makefile(tmpdir, "f2", content="\n\r".join(fx_tdata))
    fx_seven.input_l = [f1, f2]
    fx_seven.orig_l = [tmpdir.join(f1.basename + ".original"),
                       tmpdir.join(f2.basename + ".original")]
    yield fx_seven
    assert fx_seven.result == ""
    for fh in fx_seven.input_l:
        for line in fx_seven.tdata:
            assert line in fh.read()
        assert "\r" not in fh.read()
    for fh in fx_seven.orig_l:
        assert fh.exists()
        assert "\n\r" in fh.read()


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_tdata():
    """
    Set up some test data
    """
    tdata = ["one foo two foo three",
             "foo four five foo",
             "six seven eight foo nine", ]
    return tdata


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_usg_no_trbk():
    """
    result should contain 'Usage:' but not 'Traceback'
    """
    fx_usg_no_trbk.result = None
    yield fx_usg_no_trbk
    assert "Traceback" not in fx_usg_no_trbk.result
    assert "Usage:" in fx_usg_no_trbk.result

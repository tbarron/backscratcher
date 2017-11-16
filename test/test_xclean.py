import bscr.xclean
from bscr import util as U
import pexpect
import pytest
import re


# -----------------------------------------------------------------------------
def test_cleanup_dr_np_nr(capsys, tmpdir, fx_cleanup):
    """
    Run cleanup with dryrun but no pattern or recursive flag. Afterwards, the
    target files should still exist. The dryrun message should show up in the
    output. Target files in the top directory should be named in the output.
    """
    pytest.debug_func()
    bscr.xclean.cleanup(str(tmpdir), dryrun=True)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        assert floc.exists()
        if all([floc.basename.endswith("~"),
                tmpdir.strpath == floc.dirname]):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_cleanup_dr_np_r(capsys, tmpdir, fx_cleanup):
    """
    xclean --dry-run --recursive
    """
    pytest.debug_func()
    bscr.xclean.cleanup(str(tmpdir), dryrun=True, recursive=True)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        assert floc.exists()
        if all([floc.basename.endswith("~")]):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_cleanup_dr_p_nr(capsys, tmpdir, fx_cleanup):
    """
    xclean --dry-run --pattern 'no.*'
    """
    pytest.debug_func()
    rgx = fx_cleanup["rgx"]
    bscr.xclean.cleanup(str(tmpdir), dryrun=True, pattern=rgx)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        assert floc.exists()
        if all([tmpdir.strpath == floc.dirname,
                re.findall(rgx, floc.basename)]):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_cleanup_dr_p_r(capsys, tmpdir, fx_cleanup):
    """
    xclean --dry-run --pattern 'no.*' --recursive
    """
    pytest.debug_func()
    rgx = "no.*"
    bscr.xclean.cleanup(str(tmpdir), dryrun=True, pattern=rgx, recursive=True)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        assert floc.exists()
        if all([re.findall(rgx, floc.basename)]):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_cleanup_ndr_np_nr(capsys, tmpdir, fx_cleanup):
    """
    xclean
    """
    bscr.xclean.cleanup(str(tmpdir))
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] not in result
    for floc in fx_cleanup["files"]:
        if all([floc.basename.endswith("~"),
                tmpdir.strpath == floc.dirname]):
            assert floc.basename in result
            assert not floc.exists()
        else:
            assert floc.basename not in result
            assert floc.exists()


# -----------------------------------------------------------------------------
def test_cleanup_ndr_np_r(capsys, tmpdir, fx_cleanup):
    """
    xclean --recursive
    """
    bscr.xclean.cleanup(str(tmpdir), recursive=True)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] not in result
    for floc in fx_cleanup["files"]:
        if all([floc.basename.endswith("~")]):
            assert floc.basename in result
            assert not floc.exists()
        else:
            assert floc.basename not in result
            assert floc.exists()


# -----------------------------------------------------------------------------
def test_cleanup_ndr_p_nr(capsys, tmpdir, fx_cleanup):
    """
    xclean --pattern 'no.*'
    """
    rgx = fx_cleanup["rgx"]
    bscr.xclean.cleanup(str(tmpdir), pattern=rgx)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] not in result
    for floc in fx_cleanup["files"]:
        if all([tmpdir.strpath == floc.dirname,
                re.findall(rgx, floc.basename)]):
            assert floc.basename in result
            assert not floc.exists()
        else:
            assert floc.basename not in result
            assert floc.exists()


# -----------------------------------------------------------------------------
def test_cleanup_ndr_p_r(capsys, tmpdir, fx_cleanup):
    """
    xclean --pattern 'no.*' --recursive
    """
    rgx = fx_cleanup["rgx"]
    bscr.xclean.cleanup(str(tmpdir), pattern=rgx, recursive=True)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] not in result
    for floc in fx_cleanup["files"]:
        if all([re.findall(rgx, floc.basename)]):
            assert floc.basename in result
            assert not floc.exists()
        else:
            assert floc.basename not in result
            assert floc.exists()


# -------------------------------------------------------------------------
def test_find_files(tmpdir, fx_cleanup):
    """
    Finding files without recursion
    """
    fl = bscr.xclean.find_files(str(tmpdir))
    for floc in fx_cleanup["files"]:
        if all([tmpdir.strpath == floc.dirname,
                floc.basename.endswith("~")]):
            assert floc.strpath in fl
        else:
            assert floc.strpath not in fl


# -------------------------------------------------------------------------
def test_find_files_r(tmpdir, fx_cleanup):
    """
    Finding files with recursion
    """
    fl = bscr.xclean.find_files(str(tmpdir), recursive=True)
    for floc in fx_cleanup["files"]:
        if all([floc.basename.endswith("~")]):
            assert floc.strpath in fl
        else:
            assert floc.strpath not in fl


# -----------------------------------------------------------------------------
def test_find_files_p(tmpdir, fx_cleanup):
    """
    find files that match a pattern
    """
    rgx = fx_cleanup["rgx"]
    fl = bscr.xclean.find_files(str(tmpdir), pattern=rgx)
    for floc in fx_cleanup["files"]:
        if all([tmpdir.strpath == floc.dirname,
                re.findall(rgx, floc.strpath)]):
            assert floc.strpath in fl
        else:
            assert floc.strpath not in fl


# -----------------------------------------------------------------------------
def test_find_files_p_r(tmpdir, fx_cleanup):
    """
    find files that match a pattern, recursively
    """
    rgx = fx_cleanup["rgx"]
    fl = bscr.xclean.find_files(str(tmpdir), pattern=rgx, recursive=True)
    for floc in fx_cleanup["files"]:
        if all([re.findall(rgx, floc.strpath)]):
            assert floc.strpath in fl
        else:
            assert floc.strpath not in fl


# -----------------------------------------------------------------------------
def test_main_dr_np_nr(tmpdir, capsys, fx_cleanup):
    """
    calling main: xclean --dry-run
    """
    cmd = "bin/xclean -n {}".format(str(tmpdir))
    bscr.xclean.main(cmd.split())
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        assert floc.exists()
        if all([floc.basename.endswith("~"),
                tmpdir.strpath == floc.dirname]):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_main_dr_p_nr(tmpdir, capsys, fx_cleanup):
    """
    calling main: xclean --dry-run --pattern 'no.*'
    """
    rgx = fx_cleanup["rgx"]
    cmd = "bin/xclean -n -p {} {}".format(rgx, str(tmpdir))
    bscr.xclean.main(cmd.split())
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        assert floc.exists()
        if all([re.findall(rgx, floc.basename),
                tmpdir.strpath == floc.dirname]):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_main_dr_np_r(tmpdir, capsys, fx_cleanup):
    """
    calling main: xclean --dry-run --recursive
    """
    cmd = "bin/xclean -n -r {}".format(str(tmpdir))
    bscr.xclean.main(cmd.split())
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        assert floc.exists()
        if all([floc.basename.endswith("~")]):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_main_dr_p_r(tmpdir, capsys, fx_cleanup):
    """
    calling main: xclean --dry-run --pattern 'no.*' --recursive
    """
    rgx = fx_cleanup["rgx"]
    cmd = "bin/xclean -n -p {} -r {}".format(rgx, str(tmpdir))
    bscr.xclean.main(cmd.split())
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        assert floc.exists()
        if all([re.findall(rgx, floc.basename)]):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_main_ndr_np_nr(tmpdir, capsys, fx_cleanup):
    """
    calling main: xclean
    """
    pytest.debug_func()
    cmd = "bin/xclean {}".format(str(tmpdir))
    bscr.xclean.main(cmd.split())
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] not in result
    for floc in fx_cleanup["files"]:
        if all([floc.basename.endswith("~"),
                tmpdir.strpath == floc.dirname]):
            assert floc.basename in result
            assert not floc.exists()
        else:
            assert floc.basename not in result
            assert floc.exists()


# -----------------------------------------------------------------------------
def test_main_ndr_p_nr(tmpdir, capsys, fx_cleanup):
    """
    calling main: xclean --pattern 'no.*'
    """
    rgx = fx_cleanup["rgx"]
    cmd = "bin/xclean -p {} {}".format(rgx, str(tmpdir))
    bscr.xclean.main(cmd.split())
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] not in result
    for floc in fx_cleanup["files"]:
        if all([re.findall(rgx, floc.basename),
                tmpdir.strpath == floc.dirname]):
            assert floc.basename in result
            assert not floc.exists()
        else:
            assert floc.basename not in result
            assert floc.exists()


# -----------------------------------------------------------------------------
def test_main_ndr_np_r(tmpdir, capsys, fx_cleanup):
    """
    calling main: xclean --recursive
    """
    cmd = "bin/xclean -r {}".format(str(tmpdir))
    bscr.xclean.main(cmd.split())
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] not in result
    for floc in fx_cleanup["files"]:
        if all([floc.basename.endswith("~")]):
            assert floc.basename in result
            assert not floc.exists()
        else:
            assert floc.basename not in result
            assert floc.exists()


# -----------------------------------------------------------------------------
def test_main_ndr_p_r(tmpdir, capsys, fx_cleanup):
    """
    calling main: xclean --pattern 'no.*' --recursive
    """
    rgx = fx_cleanup["rgx"]
    cmd = "bin/xclean -p {} -r {}".format(rgx, str(tmpdir))
    bscr.xclean.main(cmd.split())
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] not in result
    for floc in fx_cleanup["files"]:
        if all([re.findall(rgx, floc.basename)]):
            assert floc.basename in result
            assert not floc.exists()
        else:
            assert floc.basename not in result
            assert floc.exists()


# -----------------------------------------------------------------------------
def test_xclean_help():
    """
    Verify that 'xclean --help' does the right thing
    """
    exp = ["Usage:",
           "    xclean - remove files whose names match a regexp",
           "",
           "Options:",
           "  -h, --help            show this help message and exit",
           "  -d, --debug           run under the debugger",
           "  -n, --dry-run         just report",
           "  -p PATTERN, --pattern=PATTERN",
           "                        file matching regexp",
           "  -r, --recursive       whether to descend directories",
           ]
    cmd = U.script_location("xclean")
    actual = pexpect.run("%s --help" % cmd)
    for line in exp:
        assert line in actual


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_cleanup(tmpdir):
    """
    Set up files for various tests
    """
    tmpdir.join('sub').ensure(dir=True)
    rval = {}
    rval['rgx'] = "no.*"
    rval['drmsg'] = "Without --dryrun, would remove"
    rval['files'] = [tmpdir.join(x).ensure() for x in ['xxx~',
                                                       'yyy~',
                                                       'sub/basement~',
                                                       'sub/.floor~',
                                                       'nomatch.txt',
                                                       'sub/nosuchfile',
                                                       ]]
    return rval

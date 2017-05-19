import bscr
import bscr.bscr
import glob
from bscr import util as U
import pexpect
import pytest
import re


# -----------------------------------------------------------------------------
def test_bscr_version_dir(capsys):
    """
    Test 'bscr version'
    """
    pytest.debug_func()
    bscr.bscr.bscr_version()
    result, _ = capsys.readouterr()
    assert "Traceback" not in result
    assert "Usage: bscr [options]" not in result
    assert "-d, --debug    run under the debugger" not in result
    assert re.findall("Backscratcher version \d+\.\d+.\d+", result)


# -----------------------------------------------------------------------------
def test_bscr_version_pxr():
    """
    Test 'bscr version'
    """
    pytest.debug_func()
    result = pexpect.run("bscr version")
    assert "Traceback" not in result
    assert "Usage: bscr [options]" not in result
    assert "-d, --debug    run under the debugger" not in result
    assert re.findall("Backscratcher version \d+\.\d+.\d+", result)


# -----------------------------------------------------------------------------
def test_bscr_help_dir(capsys):
    """
    Test 'bscr help'
    """
    pytest.debug_func()
    bscr.bscr.bscr_help(**{"d": False, "COMMAND": None})
    result, _ = capsys.readouterr()
    assert "Traceback" not in result
    for f in [x for x in dir(bscr.bscr) if x.startswith('bscr_')]:
        subc = f.replace('bscr_', '')
        assert subc in result


# -----------------------------------------------------------------------------
def test_bscr_help_pxr():
    """
    Test 'bscr help'
    """
    pytest.debug_func()
    result = pexpect.run('bscr help')
    assert "Traceback" not in result
    for f in [x for x in dir(bscr.bscr) if x.startswith('bscr_')]:
        subc = f.replace('bscr_', '')
        assert subc in result


# -----------------------------------------------------------------------------
def test_bscr_help_CMD_dir(capsys):
    """
    Test 'bscr help COMMAND'
    """
    pytest.debug_func()
    for fname in [x for x in dir(bscr.bscr) if x.startswith('bscr_')]:
        cname = fname.replace("bscr_", "")
        bscr.bscr.bscr_help(**{"d": False, "COMMAND": cname})
        result, ign = capsys.readouterr()
        assert result.strip() != ""
        func = getattr(bscr.bscr, fname)
        for line in [_ for _ in result.replace("\r", "").split("\n")]:
            assert line.strip() == "" or line.startswith("    ")
            assert line in func.__doc__


# -----------------------------------------------------------------------------
def test_bscr_help_CMD_pxr():
    """
    Test 'bscr help COMMAND'
    """
    pytest.debug_func()
    for fname in [x for x in dir(bscr.bscr) if x.startswith('bscr_')]:
        cname = fname.replace("bscr_", "")
        result = pexpect.run("bscr help {}".format(cname))
        assert result.strip() != ""
        func = getattr(bscr.bscr, fname)
        for line in [_ for _ in result.replace("\r", "").split("\n")]:
            assert line.strip() == "" or line.startswith("    ")
            assert line in func.__doc__


# -----------------------------------------------------------------------------
def test_bscr_help_command_dir(capsys):
    """
    Check the output of 'bscr help_commands'
    """
    pytest.debug_func()
    ignore = ["testhelp", "toolframe", "util", "version"]
    bscr.bscr.bscr_help_commands(**{})
    result, _ = capsys.readouterr()
    bscr_dir = U.dirname(bscr.__file__)
    for item in [x for x in glob.glob("{}/*.py".format(bscr_dir))
                 if '__' not in x]:
        name = U.basename(item.replace(".py", ""))
        if name not in ignore:
            assert name in result
    pass


# -----------------------------------------------------------------------------
def test_bscr_help_command_pxr(capsys):
    """
    Check the output of 'bscr help_commands'
    """
    pytest.debug_func()
    ignore = ["testhelp", "toolframe", "util", "version"]
    result = pexpect.run("bscr help_commands")
    bscr_dir = U.dirname(bscr.__file__)
    for item in [_ for _ in glob.glob("{}/*.py".format(bscr_dir))
                 if '__' not in _]:
        name = U.basename(item.replace(".py", ""))
        if name not in ignore:
            assert name in result
    pass


# -----------------------------------------------------------------------------
def test_bscr_location():
    """
    Check the location of the bscr module we're loading
    """
    pytest.debug_func()
    location = U.dirname(__file__, 2)
    bscr_loc = U.dirname(bscr.bscr.__file__, 2)
    assert location == bscr_loc


# -----------------------------------------------------------------------------
def test_bscr_roots_dir(capsys):
    """
    Report paths for bscr and its git repo
    """
    pytest.debug_func()
    bscr.bscr.bscr_roots(**{'d': False})
    result, _ = capsys.readouterr()
    assert "Traceback" not in result
    assert "bscr root:" in result
    assert "git root:" in result
    assert "in_bscr_repo:" in result


# -----------------------------------------------------------------------------
def test_bscr_roots_pxr():
    """
    Report paths for bscr and its git repo
    """
    pytest.debug_func()
    result = pexpect.run("bscr roots")
    assert "Traceback" not in result
    assert "bscr root:" in result
    assert "git root:" in result
    assert "in_bscr_repo:" in result


# -----------------------------------------------------------------------------
# def test_bscr_uninstall_dir(tmpdir):
#     """
#     Install bscr in a virtualenv so we can test uninstalling it
#     """
#     pytest.debug_func()
#     root = U.git_root()
#     with U.Chdir(tmpdir.strpath):
#         result = pexpect.run("virtualenv testenv")
#         activate_this = "testenv/bin/activate_this.py"
#         execfile(activate_this, dict(__file__=activate_this))
#         result = pexpect.run("pip install {}".format(root))
#         where = pexpect.which("bscr")
#         assert root not in where
#         assert tmpdir.strpath in where
#         pexpect.run("bscr uninstall")
#         pass


# -----------------------------------------------------------------------------
# def test_bscr_uninstall_pxr():
#     """
#     """
#     pytest.fail('construction')

"""
Tests for nvtool
"""
import os

import pexpect
import pytest

from bscr import nvtool

# -----------------------------------------------------------------------------
def test_nv_decap_dir(capsys):
    """
    'A:B:C:D' => 'B:C:D'
    ':foobar:heffalump' => 'foobar:heffalump'
    ''  => ''
    """
    pytest.debug_func()
    indata, exp = pathish("A, B, C, D"), pathish("B, C, D")
    nvtool.nv_decap(**{'VAR': indata})
    output, _ = capsys.readouterr()
    assert indata not in output
    assert exp in output


# -----------------------------------------------------------------------------
def test_nv_decap_pxr(capsys):
    """
    'A:B:C:D' => 'B:C:D'
    ':foobar:heffalump' => 'foobar:heffalump'
    ''  => ''
    """
    pytest.debug_func()
    indata, exp = pathish("A,B,C,D"), pathish("B,C,D")
    output = pexpect.run("nvtool decap {}".format(indata))
    assert indata not in output
    assert exp in output


# -----------------------------------------------------------------------------
def test_nv_dedup_dir(capsys):
    """
    'X:Y:Z:Z:Y' -> 'X:Y:Z'
    """
    pytest.debug_func()
    indata, exp = pathish('X,Y,Z,Z,Y'), pathish('X,Y,Z')
    nvtool.nv_dedup(**{'VAR': indata})
    output, _ = capsys.readouterr()
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_dedup_pxr(capsys):
    """
    'X:Y:Z:Z:Y' -> 'X:Y:Z'
    """
    pytest.debug_func()
    indata, exp = 'X:Y:Z:Z:Y', 'X:Y:Z'
    output = pexpect.run("nvtool dedup X:Y:Z:Z:Y")
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_dedup_show_dir(capsys):
    """
    'X:Y:Z:Z:Y' -> 'X:Y:Z'
    """
    pytest.debug_func()
    indata, exp = 'X:Y:Z:Z:Y', '   X\n   Y\n   Z'
    nvtool.nv_dedup_show(**{'VAR': indata})
    output, _ = capsys.readouterr()
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_dedup_show_pxr(capsys):
    """
    'X:Y:Z:Z:Y' -> '   X\r\n   Y\r\n   Z'
    """
    pytest.debug_func()
    indata, exp = ":".join(list("XYZZY")), "\r\n   ".join(list("XYZ"))
    output = pexpect.run("nvtool dedup --show X:Y:Z:Z:Y")
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_deped(capsys):
    """
    Test nv_deped()
    """
    pytest.fail('obsolete')
    nvtool_trial(nvtool.nv_deped, capsys, ['X:Y:Z:Z:Y'], 'X:Y:Z:Z')
    nvtool_trial(nvtool.nv_deped, capsys, ['X::Z::Y'], 'X::Z:')
    
# -----------------------------------------------------------------------------
def test_nv_stash_noval(capsys):
    """
    Attempt to stash an evar (environment variable) that has no value
    """
    pytest.fail('obsolete')
    nvtool_trial(nvtool.nv_stash, capsys, ['NOVAL'], 'No value for $NOVAL')
    
# -----------------------------------------------------------------------------
def test_nv_stash_val(capsys):
    """
    Attempt to stash an evar (environment variable) that has a value
    """
    pytest.fail('obsolete')
    nvtool_trial(nvtool.nv_stash,
                 capsys,
                 ['PATH'],
                 [_ + '\n' for _ in os.getenv('PATH').split(':')])
    
# -----------------------------------------------------------------------------
def test_nv_load(tmpdir, capsys):
    """
    Test nv_load
    """
    loadable = tmpdir.join('loadable')
    loadable.write(''.join(['foo\n', '$HOME\n', 'aardvark\n', ]))
    nvtool_trial(nvtool.nv_load,
                 capsys,
                 [loadable.strpath],
                 'foo:$HOME:aardvark')
    
# -----------------------------------------------------------------------------
def test_nv_show(capsys):
    """
    Test nv_show
    """
    nvtool_trial(nvtool.nv_show,
                 capsys,
                 ['PATH'],
                 ['\n   ' + _ for _ in os.getenv('PATH').split(':')])

# -----------------------------------------------------------------------------
def test_nv_remove_join(capsys):
    """
    Test nv_remove
    """
    pytest.debug_func()
    testin = 'beautiful:explicit:simple:complex:sparse'
    c_exp = 'beautiful:explicit:complex:sparse'
    s_exp = ['   \n' + _ for _ in c_exp.split(':')]
    nvtool_trial(nvtool.nv_remove, capsys, ['impl', testin], c_exp)

# -----------------------------------------------------------------------------
def test_nv_remove_show(capsys):
    """
    Test nv_remove
    """
    pytest.debug_func()
    testin = 'beautiful:explicit:simple:complex:sparse'
    c_exp = 'beautiful:explicit:complex:sparse'
    s_exp = ['   \n' + _ for _ in c_exp.split(':')]
    nvtool_trial(nvtool.nv_remove, capsys, ['-s', 'impl', testin], s_exp)

# -----------------------------------------------------------------------------
def test_nv_help(capsys):
    """
    Verify that util.dispatch warns that it's deprecated when nvtool runs
    """
    pytest.debug_func()
    cmdlist = "help decap dedup deped load remove show".split()
    result = pexpect.run("nvtool help")
    assert "nvtool examples:" in result
    for _ in cmdlist:
        assert _ in result

    for _ in cmdlist:
        result = pexpect.run("nvtool help {}".format(_))
        assert "Traceback" not in result
        assert _ in result

    
# -----------------------------------------------------------------------------
def pathish(seq):
    """
    Given a comma-separated list in string *seq*, compose and return a
    colon-separated list with whitespace squeezed out
    """
    return ":".join([_.strip() for _ in seq.split(",")])
    
# -----------------------------------------------------------------------------
def nvtool_trial(function, capsys, testin, expected):
    """
    Run an nvtool function on an input and verify the result
    """
    pytest.fail('obs')
    function(testin)
    stdo, _ = capsys.readouterr()
    if isinstance(expected, str):
        assert expected in stdo
    elif isinstance(expected, list):
        for item in expected:
            assert item in expected

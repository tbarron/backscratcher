"""
Tests for nvtool
"""
import os

import pytest

from bscr import nvtool

# -----------------------------------------------------------------------------
def test_nv_decap(capsys):
    """
    'A:B:C:D' => 'B:C:D'
    ':foobar:heffalump' => 'foobar:heffalump'
    ''  => ''
    """
    nvtool_trial(nvtool.nv_decap, capsys, ["A:B:C:D"], "B:C:D")
    nvtool_trial(nvtool.nv_decap,
                 capsys,
                 [":foobar:heffalump:"],
                 "foobar:heffalump:")
    nvtool_trial(nvtool.nv_decap, capsys, [""], "")

    path = os.getenv('PATH')
    headless = ':'.join(path.split(':')[1:])
    nvtool_trial(nvtool.nv_decap, capsys, [path], headless)

# -----------------------------------------------------------------------------
def test_nv_dedup(capsys):
    """
    'X:Y:Z:Z:Y' -> 'X:Y:Z'
    """
    nvtool_trial(nvtool.nv_dedup, capsys, ['X:Y:Z:Z:Y'], 'X:Y:Z')
    nvtool_trial(nvtool.nv_dedup, capsys, ['X::Z::Y'], 'X::Z:Y')

# -----------------------------------------------------------------------------
def test_nv_dedup_s(capsys):
    """
    -s option triggers a different output format
    """
    nvtool_trial(nvtool.nv_dedup,
                   capsys,
                   ['-s', 'X:Y:Z:Z:Y'],
                   '   X\n   Y\n   Z')
    nvtool_trial(nvtool.nv_dedup,
                   capsys,
                   ['-s', 'X::Z::Y'],
                   '   X\n   \n   Z\n   Y')

# -----------------------------------------------------------------------------
def test_nv_deped(capsys):
    """
    Test nv_deped()
    """
    nvtool_trial(nvtool.nv_deped, capsys, ['X:Y:Z:Z:Y'], 'X:Y:Z:Z')
    nvtool_trial(nvtool.nv_deped, capsys, ['X::Z::Y'], 'X::Z:')
    
# -----------------------------------------------------------------------------
def test_nv_stash_noval(capsys):
    """
    Attempt to stash an evar (environment variable) that has no value
    """
    nvtool_trial(nvtool.nv_stash, capsys, ['NOVAL'], 'No value for $NOVAL')
    
# -----------------------------------------------------------------------------
def test_nv_stash_val(capsys):
    """
    Attempt to stash an evar (environment variable) that has a value
    """
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
def nvtool_trial(function, capsys, testin, expected):
    """
    Run an nvtool function on an input and verify the result
    """
    function(testin)
    stdo, _ = capsys.readouterr()
    if isinstance(expected, str):
        assert expected in stdo
    elif isinstance(expected, list):
        for item in expected:
            assert item in expected

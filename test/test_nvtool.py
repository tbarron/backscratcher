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
def nvtool_trial(function, capsys, testin, expected):
    """
    Run an nvtool function on an input and verify the result
    """
    function(testin)
    stdo, _ = capsys.readouterr()
    assert expected in stdo

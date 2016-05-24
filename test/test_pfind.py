"""
Tests for pfind
"""
import copy
import os
import pdb
import re
import time

import py
import pytest

import tbx
from bscr import pfind

# -----------------------------------------------------------------------------
def test_everything(tmpdir, pfind_fx):
    """
    a test that finds everything
    """
    pytest.debug_func()
    opts = {'--name': '*', '--exclude': None, '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, pfind_fx.data.keys())

# -----------------------------------------------------------------------------
def test_some_noex(tmpdir, pfind_fx):
    """
    a test that finds some but not all without exclusion
    """
    pytest.debug_func()
    exp = list_minus(pfind_fx.data.keys(), ['ancient/two',
                                            'mature/four',
                                            'young$',
                                            'young/six',
                                            ])
    opts = {'--name': '*e*', '--exclude': None, '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, exp)

# -----------------------------------------------------------------------------
def test_nothing_noex(tmpdir, pfind_fx):
    """
    a test that finds nothing without exclusion
    """
    pytest.debug_func()
    opts = {'--name': '*z*', '--exclude': None, '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, [])

# -----------------------------------------------------------------------------
def test_everything_exdir(tmpdir, pfind_fx):
    """
    a test that finds everything and excludes a non-terminal path component
    """
    pytest.debug_func()
    exp = list_minus(pfind_fx.data.keys(), ['mature',
                                            'mature/three',
                                            'mature/four'])
    opts = {'--name': '*', '--exclude': 'mature', '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, exp)

# -----------------------------------------------------------------------------
def test_everything_exleaf(tmpdir, pfind_fx):
    """
    a test that finds everything and excludes a leaf
    """
    pytest.debug_func()
    exp = list_minus(pfind_fx.data.keys(), ['mature/four'])
    opts = {'--name': '*', '--exclude': 'four', '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, exp)

# -----------------------------------------------------------------------------
def test_everything_exall(tmpdir, pfind_fx):
    """
    a test that finds everything and excludes everything
    """
    pytest.debug_func()
    opts = {'--name': '*', '--exclude': 'ancient,mature,young,ref',
            '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, [])

# -----------------------------------------------------------------------------
def test_some_exdir(tmpdir, pfind_fx):
    """
    a test that finds some and excludes a non-terminal path component
    """
    pytest.debug_func()
    exp = list_minus(pfind_fx.data.keys(), ['ancient$',
                                            'mature$',
                                            'mature/three',
                                            'reference',
                                            'young.*'])
    opts = {'--name': '*o*', '--exclude': 'young', '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, exp)

# -----------------------------------------------------------------------------
def test_some_exleaf(tmpdir, pfind_fx):
    """
    a test that finds some and excludes a leaf
    """
    pytest.debug_func()
    exp = list_minus(pfind_fx.data.keys(), ['ancient$',
                                            'mature.*',
                                            'reference',
                                            'young/.*'])
    opts = {'--name': '*o*', '--exclude': 'ture', '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, exp)

# -----------------------------------------------------------------------------
def test_some_exall(tmpdir, pfind_fx):
    """
    a test that finds some and excludes it all
    """
    pytest.debug_func()
    opts = {'--name': '*o*', '--exclude': 'ref,anc,mature,young',
            '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, [])

# -----------------------------------------------------------------------------
def test_nothing_exall(tmpdir, pfind_fx):
    """
    a test that finds nothing and excludes everything
    """
    pytest.debug_func()
    opts = {'--name': 'aardvark', '--exclude': 'something',
            '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, [])

# -----------------------------------------------------------------------------
def test_parse_time():
    """
    parse_time() should take a date string in a variety of formats and return
    an epoch time
    """
    assert pfind.parse_time('2016.0101') == 1451624400.0
    assert pfind.parse_time('2015.1219.175455') == 1450565695.0

# -----------------------------------------------------------------------------
def test_parse_time_fail():
    """
    parse_time() should throw a ValueError if none of the formats match
    """
    pytest.debug_func()
    tdata = "01/17/2016"
    exp =  "time data {0} does not match any of the formats".format(tdata)
    with pytest.raises(ValueError) as err:
        assert pfind.parse_time(tdata) == 1451624400.0
    assert exp in str(err)

# -----------------------------------------------------------------------------
def test_age(tmpdir, pfind_fx):
    """
    find files based on age
    """
    pytest.fail('construction')
    opts = {'--name': 'aardvark',
            '--exclude': 'something',
            '--older': '2016.0101',
            '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, [])

# -----------------------------------------------------------------------------
def test_newer_ymd(tmpdir, pfind_fx):
    pytest.fail('construction')
    opts = {'--older': '2016.0101',
            '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, [])

# -----------------------------------------------------------------------------
def test_newer_path(tmpdir, pfind_fx):
    pytest.fail('construction')
    opts = {'--older': tmpdir.join('reference').strpath,
            '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, [])

# -----------------------------------------------------------------------------
def test_older_ymd(tmpdir, pfind_fx):
    pytest.fail('construction')
    opts = {'--older': '2016.0101',
            '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, [])

# -----------------------------------------------------------------------------
def test_older_path(tmpdir, pfind_fx):
    pytest.fail('construction')
    opts = {'--older': tmpdir.join('reference').strpath,
            '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, [])

# -----------------------------------------------------------------------------
def test_ownership(tmpdir, pfind_fx):
    """
    find files based on ownership
    """
    pytest.fail('construction')

# -----------------------------------------------------------------------------
def test_age_ref(tmpdir, pfind_fx):
    """
    find files based on age relative to a reference file
    """
    pytest.fail('construction')

# -----------------------------------------------------------------------------
def test_pfindNeedsTests():
    """
    Need tests for pfind
    """
    pytest.fail('pfind needs tests')

# -----------------------------------------------------------------------------
@pytest.fixture
def pfind_fx(tmpdir):
    """
    fixture to set up some directories and files

    We want some of them to be older and some newer than a specific date/time
    (2010.0101.000000) and some of them to older and some newer than a
    reference file (foo/reference)

    oldest files (one, two)
    2010.0101.000000
    more files (three, barx, gamma)
    foo/reference (2012.1231.235959)
    newest files (alpha, beta)
    """
    day = 24*3600
    anc = time.mktime(time.strptime('2010.0101.000000', '%Y.%m%d.%H%M%S'))
    mat = time.mktime(time.strptime('2012.1231.235959', '%Y.%m%d.%H%M%S'))
    pfind_fx.data = {'ancient': {'mtime': tbx.randomize(anc, -1, day),
                                 'atime': tbx.randomize(anc, -1, day),
                                 'dir': True},
                     'mature': {'mtime': tbx.randomize(mat-1, -1, day),
                                'atime': tbx.randomize(mat-1, -1, day),
                                'dir': True},
                     'young': {'mtime': tbx.randomize(mat+1, 1, day),
                               'atime': tbx.randomize(mat+1, 1, day),
                               'dir': True},
                     'ancient/one': {'mtime': tbx.randomize(anc, -1, day),
                                     'atime': tbx.randomize(anc, -1, day),
                                     'dir': False},
                     'ancient/two': {'mtime': tbx.randomize(anc, -1, day),
                                     'atime': tbx.randomize(anc, -1, day),
                                     'dir': False},
                     'mature/three': {'mtime': tbx.randomize(mat-1, -1, day),
                                     'atime': tbx.randomize(mat-1, -1, day),
                                     'dir': False
                                    },
                     'mature/four': {'mtime': tbx.randomize(mat-1, -1, day),
                                     'atime': tbx.randomize(mat-1, -1, day),
                                     'dir': False
                                    },
                     'young/five': {'mtime': tbx.randomize(mat+1, 1, day),
                                     'atime': tbx.randomize(mat+1, 1, day),
                                     'dir': False
                                    },
                     'young/six': {'mtime': tbx.randomize(mat+1, 1, day),
                                     'atime': tbx.randomize(mat+1, 1, day),
                                     'dir': False
                                    },
                     'reference': {'mtime': mat,
                                   'atime': mat,
                                   'dir': False
                                   }
        }

    for pstr in pfind_fx.data:
        path = tmpdir.join(pstr)
        path.ensure(dir=pfind_fx.data[pstr]['dir'])
        os.utime(path.strpath, (pfind_fx.data[pstr]['atime'],
                                pfind_fx.data[pstr]['mtime']))
        pfind_fx.data[pstr]['path'] = path
    return pfind_fx

# -----------------------------------------------------------------------------
def list_minus(keep, drop):
    """
    Subtract the items in list *drop* from list *keep*
    """
    rval = copy.deepcopy(keep)
    for expr in drop:
        for item in keep:
            if re.findall(expr, item):
                try:
                    rval.remove(item)
                except ValueError:
                    pass
    return rval

# -----------------------------------------------------------------------------
def validate_result(pfind_fx, result, expected):
    """
    Verify that *result* contains the keys in list *expected* with the same
    values as in *pfind_fx*.data
    """
    assert len(result) == len(expected)
    for key in expected:
        assert pfind_fx.data[key]['path'].strpath in result

"""
Tests for pfind
"""
import pytest
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
    opts = {'--name': '*e*', '--exclude': None, '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, ['one', 'three', 'beta'])

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
def test_everyting_exdir(tmpdir, pfind_fx):
    """
    a test that finds everything and excludes a non-terminal path component
    """
    pytest.debug_func()
    opts = {'--name': '*', '--exclude': 'foo', '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, ['d2', 'alpha', 'beta', 'gamma'])

# -----------------------------------------------------------------------------
def test_everyting_exdir(tmpdir, pfind_fx):
    """
    a test that finds everything and excludes a leaf
    """
    pytest.debug_func()
    opts = {'--name': '*', '--exclude': 'foo', '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, ['d2', 'alpha', 'beta', 'gamma'])

# -----------------------------------------------------------------------------
def test_everything_exall(tmpdir, pfind_fx):
    """
    a test that finds everything and excludes everything
    """
    pytest.debug_func()
    opts = {'--name': '*', '--exclude': 'foo,barx', '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, [])

# -----------------------------------------------------------------------------
def test_some_exdir(tmpdir, pfind_fx):
    """
    a test that finds some and excludes a non-terminal path component
    """
    pytest.debug_func()
    opts = {'--name': '*o*', '--exclude': 'barx', '<dir>': tmpdir.strpath}
    result = pfind.get_hitlist(path=tmpdir.strpath, opts=opts)
    validate_result(pfind_fx, result, ['d1', 'one', 'two'])

# -----------------------------------------------------------------------------
def test_some_exleaf(tmpdir, pfind_fx):
    """
    a test that finds some and excludes a leaf
    """
    pytest.fail('construction')

# -----------------------------------------------------------------------------
def test_some_exall(tmpdir, pfind_fx):
    """
    a test that finds some and excludes it all
    """
    pytest.fail('construction')

# -----------------------------------------------------------------------------
def test_nothing_exall(tmpdir, pfind_fx):
    """
    a test that finds nothing and excludes everything
    """
    pytest.fail('construction')

# -----------------------------------------------------------------------------
def test_age(tmpdir, pfind_fx):
    """
    find files based on age
    """
    pytest.fail('construction')

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
    """
    pfind_fx.data = {}
    d1 = pfind_fx.data['d1'] = tmpdir.join('foo').ensure(dir=True)
    pfind_fx.data['one'] = d1.join('one').ensure()
    pfind_fx.data['two'] = d1.join('two').ensure()
    pfind_fx.data['three'] = d1.join('three').ensure()
    d2 = pfind_fx.data['d2'] = tmpdir.join('barx').ensure(dir=True)
    pfind_fx.data['alpha'] = d2.join('alpha').ensure()
    pfind_fx.data['beta'] = d2.join('beta').ensure()
    pfind_fx.data['gamma'] = d2.join('gamma').ensure()
    return pfind_fx

# -----------------------------------------------------------------------------
def validate_result(pfind_fx, result, expected):
    """
    Verify that *result* contains the keys in list *expected* with the same
    values as in *pfind_fx*.data
    """
    assert len(result) == len(expected)
    for key in expected:
        assert pfind_fx.data[key].strpath in result

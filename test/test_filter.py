import pytest
from bscr import filter


# -----------------------------------------------------------------------------
def test_constructor():
    """
    Constructing a filter object
    """
    pytest.debug_func()
    xyz = filter.Filter()
    for attr in ['ignore', 'is_interesting', 'is_keepable',
                 'keep', 'ign', 'keepl', '__new__']:
        assert attr in dir(xyz)


# -----------------------------------------------------------------------------
def test_ignore():
    """
    Defining what is to be ignored
    """
    pytest.debug_func()
    x = filter.Filter()
    x.ignore('12345')
    assert '12345' in x.ign
    assert len(x.ign) == 1
    assert 'foobar' not in x.ign


# -----------------------------------------------------------------------------
def test_is_interesting():
    """
    Checking what is interesting
    """
    pytest.debug_func()
    x = filter.Filter()
    x.ignore('abccd')
    assert not x.is_interesting('one two abccd three four')
    assert x.is_interesting('foo bar wokka wokka')


# -----------------------------------------------------------------------------
def test_keep():
    """
    Defining what is keepable
    """
    pytest.debug_func()
    x = filter.Filter()
    x.keep('precious')
    assert 'precious' in x.keepl
    assert len(x.keepl) == 1
    assert 'frippery' not in x.keepl


# -----------------------------------------------------------------------------
def test_is_keepable():
    """
    After x.keep('foo'), strings containing 'foo' will be keepable while
    other strings will not be
    """
    pytest.debug_func()
    x = filter.Filter()
    x.keep('precious')
    assert(x.is_keepable('woo hoo! precious little got done today!'))
    assert(not x.is_keepable('not worth nuthin'))

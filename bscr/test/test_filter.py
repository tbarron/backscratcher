from bscr import filter
from nose.plugins.skip import SkipTest
from bscr import testhelp as th
import unittest


class TestFilter(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_constructor(self):
        """
        Constructing a filter object
        """
        xyz = filter.filter()
        for attr in ['ignore', 'is_interesting', 'is_keepable',
                     'keep', 'IGN', 'KEEP', '__new__']:
            assert(attr in dir(xyz))

    # -------------------------------------------------------------------------
    def test_ignore(self):
        """
        Defining what is to be ignored
        """
        x = filter.filter()
        x.ignore('12345')
        assert('12345' in x.IGN)
        assert(len(x.IGN) == 1)
        assert('foobar' not in x.IGN)

    # -------------------------------------------------------------------------
    def test_is_interesting(self):
        """
        Checking what is interesting
        """
        x = filter.filter()
        x.ignore('abccd')
        assert(not x.is_interesting('one two abccd three four'))
        assert(x.is_interesting('foo bar wokka wokka'))

    # -------------------------------------------------------------------------
    def test_keep(self):
        """
        Defining what is keepable
        """
        x = filter.filter()
        x.keep('precious')
        assert('precious' in x.KEEP)
        assert(len(x.KEEP) == 1)
        assert('frippery' not in x.KEEP)

    # -------------------------------------------------------------------------
    def test_is_keepable(self):
        """
        After x.keep('foo'), strings containing 'foo' will be keepable while
        other strings will not be
        """
        x = filter.filter()
        x.keep('precious')
        assert(x.is_keepable('woo hoo! precious little got done today!'))
        assert(not x.is_keepable('not worth nuthin'))

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.filter', __file__)

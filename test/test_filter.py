from bscr import filter
from bscr import testhelp as th
import unittest


class TestFilter(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_constructor(self):
        """
        Constructing a filter object
        """
        xyz = filter.Filter()
        for attr in ['ignore', 'is_interesting', 'is_keepable',
                     'keep', 'ign', 'keepl', '__new__']:
            assert(attr in dir(xyz))

    # -------------------------------------------------------------------------
    def test_ignore(self):
        """
        Defining what is to be ignored
        """
        x = filter.Filter()
        x.ignore('12345')
        assert('12345' in x.ign)
        assert(len(x.ign) == 1)
        assert('foobar' not in x.ign)

    # -------------------------------------------------------------------------
    def test_is_interesting(self):
        """
        Checking what is interesting
        """
        x = filter.Filter()
        x.ignore('abccd')
        assert(not x.is_interesting('one two abccd three four'))
        assert(x.is_interesting('foo bar wokka wokka'))

    # -------------------------------------------------------------------------
    def test_keep(self):
        """
        Defining what is keepable
        """
        x = filter.Filter()
        x.keep('precious')
        assert('precious' in x.keepl)
        assert(len(x.keepl) == 1)
        assert('frippery' not in x.keepl)

    # -------------------------------------------------------------------------
    def test_is_keepable(self):
        """
        After x.keep('foo'), strings containing 'foo' will be keepable while
        other strings will not be
        """
        x = filter.Filter()
        x.keep('precious')
        assert(x.is_keepable('woo hoo! precious little got done today!'))
        assert(not x.is_keepable('not worth nuthin'))

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.filter', __file__)

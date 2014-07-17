#!/usr/bin/env python
from bscr import dt
import time
from nose.plugins.skip import SkipTest
import unittest

# ---------------------------------------------------------------------------
class TestDt(unittest.TestCase):
    # -----------------------------------------------------------------------
    def default_fmt(self):
        return '%Y.%m%d %H:%M:%S'

    # -----------------------------------------------------------------------
    def do_both(self, testargs, expected):
        self.do_parse(testargs, expected)
        self.do_report(testargs, expected)

    # -----------------------------------------------------------------------
    def do_parse(self, testargs, expected):
        if type(expected) == int:
            a = dt.parse_whenspec(testargs)
            self.assertEqual(a, expected)
        elif type(expected) == str:
            got_exception = False
            try:
                a = dt.parse_whenspec(testargs)
            except StandardError, e:
                got_exception = True
                self.assertEqual(str(e), expected)
            assert(got_exception)
        else:
            raise StandardError("expected int or string, got '%s'" % a)

    # -----------------------------------------------------------------------
    def do_report(self, testargs, expected):
        if type(expected) == int:
            a = dt.report_date(self.default_fmt(), testargs)
            b = time.strftime(self.default_fmt(),
                              time.localtime(time.time() + expected))
            self.assertEqual(a, b)
        elif type(expected) == str:
            got_exception = False
            try:
                a = dt.report_date(self.default_fmt(), testargs)
            except StandardError, e:
                got_exception = True
                self.assertEqual(str(e), expected)
            assert(got_exception)
        else:
            raise StandardError("expected int or string, got '%s'" % a)

    # -----------------------------------------------------------------------
    def test_epoch(self):
        when = int(time.time()) - 300
        self.do_both(['%d' % when], -300)

    # -----------------------------------------------------------------------
    def test_today(self):
        self.do_both(['today'], 0)

    # -----------------------------------------------------------------------
    def test_tomorrow(self):
        self.do_both(['tomorrow'], 24 * 3600)

    # -----------------------------------------------------------------------
    def test_yesterday(self):
        self.do_both(['yesterday'], -24 * 3600)

    # -----------------------------------------------------------------------
    def test_next(self):
        self.do_both(['next'],
                       'next: expected unit or weekday, found nothing')

    # -----------------------------------------------------------------------
    def test_last(self):
        self.do_both(['last'],
                       'last: expected unit or weekday, found nothing')

    # -----------------------------------------------------------------------
    def test_plus5day(self):
        self.do_both(['+5', 'day'], 5 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_minus3month(self):
        self.do_both(['-3', 'month'], -3 * 30 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_tomorrow_plus2hour(self):
        self.do_both(['tomorrow', '2', 'hour'], (24+2) * 3600)

    # -----------------------------------------------------------------------
    def test_yesterday_plus7week(self):
        self.do_both(['yesterday', '7', 'week'], (7 * 7 - 1) * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_next_minus3(self):
        self.do_both(['next', '-3', 'hour'],
                       'next: expected unit or weekday, got number')

    # -----------------------------------------------------------------------
    def test_last_plus2day(self):
        self.do_both(['last', '+2', 'day'],
                       'last: expected unit or weekday, got number')

    # -----------------------------------------------------------------------
    def test_minus3hour(self):
        self.do_both(['-3', 'hour'], -3 * 3600)

    # -----------------------------------------------------------------------
    def test_plus2day(self):
        self.do_both(['+2', 'day'], 2 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_next_day(self):
        self.do_both(['next', 'day'], 24 * 3600)

    # -----------------------------------------------------------------------
    def test_next_monday(self):
        self.do_both(['next', 'monday'], dt.time_to('monday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_tuesday(self):
        self.do_both(['last', 'tuesday'], dt.time_to('tuesday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_wednesday(self):
        self.do_both(['next', 'wednesday'], dt.time_to('wednesday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_thursday(self):
        self.do_both(['last', 'thursday'], dt.time_to('thursday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_friday(self):
        self.do_both(['next', 'friday'], dt.time_to('friday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_saturday(self):
        self.do_both(['last', 'saturday'], dt.time_to('saturday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_sunday(self):
        self.do_both(['next', 'sunday'], dt.time_to('sunday', 'next'))

    # -------------------------------------------------------------------------
    def test_dt_help(self):
        """
        Verify that 'dt --help' does the right thing
        """
        raise SkipTest(">>> WRITE ME <<<")
    
    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        raise SkipTest(">>> WRITE ME <<<")
        
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()


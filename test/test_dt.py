#!/usr/bin/env python
import dt
import time
import unittest

# ---------------------------------------------------------------------------
class TestDt(unittest.TestCase):
    # -----------------------------------------------------------------------
    def default_fmt(self):
        return '%Y.%m%d %H:%M:%S'

    # -----------------------------------------------------------------------
    def both_test(self, testargs, expected):
        self.parse_test(testargs, expected)
        self.report_test(testargs, expected)

    # -----------------------------------------------------------------------
    def parse_test(self, testargs, expected):
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
    def report_test(self, testargs, expected):
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
        self.both_test(['%d' % when], -300)

    # -----------------------------------------------------------------------
    def test_today(self):
        self.both_test(['today'], 0)

    # -----------------------------------------------------------------------
    def test_tomorrow(self):
        self.both_test(['tomorrow'], 24 * 3600)

    # -----------------------------------------------------------------------
    def test_yesterday(self):
        self.both_test(['yesterday'], -24 * 3600)

    # -----------------------------------------------------------------------
    def test_next(self):
        self.both_test(['next'],
                       'next: expected unit or weekday, found nothing')

    # -----------------------------------------------------------------------
    def test_last(self):
        self.both_test(['last'],
                       'last: expected unit or weekday, found nothing')

    # -----------------------------------------------------------------------
    def test_plus5day(self):
        self.both_test(['+5', 'day'], 5 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_minus3month(self):
        self.both_test(['-3', 'month'], -3 * 30 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_tomorrow_plus2hour(self):
        self.both_test(['tomorrow', '2', 'hour'], (24+2) * 3600)

    # -----------------------------------------------------------------------
    def test_yesterday_plus7week(self):
        self.both_test(['yesterday', '7', 'week'], (7 * 7 - 1) * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_next_minus3(self):
        self.both_test(['next', '-3', 'hour'],
                       'next: expected unit or weekday, got number')

    # -----------------------------------------------------------------------
    def test_last_plus2day(self):
        self.both_test(['last', '+2', 'day'],
                       'last: expected unit or weekday, got number')

    # -----------------------------------------------------------------------
    def test_minus3hour(self):
        self.both_test(['-3', 'hour'], -3 * 3600)

    # -----------------------------------------------------------------------
    def test_plus2day(self):
        self.both_test(['+2', 'day'], 2 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_next_day(self):
        self.both_test(['next', 'day'], 24 * 3600)

    # -----------------------------------------------------------------------
    def test_next_monday(self):
        self.both_test(['next', 'monday'], dt.time_to('monday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_tuesday(self):
        self.both_test(['last', 'tuesday'], dt.time_to('tuesday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_wednesday(self):
        self.both_test(['next', 'wednesday'], dt.time_to('wednesday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_thursday(self):
        self.both_test(['last', 'thursday'], dt.time_to('thursday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_friday(self):
        self.both_test(['next', 'friday'], dt.time_to('friday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_saturday(self):
        self.both_test(['last', 'saturday'], dt.time_to('saturday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_sunday(self):
        self.both_test(['next', 'sunday'], dt.time_to('sunday', 'next'))

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()


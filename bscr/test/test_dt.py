#!/usr/bin/env python
import bscr
from bscr import dt
from bscr import testhelp as th
from bscr import util as U
import pexpect
import time
import unittest


# ---------------------------------------------------------------------------
class TestDt(th.HelpedTestCase):
    # -----------------------------------------------------------------------
    def default_fmt(self):
        """
        Defines the default date/time format
        """
        return '%Y.%m%d %H:%M:%S'

    # -----------------------------------------------------------------------
    def do_both(self, testargs, expected):
        """
        Test both parsing and date reporting
        """
        self.do_parse(testargs, expected)
        self.do_report(testargs, expected)

    # -----------------------------------------------------------------------
    def do_parse(self, testargs, expected):
        """
        Test parsing a list of command line arguments
        """
        if type(expected) == int:
            a = dt.parse_whenspec(testargs)
            self.assertEqual(a, expected)
        elif type(expected) == str:
            self.assertRaisesMsg(bscr.Error,
                                 expected,
                                 dt.parse_whenspec,
                                 testargs)
        else:
            self.fail("expected int or string, got '%s'" % a)

    # -----------------------------------------------------------------------
    def do_report(self, testargs, expected):
        """
        Test report_date()
        """
        if type(expected) == int:
            a = dt.report_date(self.default_fmt(), testargs)
            b = time.strftime(self.default_fmt(),
                              time.localtime(time.time() + expected))
            self.assertEqual(a, b)
        elif type(expected) == str:
            self.assertRaisesMsg(bscr.Error,
                                 expected,
                                 dt.report_date,
                                 self.default_fmt(),
                                 testargs)
        else:
            self.fail("expected int or string, got '%s'" % a)

    # -----------------------------------------------------------------------
    def test_epoch(self):
        """
        offset seconds
        """
        when = int(time.time()) - 300
        self.do_both(['%d' % when], -300)

    # -----------------------------------------------------------------------
    def test_today(self):
        """
        Today
        """
        self.do_both(['today'], 0)

    # -----------------------------------------------------------------------
    def test_tomorrow(self):
        """
        Tomorrow
        """
        self.do_both(['tomorrow'], 24 * 3600)

    # -----------------------------------------------------------------------
    def test_yesterday(self):
        """
        Yesterday
        """
        self.do_both(['yesterday'], -24 * 3600)

    # -----------------------------------------------------------------------
    def test_next(self):
        """
        Error
        """
        self.do_both(['next'],
                     'next: expected unit or weekday, found nothing')

    # -----------------------------------------------------------------------
    def test_last(self):
        """
        Error
        """
        self.do_both(['last'],
                     'last: expected unit or weekday, found nothing')

    # -----------------------------------------------------------------------
    def test_last_week(self):
        """
        relative week
        """
        self.do_both(['last', 'week'], -7 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_next_week(self):
        """
        relative week
        """
        self.do_both(['next', 'week'], 7 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_plus5day(self):
        """
        offset days
        """
        self.do_both(['+5', 'day'], 5 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_minus3month(self):
        """
        month offset
        """
        self.do_both(['-3', 'month'], -3 * 30 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_tomorrow_plus2hour(self):
        """
        multiple offsets
        """
        self.do_both(['tomorrow', '2', 'hour'], (24+2) * 3600)

    # -----------------------------------------------------------------------
    def test_yesterday_plus7week(self):
        """
        multiple offsets
        """
        self.do_both(['yesterday', '7', 'week'], (7 * 7 - 1) * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_next_minus3(self):
        """
        Hour offsest
        """
        self.do_both(['next', '-3', 'hour'],
                     'next: expected unit or weekday, got number')

    # -----------------------------------------------------------------------
    def test_last_plus2day(self):
        """
        Day offset
        """
        self.do_both(['last', '+2', 'day'],
                     'last: expected unit or weekday, got number')

    # -----------------------------------------------------------------------
    def test_minus3hour(self):
        """
        Computing by hour offset
        """
        self.do_both(['-3', 'hour'], -3 * 3600)

    # -----------------------------------------------------------------------
    def test_plus2day(self):
        """
        Computing date by day offset
        """
        self.do_both(['+2', 'day'], 2 * 24 * 3600)

    # -----------------------------------------------------------------------
    def test_next_day(self):
        """
        Computing relative day -- tomorrow
        """
        self.do_both(['next', 'day'], 24 * 3600)

    # -----------------------------------------------------------------------
    def test_next_monday(self):
        """
        Computing relative weekday
        """
        self.do_both(['next', 'monday'], dt.time_to('monday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_tuesday(self):
        """
        Computing relative weekday
        """
        self.do_both(['last', 'tuesday'], dt.time_to('tuesday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_wednesday(self):
        """
        Computing relative weekday
        """
        self.do_both(['next', 'wednesday'], dt.time_to('wednesday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_thursday(self):
        """
        Computing relative weekday
        """
        self.do_both(['last', 'thursday'], dt.time_to('thursday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_friday(self):
        """
        Computing relative weekday
        """
        self.do_both(['next', 'friday'], dt.time_to('friday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_saturday(self):
        """
        Computing relative weekday
        """
        self.do_both(['last', 'saturday'], dt.time_to('saturday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_sunday(self):
        """
        Computing relative weekday
        """
        self.do_both(['next', 'sunday'], dt.time_to('sunday', 'next'))

    # -------------------------------------------------------------------------
    def test_dt_help(self):
        """
        Verify that 'dt --help' does the right thing
        """
        self.assertOptionHelp("dt", "playing with dates")

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.dt', __file__)

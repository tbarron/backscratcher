import bscr
from bscr import dt
from bscr import testhelp as th
import pexpect
import pytest
import time


# -----------------------------------------------------------------------------
def test_dt_help():
    """
    Verify that 'dt --help' does the right thing
    """
    pytest.debug_func()
    result = pexpect.run("dt --help")
    assert "playing with dates" in result
    assert "Options:" in result
    assert "--help" in result


# -----------------------------------------------------------------------------
def test_epoch(fx_both):
    """
    offset seconds
    """
    pytest.debug_func()
    fx_both.expected = -300
    argl = [str(int(time.time()) + fx_both.expected)]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_last(fx_botherr):
    """
    'last' as the argument should throw an exception
    """
    pytest.debug_func()
    fx_botherr.exp = 'last: expected unit or weekday, found nothing'
    argl = ["last"]
    with pytest.raises(bscr.Error) as fx_botherr.perr:
        dt.parse_whenspec(argl)
    with pytest.raises(bscr.Error) as fx_botherr.rerr:
        dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_last_plus2day(fx_botherr):
    """
    'last +2 day' as the argument should throw an exception
    """
    pytest.debug_func()
    fx_botherr.exp = 'last: expected unit or weekday, got number'
    argl = ["last", "+2", "day"]
    with pytest.raises(bscr.Error) as fx_botherr.perr:
        dt.parse_whenspec(argl)
    with pytest.raises(bscr.Error) as fx_botherr.rerr:
        dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_last_week(fx_both):
    """
    last week
    """
    pytest.debug_func()
    fx_both.expected = -7 * 24 * 3600
    argl = ["last", "week"]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_minus3month(fx_both):
    """
    three months ago
    """
    pytest.debug_func()
    fx_both.expected = -3 * 30 * 24 * 3600
    argl = ["-3", "month"]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_next(fx_botherr):
    """
    'next' as the argument should throw an exception
    """
    pytest.debug_func()
    fx_botherr.exp = 'next: expected unit or weekday, found nothing'
    argl = ["next"]
    with pytest.raises(bscr.Error) as fx_botherr.perr:
        dt.parse_whenspec(argl)
    with pytest.raises(bscr.Error) as fx_botherr.rerr:
        dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_next_minus3(fx_botherr):
    """
    """
    pytest.debug_func()
    fx_botherr.exp = 'next: expected unit or weekday, got number'
    argl = ["next", "-3", "hour"]
    with pytest.raises(bscr.Error) as fx_botherr.perr:
        dt.parse_whenspec(argl)
    with pytest.raises(bscr.Error) as fx_botherr.rerr:
        dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_next_week(fx_both):
    """
    next week
    """
    pytest.debug_func()
    fx_both.expected = 7 * 24 * 3600
    argl = ["next", "week"]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_plus5day(fx_both):
    """
    five days in the future
    """
    pytest.debug_func()
    fx_both.expected = 5 * 24 * 3600
    argl = ["+5", "day"]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_today(fx_both):
    """
    today
    """
    pytest.debug_func()
    fx_both.expected = 0
    argl = ["today"]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_tomorrow(fx_both):
    """
    tomorrow
    """
    fx_both.expected = 24 * 3600
    argl = ["tomorrow"]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_tomorrow_plus2hr(fx_both):
    """
    tomorrow
    """
    fx_both.expected = (24+2) * 3600
    argl = ["tomorrow", "2", "hour"]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_yesterday(fx_both):
    """
    yesterday
    """
    fx_both.expected = -24 * 3600
    argl = ["yesterday"]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_yesterday_plus7wk(fx_both):
    """
    yesterday
    """
    fx_both.expected = (7 * 7 - 1) * 24 * 3600
    argl = ["yesterday", "7", "week"]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def default_format():
    """
    The default date/time/format
    """
    return "%Y.%m%d %H:%M:%S"


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_botherr(request):
    """
    Fixture that expects exceptions and checks the error they contain
    """
    fx_botherr.exp = fx_botherr.perr = fx_botherr.rerr = None
    yield fx_botherr
    assert fx_botherr.exp in str(fx_botherr.perr)
    assert fx_botherr.exp in str(fx_botherr.rerr)


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_both():
    """
    Fixture for successful tests. That is, tests that don't involve exceptions
    being thrown.
    """
    fx_both.expected = None
    fx_both.reported = None
    fx_both.input = None
    yield fx_both
    assert fx_both.expected == fx_both.parsed
    rptexp = time.strftime(default_format(), time.localtime(time.time() +
                                                            fx_both.expected))
    assert fx_both.reported == rptexp


# -----------------------------------------------------------------------------
def test_standalone():
    """
    Make these tests stand-alone
    """
    pytest.fail("Make {} tests stand-alone".format(__file__))


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
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.dt', __file__)

import bscr
from bscr import dt
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
def test_last_saturday(fx_both):
    """
    Computing relative weekday to last saturday
    """
    pytest.debug_func()
    argl = ["last", "saturday"]
    fx_both.expected = dt.time_to(argl[1], argl[0])
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_last_thursday(fx_both):
    """
    Computing relative weekday to last thursday
    """
    pytest.debug_func()
    argl = ["last", "thursday"]
    fx_both.expected = dt.time_to(argl[1], argl[0])
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_last_tuesday(fx_both):
    """
    Computing relative weekday to last tuesday
    """
    pytest.debug_func()
    argl = ["last", "tuesday"]
    fx_both.expected = dt.time_to(argl[1], argl[0])
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


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
def test_minus3hour(fx_both):
    """
    three months ago
    """
    pytest.debug_func()
    fx_both.expected = -3 * 3600
    argl = ["-3", "hour"]
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
def test_next_day(fx_both):
    """
    next day
    """
    pytest.debug_func()
    fx_both.expected = 24 * 3600
    argl = ["next", "day"]
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_next_friday(fx_both):
    """
    Computing relative weekday to next friday
    """
    pytest.debug_func()
    argl = ["next", "friday"]
    fx_both.expected = dt.time_to(argl[1], argl[0])
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_next_monday(fx_both):
    """
    Computing relative weekday to next monday
    """
    pytest.debug_func()
    argl = ["next", "monday"]
    fx_both.expected = dt.time_to(argl[1], argl[0])
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


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
def test_next_sunday(fx_both):
    """
    Computing relative weekday to last sunday
    """
    pytest.debug_func()
    argl = ["next", "sunday"]
    fx_both.expected = dt.time_to(argl[1], argl[0])
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


# -----------------------------------------------------------------------------
def test_next_wednesday(fx_both):
    """
    Computing relative weekday to next wednesday
    """
    pytest.debug_func()
    argl = ["next", "wednesday"]
    fx_both.expected = dt.time_to(argl[1], argl[0])
    fx_both.parsed = dt.parse_whenspec(argl)
    fx_both.reported = dt.report_date(default_format(), argl)


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
def test_plus2day(fx_both):
    """
    two days in the future
    """
    pytest.debug_func()
    fx_both.expected = 2 * 24 * 3600
    argl = ["+2", "day"]
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

    2017-11-13: Adding fx_both.basetime because without it, tests that use this
    fixture can fail whenif the time.time() call in the test and the
    time.time() call in this fixture don't fall within the same second. To
    ensure that doesn't happen, the test can set fx_both.basetime and we'll use
    that as the starting point here.
    """
    fx_both.expected = None
    fx_both.reported = None
    fx_both.input = None
    yield fx_both
    assert fx_both.expected == fx_both.parsed
    if not hasattr(fx_both, "basetime"):
        fx_both.basetime = time.time()
    rptexp = time.strftime(default_format(), time.localtime(fx_both.basetime +
                                                            fx_both.expected))
    assert fx_both.reported == rptexp

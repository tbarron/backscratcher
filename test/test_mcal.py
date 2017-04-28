"""
Tests for mcal
"""
import time

import pytest

from bscr import mcal


# -----------------------------------------------------------------------------
def test_mcal_first_day():
    """
    Verify that first day returns the right thing
    """
    pytest.debug_func()
    validate_first_day(1999, 3, 0)
    validate_first_day(2003, 7, 1)
    validate_first_day(2003, 1, 2)
    validate_first_day(2003, 5, 3)


# -----------------------------------------------------------------------------
def test_mcal_gen_month():
    """
    Verify that gen_month puts out what we expect
    """
    pytest.debug_func()
    result = mcal.gen_month(1999, 2)
    assert isinstance(result, list)
    assert len(result) == 8
    assert " Mo Tu We Th Fr Sa Su" in result
    assert "  1  2  3  4  5  6  7" in result
    assert "  8  9 10 11 12 13 14" in result
    assert " 15 16 17 18 19 20 21" in result
    assert " 22 23 24 25 26 27 28" in result


# -----------------------------------------------------------------------------
def test_mcal_main_h(capsys):
    """
    mcal.main([-h]) should report the help message. I think docopt writes this
    directly to stdout so we'll have to use capsys.
    """
    pytest.debug_func()
    exp = '\n'.join(['Usage:',
                     '    mcal.py [-y <year>] [-m <month>] [-w] [-d]',
                     '',
                     'Options:',
                     '    -d          Run the debugger',
                     '    -y <year>   Year of calendar',
                     '    -m <month>  Month of calendar',
                     '    -w          Print a wide calendar showing two '
                     'months',
                     ])
    with pytest.raises(SystemExit):
        mcal.main(['-h'])
    stdo, _ = capsys.readouterr()
    assert exp.strip() == stdo.strip()


# -----------------------------------------------------------------------------
def test_mcal_main_noarg():
    """
    mcal.main([]) should return a string containing the current month
    """
    pytest.debug_func()
    actual = mcal.main([])
    assert time.strftime("%Y.%m") in actual
    assert "  1" in actual
    assert " 28" in actual


# -----------------------------------------------------------------------------
def test_mcal_main_y():
    """
    mcal.main(['-y <year>']) should return a string containing the current
    month in the specified year
    """
    pytest.debug_func()
    actual = mcal.main(['-y 2001'])
    assert time.strftime("2001.%m") in actual
    assert "  1" in actual
    assert " 28" in actual


# -----------------------------------------------------------------------------
def test_mcal_main_ym():
    """
    mcal.main(['-y <year>', '-m <month>']) should return a string containing
    the specified month and year
    """
    pytest.debug_func()
    exp = '\n'.join(['       1999.02       ',
                     ' Mo Tu We Th Fr Sa Su',
                     '  1  2  3  4  5  6  7',
                     '  8  9 10 11 12 13 14',
                     ' 15 16 17 18 19 20 21',
                     ' 22 23 24 25 26 27 28',
                     '                     ',
                     '                     ',
                     ])
    actual = mcal.main(['-y 1999', '-m 2'])
    assert actual == exp


# -----------------------------------------------------------------------------
def test_mcal_main_m():
    """
    mcal.main(['-m <month>']) should return a string containing the specified
    month in the current year
    """
    pytest.debug_func()
    actual = mcal.main(['-m 9'])
    assert time.strftime("%Y.09") in actual
    assert "  1" in actual
    assert " 28" in actual


# -----------------------------------------------------------------------------
def test_mcal_main_w():
    """
    mcal.main(['-w']) should return a string containing the current month and
    next month
    """
    pytest.debug_func()
    actual = mcal.main(['-w'])
    assert time.strftime("%Y.%m") in actual
    now = time.localtime()
    assert time.strftime("%Y.%m", (now.tm_year, now.tm_mon+1, now.tm_mday,
                                   0, 0, 0, 0, 0, 0))
    assert "  1" in actual
    assert " 28" in actual
    assert " 31" in actual


# -----------------------------------------------------------------------------
def test_mcal_main_yw():
    """
    mcal.main(['-y <year>', '-w']) should return a string containing the
    current and next month in the specified year
    """
    pytest.debug_func()
    this_month = int(time.strftime("%m"))
    actual = mcal.main(['-y 2035', '-w'])
    assert "2035.{0:02}".format(this_month) in actual
    succy, succm = mcal.next_month(2035, this_month)
    assert "{0}.{1:02}".format(succy, succm) in actual
    assert "  1" in actual
    assert " 28" in actual
    assert " 31" in actual


# -----------------------------------------------------------------------------
def test_mcal_main_ymw():
    """
    mcal.main(['-y <year>', '-m <month>', '-w']) should return a string
    containing the specified and following month in the specified year
    """
    pytest.debug_func()
    year = 1902
    mon = 12
    actual = mcal.main(['-y {0}'.format(year), '-m {0}'.format(mon), '-w'])
    assert "{0}.{1:02}".format(year, mon) in actual
    syr, smn = mcal.next_month(year, mon)
    assert "{0}.{1:02}".format(syr, smn) in actual
    assert "  1" in actual
    assert " 28" in actual
    assert " 31" in actual


# -----------------------------------------------------------------------------
def test_mcal_main_mw():
    """
    mcal.main(['-m <month>', '-w']) should return a string containing the
    specified and following month in the current year
    """
    pytest.debug_func()
    year = int(time.strftime('%Y'))
    mon = 12
    actual = mcal.main(['-m {0}'.format(mon), '-w'])
    assert "{0}.{1:02}".format(year, mon) in actual
    syr, smn = mcal.next_month(year, mon)
    assert "{0}.{1:02}".format(syr, smn) in actual
    assert "  1" in actual
    assert " 28" in actual
    assert " 31" in actual


# -----------------------------------------------------------------------------
def test_mcal_next_day():
    """
    Need tests for mcal
    """
    pytest.debug_func()
    validate_next_day('2003.1231', '2004.0101')
    validate_next_day('2004.0131', '2004.0201')
    validate_next_day('2004.0228', '2004.0229')
    validate_next_day('2004.0229', '2004.0301')
    validate_next_day('2004.0331', '2004.0401')
    validate_next_day('2004.0430', '2004.0501')
    validate_next_day('2004.0531', '2004.0601')
    validate_next_day('2004.0630', '2004.0701')
    validate_next_day('2004.0731', '2004.0801')
    validate_next_day('2004.0831', '2004.0901')
    validate_next_day('2004.0930', '2004.1001')
    validate_next_day('2004.1031', '2004.1101')
    validate_next_day('2004.1130', '2004.1201')
    validate_next_day('2004.1231', '2005.0101')


# -----------------------------------------------------------------------------
def test_mcal_next_month():
    """
    Test mcal.next_month
    """
    pytest.debug_func()
    assert mcal.next_month(2003, 12) == (2004, 1)
    for mon in range(12):
        assert mcal.next_month(2004, mon) == (2004, mon+1)
    assert mcal.next_month(2004, 12) == (2005, 1)


# -----------------------------------------------------------------------------
def test_mcal_title():
    """
    Verify that title puts out what we expect
    """
    pytest.debug_func()
    result = mcal.title(1999, 2)
    assert result == '       1999.02       '


# -----------------------------------------------------------------------------
def validate_first_day(year, month, wday):
    """
    validate the result of mcal.first_day
    """
    fday = mcal.first_day(year, month)
    assert fday.tm_wday == wday


# -----------------------------------------------------------------------------
def validate_next_day(pred, succ):
    """
    validate the result of mcal.next_day
    """
    ptm = time.strptime(pred, '%Y.%m%d')
    nday = mcal.next_day(ptm)
    result = time.strftime('%Y.%m%d', nday)
    assert result == succ

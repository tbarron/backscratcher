import optparse
import os
import re
import time

import pytest

from bscr import util as U
from bscr import workrpt as wr


# -------------------------------------------------------------------------
def test_daily_subtotal(tmpdir, fx_stddata, fx_wrprep):
    """
    Test that generating a report with dayflag=True produces non-zero daily
    subtotals when appropriate
    """
    pytest.skip()
    pytest.debug_func()
    opts = optparse.Values({'filename': fx_stddata.file.strpath,
                            'match_regexp': 'admin',
                            'start': '2009.0721',
                            'end': '2009.0724',
                            'dayflag': True})
    r = wr.write_report(opts, True)
    subtotal = 0
    for line in r.split('\n'):
        (text, duration) = parse_report_line(line)
        if 'Total:' in text:
            assert duration == subtotal
            subtotal = 0
        else:
            subtotal += duration


# -------------------------------------------------------------------------
def test_match(tmpdir, fx_stddata, fx_wrprep):
    """
    Test that option --match/-m matches specific lines from input file
    """
    pytest.debug_func()
    opts = optparse.Values({'filename': fx_stddata.file.strpath,
                            'match_regexp': 'admin',
                            'start': '2009.0721',
                            'end': '2009.0724',
                            'dayflag': False})
    r = wr.write_report_regexp(opts, True)
    assert_includes(r, '13:35:14')
    assert_includes(r, '(13.6)')
    assert_excludes(r, 'vacation')


# -------------------------------------------------------------------------
def test_rgx_end(fx_stddata, fx_wrprep):
    """
    Verify that -m and -e work properly together
    """
    pytest.debug_func()
    opts = optparse.Values({'filename': fx_stddata.file.strpath,
                            'match_regexp': 'admin',
                            'start': '2009.0701',
                            'end': '2009.0723',
                            'dayflag': False})
    r = wr.write_report_regexp(opts, True)
    assert_includes(r, 'admin: read mail')
    assert_includes(r, 'admin: hpss')
    assert_includes(r, 'admin: liason')
    assert_includes(r, 'admin: setup')
    assert_excludes(r, 'admin: other stuff')


# -------------------------------------------------------------------------
def test_rgx_start(fx_stddata, fx_wrprep):
    """
    Verify that -m and -s work properly together
    """
    pytest.debug_func()
    opts = optparse.Values({'filename': fx_stddata.file.strpath,
                            'match_regexp': 'admin',
                            'start': '2009.0722',
                            'end': '2009.0731',
                            'dayflag': False})
    r = wr.write_report_regexp(opts, True)
    assert_includes(r, 'admin: read mail')
    assert_includes(r, 'admin: hpss')
    assert_excludes(r, 'admin: liason')
    assert_excludes(r, 'admin: setup')
    assert_includes(r, 'admin: other stuff')


# -------------------------------------------------------------------------
def test_rgx_start_end(fx_stddata, fx_wrprep):
    """
    Verify that -m, -s, and -e all work properly together
    """
    pytest.debug_func()
    opts = optparse.Values({'filename': fx_stddata.file.strpath,
                            'match_regexp': 'admin',
                            'start': '2009.0722',
                            'end': '2009.0723',
                            'dayflag': False})
    r = wr.write_report_regexp(opts, True)
    assert_includes(r, 'admin: read mail')
    assert_includes(r, 'admin: hpss')
    assert_excludes(r, 'admin: liason')
    assert_excludes(r, 'admin: setup')
    assert_excludes(r, 'admin: other stuff')


# -------------------------------------------------------------------------
def test_rounding(tmpdir, fx_stddata, fx_wrprep):
    """
    Test that calculations round properly. There are five types of duration
    number in this report:

        line item hms - HH:MM:SS for a specific task
        subtotal hms - HH:MM:SS for a category of tasks
        subtotal fp - floating point hour.tenth version of subtotal hms
        total hms - HH:MM:SS total duration at the bottom
        total fp - floating point hour.tenth version of total hms

    The issue is that sometimes when we add up the subtotal hms values, the
    result is larger than the sum of all the subtotal fp values. I want the
    total fp to represent the sum of the subtotal fp's, as PALS does.
    """
    pytest.debug_func()
    opts = optparse.Values({'filename': fx_stddata.file.strpath,
                            'start': '2009.0721',
                            'end': '2009.0724',
                            'dayflag': False})
    r = wr.write_report(opts, True)
    htot = stot = fpsum = 0
    for line in r.split('\n'):
        # zap: result of parsing the string
        # hms: what HH:MM:SS matched
        # fp: what [\d.]+ matched
        # stot: total of lines
        # htot: total in header
        zap = re.findall('(\d\d:\d\d:\d\d)( \(([\d.]+)\))?', line)
        if 0 < len(zap):
            (hms, _, fp) = zap[0]
            if 'Total:' in line:
                # here we verify that the total fp matchs the sum of the
                # subtotal fp values even though the sum of the hms values
                # would be larger
                htot = float(fp)
                assert fp_close(htot, fpsum, 0.001)
                assert not fp_close(htot, phms(hms), 0.05)
            elif fp != '':
                # here we handle a subtotal header line
                if 0 < stot:
                    assert fp_close(stot, htot, 0.05)
                    stot = 0
                htot = float(fp)
                assert fp_close(htot, phms(hms), 0.05)
                fpsum += htot
            else:
                # here we handle a detail line
                stot += phms(hms)
        pass


# -------------------------------------------------------------------------
def test_standalone_category(tmpdir, fx_stddata, fx_wrprep):
    """
    test standalone categories like 'vacation' and 'holiday'
    """
    pytest.debug_func()
    opts = optparse.Values({'filename': fx_stddata.file.strpath,
                            'start': '2009.0721',
                            'end': '2009.0724',
                            'dayflag': False})
    r = wr.write_report(opts, True)
    assert_includes(r, '27:58:49')


# -----------------------------------------------------------------------------
def test_start_date_missing(tmpdir, fx_stddata, fx_wrprep):
    """
    Calculate a week when the first few dates are missing
    """
    opts = optparse.Values({'filename': fx_stddata.file.strpath,
                            'start': '2009.0718',
                            'end': '2009.0722',
                            'dayflag': False})
    r = wr.write_report(opts, True)
    assert_excludes(r, '24.0')
    assert_excludes(r, '2009.0719')
    assert_includes(r, '16:29:06 (16.4)')


# -----------------------------------------------------------------------------
def test_workrpt_order(tmpdir, fx_wrprep):
    """
    Times or dates out of order should produce SystemExit exception
    """
    xyz = tmpdir.join('XYZ')
    xyz.write('\n'.join(['2015-01-07 10:00:00 first task',
                         '2015-01-07 10:15:00 second task',
                         '2015-01-07 10:10:00 time order',
                         '2015-01-07 10:20:00 fourth task',
                         ]))
    with pytest.raises(SystemExit) as err:
        opts = optparse.Values({'filename': xyz.strpath,
                                'start': '2015.0107',
                                'end': '2015.0107',
                                'dayflag': False})
        wr.write_report(opts, True)
    assert_includes(str(err), 'Dates or times out of order')


# -------------------------------------------------------------------------
def assert_includes(container, content):
    """
    Report when something expected is not present
    """
    assert content in container, 'expectd {} in {}'.format(content,
                                                           container)


# -------------------------------------------------------------------------
def assert_excludes(container, content):
    """
    Report when something unexpected IS present
    """
    assert content not in container, '{} {} {} {}'.format('unexpected',
                                                          content,
                                                          'found in',
                                                          container)


# -------------------------------------------------------------------------
def shms(hms):
    """
    Parse an HH:MM:SS string and return the corresponding seconds
    """
    (hours, minutes, seconds) = hms.split(':')
    seconds = int(seconds) + 60*(int(minutes) + 60*int(hours))
    return seconds


# -------------------------------------------------------------------------
def phms(hms):
    """
    Parse an HH:MM:SS string and return the corresponding %3.1f hours
    """
    (hours, minutes, seconds) = hms.split(':')
    seconds = int(seconds) + 60*(int(minutes) + 60*int(hours))
    hours = float(seconds)/3600.0
    return hours


# -------------------------------------------------------------------------
def fp_close(a, b, tolerance):
    """
    Return True or False indicating whether values *a* and *b* are within
    *tolerance* of each other
    """
    return abs(a - b) < tolerance


# -------------------------------------------------------------------------
@pytest.fixture
def fx_wrprep():
    """
    Set wr verbosity and remove wr.process_line.lastline if it exists
    """
    wr.verbose(False, True)
    if hasattr(wr.process_line, 'lastline'):
        del wr.process_line.lastline


# -------------------------------------------------------------------------
@pytest.fixture
def fx_stddata(tmpdir):
    """
    Generate standard test data
    """
    lines = ['-- Tuesday',
             '2009-07-21 08:30:28 admin: setup',
             '2009-07-21 08:35:34 admin: liason',
             '2009-07-21 17:00:34 COB',
             '-- Wednesday',
             '2009-07-22 08:35:59 e-mail: forty-nine',
             '2009-07-22 11:17:24 stella: frump',
             '2009-07-22 12:48:54 stella: alump',
             '2009-07-22 13:32:19 admin: hpss',
             '2009-07-22 14:26:00 e-mail: fiddle',
             '2009-07-22 16:34:59 COB',
             '-- Thursday',
             '2009-07-23 11:22:17 admin: read mail',
             '2009-07-23 13:17:43 vacation',
             '2009-07-23 16:35:59 COB',
             '-- Friday',
             '2009-07-24 10:19:58 admin: other stuff',
             '2009-07-24 12:35:59 vacation',
             '2009-07-24 16:35:59 COB']
    xyz = tmpdir.join('XYZ')
    f = open(xyz.strpath, 'w')
    f.write('\n'.join(lines) + "\n")
    f.close()
    fx_stddata.file = xyz
    return fx_stddata


# -----------------------------------------------------------------------------
def parse_report_line(line):
    """
    Break up a line like one of the following into text and duration

    '   e-mail: forty-nine                              02:41:25'
    'Total:                                                    00:00:00 (0)'

    For lines that don't match the pattern, return text = '', duration = 0
    """
    result = re.findall('\s*(.*[\w:])\s+(\d{2}:\d{2}:\d{2}).*', line)
    if result == []:
        rval = ('', 0)
    else:
        rval = (result[0][0], shms(result[0][1]))
    return rval

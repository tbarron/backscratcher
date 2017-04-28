import optparse
import os
import re
import time

import pytest

import bscr
from bscr import testhelp as th
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


# -----------------------------------------------------------------------------
class workrptTest(th.HelpedTestCase):
    """
    things to test
     - week_starting_last()
     - day_plus()
     - package()
     - tally()
     - category()
     - reset_category_total()
     - increment_category_total()
     - week_diff()
     - write_report()
    """
    # -------------------------------------------------------------------------
    def test_day_offset(self):
        """
        Check each weekday offset.
        """
        assert(wr.day_offset('f') == 3)
        assert(wr.day_offset('c') == 4)
        assert(wr.day_offset('M') == 0)
        assert(wr.day_offset('T') == 1)
        assert(wr.day_offset('W') == 2)
        assert(wr.day_offset('t') == 3)
        assert(wr.day_offset('F') == 4)
        assert(wr.day_offset('s') == 5)
        assert(wr.day_offset('S') == 6)
        assert(wr.day_offset('') == 3)
        e = None
        try:
            wr.day_offset('x')
        except KeyError, e:
            pass
        assert(str(e) == "'x'")
        # print "exception as a string: '%s'" % str(e)

    # -------------------------------------------------------------------------
    def test_default_input_filename(self):
        """
        Make sure workrpt agrees with where we think the default input file
        should be.
        """
        home = os.getenv("HOME")
        exp = U.pj(home, "Dropbox", "journal",
                   time.strftime("%Y"), "WORKLOG")
        actual = wr.default_input_filename()
        self.assertEqual(exp, actual,
                         "Expected '%s', got '%s'" % (exp, actual))

    # -------------------------------------------------------------------------
    def test_hms(self):
        """
        Test the workrpt hms() routine which is supposed to convert an epoch
        time to HH:MM:SS format.
        """
        assert(wr.hms(72) == '00:01:12')
        assert(wr.hms(120) == '00:02:00')
        assert(wr.hms(4000) == '01:06:40')

    # -------------------------------------------------------------------------
    def test_interpret_options_defaults(self):
        """
        Check default start and end times.
        """
        (o, a) = wr.make_option_parser([])
        (start, end) = wr.interpret_options(o)
        assert(not o.dayflag)
        (start_should_be, x) = wr.week_starting_last(wr.day_offset('M'), 0)
        end_should_be = time.strftime('%Y.%m%d', time.localtime())
        assert(start == start_should_be)
        assert(end == end_should_be)

    # -------------------------------------------------------------------------
    def test_interpret_options_dayflag(self):
        """
        Verify that setting the day flag does not disrupt the default start/end
        time.
        """
        (o, a) = wr.make_option_parser(['-d'])
        (start, end) = wr.interpret_options(o)
        assert(o.dayflag)
        (start_should_be, x) = wr.week_starting_last(wr.day_offset('M'), 0)
        end_should_be = time.strftime('%Y.%m%d', time.localtime())
        assert(start == start_should_be)
        assert(end == end_should_be)

    # -------------------------------------------------------------------------
    def test_interpret_options_end(self):
        """
        If the user provides option -e <date>, wr.interpret_options should
        return a start date one week before and an end date of <date>.
        """
        (o, a) = wr.make_option_parser(['-e', '2009.0401'])
        (start, end) = wr.interpret_options(o)
        start_should_be = '2009.0326'
        end_should_be = '2009.0401'
        self.assertEqual(start_should_be, start,
                         'start incorrect for -e 2009.0401: %s =?= %s'
                         % (start_should_be, start))
        self.assertEqual(end_should_be, end,
                         'end incorrect for -e 2009.0401: %s =?= %s'
                         % (end_should_be, end))

    # -------------------------------------------------------------------------
    def test_interpret_options_last_start(self):
        """
        Verify mutual exclusion of -l and -s
        """
        (o, a) = wr.make_option_parser(['-l', '-s', '2009.0501'])
        self.assertRaisesMsg(bscr.Error,
                             '--last and --start or --end are not compatible',
                             wr.interpret_options,
                             o)

    # -------------------------------------------------------------------------
    def test_interpret_options_last_end(self):
        """
        Verify mutual exclusion of -l and -e
        """
        (o, a) = wr.make_option_parser(['-l', '-e', '2009.0501'])
        self.assertRaisesMsg(bscr.Error,
                             '--last and --start or --end are not compatible',
                             wr.interpret_options,
                             o)

    # -------------------------------------------------------------------------
    def test_interpret_options_since(self):
        """
        Verify that option --since works as expected
        """
        (o, a) = wr.make_option_parser(['--since', '2009.0501'])
        (start, end) = wr.interpret_options(o)
        self.assertEqual(start, '2009.0501')
        self.assertEqual(end, time.strftime('%Y.%m%d'))

        (o, a) = wr.make_option_parser(['-s', '2010.0101', '-S', '2010.1231'])
        self.assertRaisesMsg(bscr.Error,
                             '--since and --start are not compatible',
                             wr.interpret_options,
                             o)

    # -------------------------------------------------------------------------
    def test_interpret_options_week_start(self):
        """
        Verify mutual exclusion of -w and -s
        """
        (o, a) = wr.make_option_parser(['-w', 'M', '-s', '2009.0501'])
        self.assertRaisesMsg(bscr.Error,
                             '--week and --start or --end are not compatible',
                             wr.interpret_options,
                             o)

    # -------------------------------------------------------------------------
    def test_interpret_options_week_end(self):
        """
        Verify mutual exclusion of -w and -e
        """
        (o, a) = wr.make_option_parser(['-w', 'T', '-e', '2009.0501'])
        self.assertRaisesMsg(bscr.Error,
                             '--week and --start or --end are not compatible',
                             wr.interpret_options,
                             o)

#     def test_last_monday(self):  # last_monday() is never called
#         now = self.last_wkday(wr.day_offset('M'))
#         lm = last_monday()
#         assert(abs(lm - now) <= 24*3600)

#     def test_last_wednesday(self):   # last_wednesday() is never called
#         now = self.last_wkday(wr.day_offset('W'))
#         lm = last_wednesday()
#         assert(abs(lm - now) <= 24*3600)

    # -------------------------------------------------------------------------
#     def test_maketime(self):
#         """
#         """
#         self.dbgfunc()
#         td = ["2014.1031", "2014.1105"]
#         for ymd in td:
#             mktime_out = U.epoch(ymd)
#             wr_out = wr.maketime(time.strptime(ymd, "%Y.%m%d"))
#             self.expected(mktime_out, wr_out)

    # -------------------------------------------------------------------------
    def test_next_tuesday(self):  # never called
        """
        Routine wr.next_tuesday() should return the date of next tuesday
        """
        now = self.next_wkday(wr.day_offset('T'))
        nm = time.strftime('%Y.%m%d', time.localtime(now))
        lm = wr.next_tuesday()
        assert(nm == lm)

    # -------------------------------------------------------------------------
    def last_wkday(self, weekday):
        """
        Brute force the last occurrence of *weekday* for verifying tests
        """
        now = time.time()
        tm = time.localtime(now)
        while tm[6] != weekday:
            now = now - 24 * 3600
            tm = time.localtime(now)
        return now

    # -------------------------------------------------------------------------
    def next_wkday(self, weekday):
        """
        Brute force the next occurrence of *weekday* for verifying tests
        """
        now = time.time()
        tm = time.localtime(now)
        while tm[6] != weekday:
            now = now + 24 * 3600
            tm = time.localtime(now)
        return now

    # -------------------------------------------------------------------------
    def test_next_day(self):
        """
        test the next_day() routine
        """
        assert(wr.next_day('2009.1231') == '2010.0101')
        assert(wr.next_day('2009.0228') == '2009.0301')
        assert(wr.next_day('2008.0228') == '2008.0229')
        assert(wr.next_day('2007.1231', '%Y.%m%d') == '2008.0101')
        self.assertRaisesMsg(ValueError,
                             "next_day threw ValueError",
                             wr.next_day,
                             "2006.0228")

    # -------------------------------------------------------------------------
    def test_parse_timeline(self):
        """
        test parse_timeline()
        """
        assert(['2009', '05', '13', '09', '20', '26', 'admin: setup'] ==
               wr.parse_timeline('2009-05-13 09:20:26 admin: setup'))
        assert(['2009', '05', '14', '10', '20', '19', 'foobar: plugh'] ==
               wr.parse_timeline('2009.0514 10:20:19 foobar: plugh'))
        self.assertEqual(['2010', '02', '07',
                          '15', '30', '40',
                          '3opsarst: fro-oble 8.1'],
                         wr.parse_timeline('2010.0207 ' +
                                           '15:30:40 ' +
                                           '3opsarst: fro-oble 8.1'))

    # -------------------------------------------------------------------------
    def test_parse_ymd(self):
        """
        test parse_ymd() for each weekday, yesterday, and tomorrow
        """
        pytest.debug_func()
        s = wr.stringify(time.localtime(wr.day_plus(-1)))
        assert(wr.parse_ymd('yesterday') == s[0:3])
        s = wr.stringify(time.localtime(wr.day_plus(1)))
        assert(wr.parse_ymd('tomorrow') == s[0:3])

        self.parse_ymd('monday', 'M')
        self.parse_ymd('tuesday', 'T')
        self.parse_ymd('wednesday', 'W')
        self.parse_ymd('thursday', 't')
        self.parse_ymd('friday', 'F')
        self.parse_ymd('saturday', 's')
        self.parse_ymd('sunday', 'S')

    # -------------------------------------------------------------------------
    def parse_ymd(self, target, t):
        """
        test parse_ymd for one day
        """
        n = time.localtime()
        d = wr.week_diff(n[6], wr.day_offset(t))
        s = wr.stringify(time.localtime(wr.day_plus(d)))
        # print 's = ', s
        # print 'p = ', wr.parse_ymd(target)
        assert(wr.parse_ymd(target) == s[0:3])

    # -------------------------------------------------------------------------
    def daystart(self, mark):
        """
        Given *mark* compute the beginning of the day mark falls in
        """
        t = time.localtime(mark)
        rval = time.mktime([t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, 0, 0, 0])
        return rval

    # -------------------------------------------------------------------------
    def test_week_ending(self):
        """
        test calculating the beginning of a week from its end?
        """
        self.dbgfunc()
        tlist = {'yesterday': self.daystart(time.time() - 24*3600),
                 'today': self.daystart(time.time()),
                 'tomorrow': self.daystart(time.time() + 24*3600),
                 '2014.1104': U.epoch("2014.1104"),
                 '2009.0401': time.mktime(time.strptime('2009.0401',
                                                        '%Y.%m%d'))}
        for t in tlist.keys():
            (start, end) = wr.week_ending(t)
            tm = time.localtime(tlist[t])
            end_exp = time.strftime('%Y.%m%d', tm)

            tm = time.localtime(tlist[t] - (6*24*3600-7200))
            start_exp = time.strftime('%Y.%m%d', tm)

            self.expected(start_exp, start)
            self.expected(end_exp, end)

    # -------------------------------------------------------------------------
    def test_week_starting(self):
        """
        test calculating the end of a week from its start. The test for
        2014.1031 spans the beginning of DST.
        """
        self.dbgfunc()
        tlist = {'yesterday': time.time() - 24*3600,
                 'today': time.time(),
                 'tomorrow': time.time() + 24*3600,
                 '2014.1028': U.epoch("2014.1028"),
                 '2009.0401': time.mktime(time.strptime('2009.0401',
                                                        '%Y.%m%d'))}
        for t in tlist.keys():
            print("t = %s" % t)
            (start, end) = wr.week_starting(t)
            tm = time.localtime(tlist[t])
            start_should_be = time.strftime('%Y.%m%d', tm)

            tm = time.localtime(tlist[t] + 6*24*3600 + 7200)
            end_should_be = time.strftime('%Y.%m%d', tm)

            self.expected(start_should_be, start)
            self.expected(end_should_be, end)

    # -------------------------------------------------------------------------
    def test_week_starting_last(self):
        """
        See docstring for wsl()
        """
        # monday -> monday
        self.wsl(0, 0, 1173070800.0, '2007.0305', '2007.0311')
        # tuesday -> monday
        self.wsl(0, 0, 1177995600.0, '2007.0430', '2007.0506')
        # wednesday -> monday
        # thurday -> monday
        # friday -> monday
        self.wsl(0, 0, 1230872400.0, '2008.1229', '2009.0104')
        # saturday -> monday
        # sunday -> monday

        # monday -> tuesday
        # tuesday -> tuesday
        # wednesday -> tuesday
        # thurday -> tuesday
        # friday -> tuesday
        # saturday -> tuesday
        # sunday -> tuesday

        # monday -> wednesday
        # tuesday -> wednesday
        # wednesday -> wednesday
        # thurday -> wednesday
        # friday -> wednesday
        # saturday -> wednesday
        # sunday -> wednesday

        # monday -> thursday
        # tuesday -> thursday
        # wednesday -> thursday
        # thurday -> thursday
        # friday -> thursday
        # saturday -> thursday
        # sunday -> thursday

        # monday -> friday
        # tuesday -> friday
        # wednesday -> friday
        # thurday -> friday
        # friday -> friday
        # saturday -> friday
        # sunday -> friday

        # monday -> saturday
        # tuesday -> saturday
        # wednesday -> saturday
        # thurday -> saturday
        # friday -> saturday
        # saturday -> saturday
        # sunday -> saturday

        # monday -> sunday
        # tuesday -> sunday
        # wednesday -> sunday
        # thurday -> sunday
        # friday -> sunday
        # saturday -> sunday
        # sunday -> sunday

    # -------------------------------------------------------------------------
    def wsl(self, target, offset, now, should_start, should_end):
        """
        Routine week_starting_last() takes time index *now*, *target* weekday
        (0 = Monday), and *offset* seconds. It computes, say,"last Monday" from
        *now*, adds *offset* seconds, and returns a tuple containing the day
        indicated in %Y.%m%d format and a week later in the same format.
        """
        (s, e) = wr.week_starting_last(target, offset, now)
        # print s, should_start
        # print e, should_end
        assert(s == should_start)
        assert(e == should_end)

    # -------------------------------------------------------------------------
    def test_weekday_num(self):
        """
        Verify the numeric correspondences of the weekdays -- monday == 0,
        sunday == 6.
        """
        count = 0
        for d in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday']:
            self.assertEqual(wr.weekday_num(d), count,
                             'weekday_num(%d) fails for %s' % (count, d))
            count = count + 1

        self.assertRaisesMsg(KeyError,
                             "notaday",
                             wr.weekday_num,
                             'notaday')


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
def epoch_strptime(timespec, format):
    """
    """
    tup = time.strptime(timespec, format)
    epoch = time.mktime(tup)
    return epoch


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

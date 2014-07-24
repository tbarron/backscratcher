import os
from bscr import testhelp as th
import time
from bscr import util as U
from bscr import workrpt as wr


# ---------------------------------------------------------------------------
class workrptTest(th.HelpedTestCase):
    # things to test
    #  - week_starting_last()
    #  - day_plus()
    #  - package()
    #  - tally()
    #  - category()
    #  - reset_category_total()
    #  - increment_category_total()
    #  - week_diff()
    #  - write_report()

    def test_day_offset(self):
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
            q = wr.day_offset('x')
        except KeyError, e:
            pass
        assert(str(e) == "'x'")
        # print "exception as a string: '%s'" % str(e)

    def test_default_input_filename(self):
        home = os.getenv("HOME")
        exp = U.pj(home, "Dropbox", "journal",
                   time.strftime("%Y"), "WORKLOG")
        actual = wr.default_input_filename()
        self.assertEqual(exp, actual,
                         "Expected '%s', got '%s'" % (exp, actual))

    def test_hms(self):
        assert(wr.hms(72) == '00:01:12')
        assert(wr.hms(120) == '00:02:00')
        assert(wr.hms(4000) == '01:06:40')

    def test_interpret_options_defaults(self):
        (o, a) = wr.makeOptionParser([])
        (start, end) = wr.interpret_options(o)
        assert(not o.dayflag)
        (start_should_be, x) = wr.week_starting_last(wr.day_offset('M'), 0)
        end_should_be = time.strftime('%Y.%m%d', time.localtime())
        assert(start == start_should_be)
        assert(end == end_should_be)

    def test_interpret_options_dayflag(self):
        (o, a) = wr.makeOptionParser(['-d'])
        (start, end) = wr.interpret_options(o)
        assert(o.dayflag)
        (start_should_be, x) = wr.week_starting_last(wr.day_offset('M'), 0)
        end_should_be = time.strftime('%Y.%m%d', time.localtime())
        assert(start == start_should_be)
        assert(end == end_should_be)

    def test_interpret_options_end(self):
        (o, a) = wr.makeOptionParser(['-e', '2009.0401'])
        (start, end) = wr.interpret_options(o)
        start_should_be = '2009.0326'
        end_should_be = '2009.0401'
        self.validate(start, start_should_be,
                      'start incorrect for -e 2009.0401')
        self.validate(end, end_should_be,
                      'end incorrect for -e 2009.0401')

    def test_interpret_options_last_start(self):
        (o, a) = wr.makeOptionParser(['-l', '-s', '2009.0501'])
        self.assertRaisesMsg(StandardError,
                             '--last and --start or --end are not compatible',
                             wr.interpret_options,
                             o)

    def test_interpret_options_last_end(self):
        (o, a) = wr.makeOptionParser(['-l', '-e', '2009.0501'])
        self.assertRaisesMsg(StandardError,
                             '--last and --start or --end are not compatible',
                             wr.interpret_options,
                             o)

    def test_interpret_options_since(self):
        (o, a) = wr.makeOptionParser(['--since', '2009.0501'])
        (start, end) = wr.interpret_options(o)
        self.assertEqual(start, '2009.0501')
        self.assertEqual(end, time.strftime('%Y.%m%d'))

        (o, a) = wr.makeOptionParser(['-s', '2010.0101', '-S', '2010.1231'])
        self.assertRaisesMsg(StandardError,
                             '--since and --start are not compatible',
                             wr.interpret_options,
                             o)

    def test_interpret_options_week_start(self):
        (o, a) = wr.makeOptionParser(['-w', 'M', '-s', '2009.0501'])
        self.assertRaisesMsg(StandardError,
                             '--week and --start or --end are not compatible',
                             wr.interpret_options,
                             o)

    def test_interpret_options_week_end(self):
        (o, a) = wr.makeOptionParser(['-w', 'T', '-e', '2009.0501'])
        self.assertRaisesMsg(StandardError,
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

    def test_next_tuesday(self):  # never called
        now = self.next_wkday(wr.day_offset('T'))
        nm = time.strftime('%Y.%m%d', time.localtime(now))
        lm = wr.next_tuesday()
        assert(nm == lm)

    def last_wkday(self, weekday):
        now = time.time()
        tm = time.localtime(now)
        while tm[6] != weekday:
            now = now - 24 * 3600
            tm = time.localtime(now)
        return now

    def next_wkday(self, weekday):
        now = time.time()
        tm = time.localtime(now)
        while tm[6] != weekday:
            now = now + 24 * 3600
            tm = time.localtime(now)
        return now

    def test_next_day(self):
        assert(wr.next_day('2009.1231') == '2010.0101')
        assert(wr.next_day('2009.0228') == '2009.0301')
        assert(wr.next_day('2008.0228') == '2008.0229')
        assert(wr.next_day('2007.1231', '%Y.%m%d') == '2008.0101')
        result = 'no exception'
        try:
            q = wr.next_day('2006-02-28')
        except ValueError:
            result = 'next_day threw ValueError'
        assert(result == 'next_day threw ValueError')

    def test_parse_timeline(self):
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

    def test_parse_ymd(self):
        s = wr.stringify(time.localtime(wr.day_plus(-1)))
        assert(wr.parse_ymd('yesterday') == s[0:3])
        s = wr.stringify(time.localtime(wr.day_plus(1)))
        assert(wr.parse_ymd('tomorrow') == s[0:3])

        self.parse_ymd_test('monday', 'M')
        self.parse_ymd_test('tuesday', 'T')
        self.parse_ymd_test('wednesday', 'W')
        self.parse_ymd_test('thursday', 't')
        self.parse_ymd_test('friday', 'F')
        self.parse_ymd_test('saturday', 's')
        self.parse_ymd_test('sunday', 'S')

    def parse_ymd_test(self, target, t):
        n = time.localtime()
        d = wr.week_diff(n[6], wr.day_offset(t))
        s = wr.stringify(time.localtime(wr.day_plus(d)))
        # print 's = ', s
        # print 'p = ', wr.parse_ymd(target)
        assert(wr.parse_ymd(target) == s[0:3])

    def test_standalone_category(self):
        # pdb.set_trace()
        lines = '''-- Tuesday
2009-07-21 08:30:28 admin: setup
2009-07-21 08:35:34 admin: liason
2009-07-21 17:00:34 COB

-- Wednesday
2009-07-22 08:35:59 vacation
2009-07-22 16:35:59 COB

-- Thursday
2009-07-23 08:35:59 vacation
2009-07-23 16:35:59 COB

-- Friday
2009-07-24 08:35:59 vacation
2009-07-24 16:35:59 COB
'''
        wr.verbose(False, True)
        f = open('XYZ', 'w')
        f.write(lines)
        f.close()

        r = wr.write_report('XYZ', '2009.0721', '2009.0724', False, True)
        os.unlink('XYZ')
        try:
            assert('32:30:06' in r)
        except AssertionError:
            print r

    def test_rounding(self):
        # pdb.set_trace()
        lines = '''-- Tuesday
2009-07-21 08:30:28 admin: setup
2009-07-21 08:35:34 admin: liason
2009-07-21 17:00:34 COB

-- Wednesday
2009-07-22 08:35:59 vacation
2009-07-22 16:34:59 COB

-- Thursday
2009-07-23 08:35:59 vacation
2009-07-23 16:35:59 COB

-- Friday
2009-07-24 08:35:59 vacation
2009-07-24 16:35:59 COB
'''
        wr.verbose(False, True)
        f = open('XYZ', 'w')
        f.write(lines)
        f.close()

        r = wr.write_report('XYZ', '2009.0721', '2009.0724', False, True)
        os.unlink('XYZ')
        try:
            assert('23.10' not in r)
        except AssertionError:
            print r
            raise

        try:
            assert('24.0' in r)
        except AssertionError:
            print r
            raise

    def test_start_date_missing(self):
        lines = '''-- Friday
2012-04-13 08:30:48 3op3arst: trouble-shooting production logc
2012-04-13 14:16:34 3op3sysp: e-mail
2012-04-13 15:45:03 3op3arst: bug 1476
2012-04-13 17:55:00 COB
'''
        wr.verbose(False, True)
        f = open('XYZ', 'w')
        f.write(lines)
        f.close()

        r = wr.write_report('XYZ', '2012.0407', '2012.0413', True, True)
        os.unlink('XYZ')
        try:
            assert('23.10' not in r)
        except AssertionError:
            print r
            raise

        try:
            assert('09:24:12 (9.4)' in r)
        except AssertionError:
            print r
            raise

    def test_week_ending(self):
        tlist = {'yesterday': time.time() - 24*3600,
                 'today': time.time(),
                 'tomorrow': time.time() + 24*3600,
                 '2009.0401': time.mktime(time.strptime('2009.0401',
                                                        '%Y.%m%d'))}
        for t in tlist.keys():
            (start, end) = wr.week_ending(t)
            end_should_be = time.strftime('%Y.%m%d',
                                          time.localtime(tlist[t]))
            start_should_be = time.strftime('%Y.%m%d',
                                            time.localtime(tlist[t]-6*24*3600))
            self.validate(start, start_should_be,
                          'start is incorrect for %s' % t)
            self.validate(end, end_should_be,
                          'end is incorrect for %s' % t)

    def test_week_starting(self):
        tlist = {'yesterday': time.time() - 24*3600,
                 'today': time.time(),
                 'tomorrow': time.time() + 24*3600,
                 '2009.0401': time.mktime(time.strptime('2009.0401',
                                                        '%Y.%m%d'))}
        for t in tlist.keys():
            (start, end) = wr.week_starting(t)
            start_should_be = time.strftime('%Y.%m%d',
                                            time.localtime(tlist[t]))
            end_should_be = time.strftime('%Y.%m%d',
                                          time.localtime(tlist[t]+6*24*3600))
            self.validate(start, start_should_be,
                          'start is incorrect for %s' % t)
            self.validate(end, end_should_be,
                          'end is incorrect for %s' % t)

    def test_week_starting_last(self):
        # monday -> monday
        self.wsl_test(0, 0, 1173070800.0, '2007.0305', '2007.0311')
        # tuesday -> monday
        self.wsl_test(0, 0, 1177995600.0, '2007.0430', '2007.0506')
        # wednesday -> monday
        # thurday -> monday
        # friday -> monday
        self.wsl_test(0, 0, 1230872400.0, '2008.1229', '2009.0104')
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

    def wsl_test(self, target, offset, now, should_start, should_end):
        (s, e) = wr.week_starting_last(target, offset, now)
        # print s, should_start
        # print e, should_end
        assert(s == should_start)
        assert(e == should_end)

    def test_weekday_num(self):
        count = 0
        for d in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday']:
            self.validate(wr.weekday_num(d), count,
                          'weekday_num() fails for %s' % d)
            count = count + 1

        success = False
        try:
            x = wr.weekday_num('notaday')
        except KeyError:
            success = True
        self.validate(success, True,
                      'should have gotten a KeyError for notaday')

    def validate(self, v1, v2, msg):
        try:
            assert(v1 == v2)
        except AssertionError:
            print msg
            print '%s =?= %s' % (v1, v2)
            raise

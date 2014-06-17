#!/usr/bin/python
"""
dt - date/time manipulation from the command line

Apply a format to a time index like date(1). However, dt will also
accept a time specification to indicate the time index to be formatted.

The time spec can be one of the following:

   today
   tomorrow
   yesterday
   (last|next) (week|month|year)
   (+|-)<n> (seconds|minutes|hours|days|weeks|months|years)
   (+|-)((HH:)MM:)SS
   [epoch-time]

 dt -f '%Y.%m%d' next week
 dt -f '%Y.%m%d' {next|last} {second|minute|hour|day|week|month|year
                              |monday|tuesday|wednesday|thursday
                              |friday|saturday|sunday}
 dt -f <format> [+|-]<integer> {sec|min|hour|day|week|month|year}
 dt -f <format> [epoch-time]

EXAMPLES

   $ dt next week
   2010.0413 15:51:18

   $ dt last year
   2009.0406 15:51:22

   $ dt next year
   2011.0406 15:51:28

   $ dt -f "%s" yesterday
   1270500782

   $ dt -f %s
   1270587188

   $ dt -f "%Y.%m%d" 1270587188

LICENSE

Copyright (C) 1995 - <the end of time>  Tom Barron
   tom.barron@comcast.net
   177 Crossroads Blvd
   Oak Ridge, TN  37830

This software is licensed under the CC-GNU GPL. For the full text of
the license, see http://creativecommons.org/licenses/GPL/2.0/

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import optparse
import pdb
import re
import sys
import time
import toolframe
import unittest


# ---------------------------------------------------------------------------
def main(argv=None):
#     if argv == None:
#         argv = sys.argv

    p = optparse.OptionParser()
    p.add_option('-d', '--debug', dest='debug',
                 action='store_true', default=False,
                 help='run the debugger')
    p.add_option('-f', '--format', type='string', dest='format',
                 action='store', default='%Y.%m%d %H:%M:%S',
                 help='date format (see strftime(3))')
    (o, a) = p.parse_args(argv)

    if o.debug:
        pdb.set_trace()
    print report_date(o.format, a[1:])


# ---------------------------------------------------------------------------
def fatal(msg):
    # raise DtError(msg)
    raise StandardError(msg)


# ---------------------------------------------------------------------------
def report_date(format, args):
    # print args
    argstr = ' '.join(args).lower()
    argstr = re.sub(r'(\+|-)\s+', r'\1', argstr)
    argstr = argstr.strip()
    if ' ' in argstr:
        edited_args = argstr.split()
    else:
        edited_args = [argstr]

    # print('edited_args = ', edited_args)
    offset = parse_whenspec(edited_args)
    when = time.time() + offset
    return time.strftime(format, time.localtime(when))


# ---------------------------------------------------------------------------
def is_numeric(strval):
    try:
        float(strval)
    except:
        return False
    return True


# ---------------------------------------------------------------------------
def parse_whenspec(args):
    if is_numeric(args[0]) and (1 == len(args)):
        rval = int(args[0]) - int(time.time())
    elif args[0] == 'next':
        rval = next(args[1:])
    elif args[0] == 'last':
        rval = last(args[1:])
    elif args[0] == 'today':
        rval = today(args[1:])
    elif args[0] == 'tomorrow':
        rval = tomorrow(args[1:])
    elif args[0] == 'yesterday':
        rval = yesterday(args[1:])
    elif re.search(r'^(\+|-)\d+', args[0]):
        rval = today(args)
    elif args[0] == '':
        rval = today(args)
    else:
        fatal("can't parse whenspec '%s'" % ' '.join(args))

    return rval


# ---------------------------------------------------------------------------
def next(args):
    if len(args) < 1:
        # raise DtError('next: expected unit or weekday, found nothing')
        raise StandardError('next: expected unit or weekday, found nothing')
    elif re.match(r'[+-]?\d+', args[0]):
        # raise DtError('next: expected unit or weekday, got number')
        raise StandardError('next: expected unit or weekday, got number')
    elif args[0] in ['second', 'minute', 'hour', 'day',
                     'week', 'month', 'year']:
        rval = unit_size(args[0])
    elif 0 <= weekday_number(args[0]) and weekday_number(args[0]) <= 6:
        rval = time_to(args[0], dir='next')

    try:
        return rval
    except UnboundLocalError:
        # raise DtError('next: no return value set')
        raise StandardError('next: no return value set')


# ---------------------------------------------------------------------------
def last(args):
    if len(args) < 1:
        # raise DtError('last: expected unit or weekday, found nothing')
        raise StandardError('last: expected unit or weekday, found nothing')
    elif re.match(r'[+-]?\d+', args[0]):
        # raise DtError('last: expected unit or weekday, got number')
        raise StandardError('last: expected unit or weekday, got number')
    elif args[0] in ['second', 'minute', 'hour', 'day',
                     'week', 'month', 'year']:
        rval = unit_size(args[0])
    elif 0 <= weekday_number(args[0]) and weekday_number(args[0]) <= 6:
        rval = time_to(args[0], dir='last')

    try:
        return rval
    except UnboundLocalError:
        # raise DtError('last: no return value set')
        raise StandardError('last: no return value set')


# ---------------------------------------------------------------------------
def weekday_number(day):
    wdl = weekday_list()
    for num in range(len(wdl)):
        if wdl[num].startswith(day):
            return num
    return -1


# ---------------------------------------------------------------------------
def time_to(day, dir):
    wdl = weekday_list()
    # daynum = wdl.index(day)
    daynum = weekday_number(day)
    tup = time.localtime()
    if dir == 'last':
        then = -24*60*60 * ((7 + tup[6] - daynum - 1) % 7 + 1)
    elif dir == 'next':
        then = 24*60*60 * ((7 + daynum - tup[6] - 1) % 7 + 1)
    else:
        # raise DtError('time_to: invalid direction')
        raise StandardError('time_to: invalid direction')
    return then


# ---------------------------------------------------------------------------
def today(args):
    if len(args) == 0:
        return 0
    elif args[0] == '':
        return 0

    count = int(args[0])
    if count == 0:
        fatal("expected a number, got '%s'" % args[0])

    if args[1] not in unit_list():
        fatal("expected a unit, got '%s'" % args[1])

    rval = count * unit_size(args[1])
    return rval


# ---------------------------------------------------------------------------
def tomorrow(args):
    if len(args) == 0:
        return 24 * 3600

    count = int(args[0])
    if count == 0:
        fatal("expected a number, got '%s'" % args[0])

    if args[1] not in unit_list():
        fatal("expected a unit, got '%s'" % args[1])

    rval = 24 * 3600 + count * unit_size(args[1])
    return rval


# ---------------------------------------------------------------------------
def unit_list():
    return ['second', 'minute', 'hour', 'day', 'week', 'month', 'year']


# ---------------------------------------------------------------------------
def unit_size(unit):
    uval = {'second': 1,
            'minute': 60,
            'hour': 3600,
            'day': 24 * 3600,
            'week': 7 * 24 * 3600,
            'month': 30 * 24 * 3600,
            'year': 365 * 24 * 3600}
    rval = uval[unit]
    return rval


# ---------------------------------------------------------------------------
def weekday_list():
    return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
            'saturday', 'sunday']


# ---------------------------------------------------------------------------
def yesterday(args):
    if len(args) == 0:
        return -24 * 3600

    count = int(args[0])
    if count == 0:
        fatal("expected a number, got '%s'" % args[0])

    if args[1] not in unit_list():
        fatal("expected a unit, got '%s'" % args[1])

    rval = -24 * 3600 + count * unit_size(args[1])
    return rval


# ---------------------------------------------------------------------------
class dtTest(unittest.TestCase):
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
            a = parse_whenspec(testargs)
            self.assertEqual(a, expected)
        elif type(expected) == str:
            got_exception = False
            try:
                a = parse_whenspec(testargs)
            except StandardError, e:
                got_exception = True
                self.assertEqual(str(e), expected)
            assert(got_exception)
        else:
            raise StandardError("expected int or string, got '%s'" % a)

    # -----------------------------------------------------------------------
    def report_test(self, testargs, expected):
        if type(expected) == int:
            a = report_date(self.default_fmt(), testargs)
            b = time.strftime(self.default_fmt(),
                              time.localtime(time.time() + expected))
            self.assertEqual(a, b)
        elif type(expected) == str:
            got_exception = False
            try:
                a = report_date(self.default_fmt(), testargs)
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
        self.both_test(['next', 'monday'], time_to('monday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_tuesday(self):
        self.both_test(['last', 'tuesday'], time_to('tuesday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_wednesday(self):
        self.both_test(['next', 'wednesday'], time_to('wednesday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_thursday(self):
        self.both_test(['last', 'thursday'], time_to('thursday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_friday(self):
        self.both_test(['next', 'friday'], time_to('friday', 'next'))

    # -----------------------------------------------------------------------
    def test_last_saturday(self):
        self.both_test(['last', 'saturday'], time_to('saturday', 'last'))

    # -----------------------------------------------------------------------
    def test_next_sunday(self):
        self.both_test(['next', 'sunday'], time_to('sunday', 'next'))

# ---------------------------------------------------------------------------
toolframe.ez_launch(__name__, main)

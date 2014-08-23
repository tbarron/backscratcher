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
    """
    CLEP
    """
    if argv is None:
        argv = sys.argv

    p = optparse.OptionParser(usage=usage())
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


# -----------------------------------------------------------------------------
def fatal(msg):
    """
    !@!DERPRECATED -- should this be in util?
    """
    # raise DtError(msg)
    raise StandardError(msg)


# -----------------------------------------------------------------------------
def report_date(format, args):
    """
    Parse *args* to get a time and return it formatted according to *format*
    """
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
    """
    True if strval can be converted to float, otherwise False
    """
    try:
        float(strval)
    except:
        return False
    return True


# ---------------------------------------------------------------------------
def parse_whenspec(args):
    """
    Parse a time specification from *args*
    """
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
    """
    Apply 'next' to the unit
    """
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
    """
    Apply 'last' to the unit
    """
    if len(args) < 1:
        # raise DtError('last: expected unit or weekday, found nothing')
        raise StandardError('last: expected unit or weekday, found nothing')
    elif re.match(r'[+-]?\d+', args[0]):
        # raise DtError('last: expected unit or weekday, got number')
        raise StandardError('last: expected unit or weekday, got number')
    elif args[0] in ['second', 'minute', 'hour', 'day',
                     'week', 'month', 'year']:
        rval = -1 * unit_size(args[0])
    elif 0 <= weekday_number(args[0]) and weekday_number(args[0]) <= 6:
        rval = time_to(args[0], dir='last')

    try:
        return rval
    except UnboundLocalError:
        # raise DtError('last: no return value set')
        raise StandardError('last: no return value set')


# ---------------------------------------------------------------------------
def weekday_number(day):
    """
    Convert from weekday to a number. !@! This could probably be done better
    with a dict indexed by day names.
    """
    wdl = weekday_list()
    for num in range(len(wdl)):
        if wdl[num].startswith(day):
            return num
    return -1


# ---------------------------------------------------------------------------
def time_to(day, dir):
    """
    Figure out the time to the next or previous *day*
    """
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
    """
    What does this do?
    """
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
    """
    This does it for 24 hours from now
    """
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
    """
    list of units
    """
    return ['second', 'minute', 'hour', 'day', 'week', 'month', 'year']


# ---------------------------------------------------------------------------
def unit_size(unit):
    """
    size of units
    """
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
def usage():
    """
    usage
    """
    return """dt

    playing with dates"""


# ---------------------------------------------------------------------------
def weekday_list():
    """
    list of weekday names
    """
    return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
            'saturday', 'sunday']


# ---------------------------------------------------------------------------
def yesterday(args):
    """
    offset computation for 24 hours ago
    """
    if len(args) == 0:
        return -24 * 3600

    count = int(args[0])
    if count == 0:
        fatal("expected a number, got '%s'" % args[0])

    if args[1] not in unit_list():
        fatal("expected a unit, got '%s'" % args[1])

    rval = -24 * 3600 + count * unit_size(args[1])
    return rval

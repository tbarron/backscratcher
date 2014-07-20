#!/usr/bin/python
"""
generate calendars (pronounced "jackal")

Formats to be supported:
    analog
    analog-html
"""

import sys
import time
import toolframe
import unittest

from optparse import *


# -----------------------------------------------------------------------------
def main(argv=None):
    if argv is None:
        argv = sys.argv

    p = OptionParser()
    p.add_option('-f', '--format',
                 action='store', default='workflowy', dest='format',
                 help='calendar format (default = workflowy)')
    p.add_option('-i', '--input',
                 action='store', default='', dest='input',
                 help='input filename (default = no input)')
    p.add_option('-o', '--output',
                 action='store', default='', dest='output',
                 help='output filename (default = stdout)')
    p.add_option('-d', '--datefmt',
                 action='store', default='%Y.%m%d', dest='datefmt',
                 help='date format for -s, -e (default = %Y[.%m[%d]])')
    p.add_option('-s', '--start',
                 action='store', default='', dest='start',
                 help='start date (default = 1st of current month)')
    p.add_option('-e', '--end',
                 action='store', default='', dest='end',
                 help='end date (default = last of current month)')
    (o, a) = p.parse_args(argv)

    start = parse_date(o.start, o.datefmt, month_floor)
    end = parse_date(o.end, o.datefmt, month_ceiling)

    cdata = load_cal_info(o.input)

    step = 3600 * 24
    for day in range(start, end + step, step):
        generate_day(output, o.format, cdata, day)


# -----------------------------------------------------------------------------
def generate_day(outf, fmt, cdata, date):
    """
    Generate a day's worth of output based on fmt, cdata, and date
    """
    pass


# -----------------------------------------------------------------------------
def load_cal_info(filename):
    """
    Read filename and load the information into a dict and return it
    """
    pass


# -----------------------------------------------------------------------------
def month_ceiling(date=time.time()):
    """
    Compute the epoch time of the last day of the month in which date falls
    """
    pass


# -----------------------------------------------------------------------------
def month_floor(date=time.time()):
    """
    Compute the epoch time of the first day of the month in which date falls
    """
    pass


# -----------------------------------------------------------------------------
def parse_date(dspec, dfmt="%Y.%m%d", default_func=month_floor):
    """
    Parse dspec into an epoch time using the format in dfmt. If dspec is empty
    or None, call default_func and return the value it provides.
    """
    if dspec is None or dspec == '':
        return default_func()

    return time.mktime(time.strptime(dspec, dfmt))

# -----------------------------------------------------------------------------
toolframe.ez_launch(__name__, main)

#!/usr/bin/python
"""
generate calendars (pronounced "jackal")

Formats to be supported:
    analog
    analog-html
"""

import sys
import time

import util as U


# -----------------------------------------------------------------------------
def main(argv=None):
    """
    CLEP
    """
    if argv is None:
        argv = sys.argv
    U.dispatch('bscr.jcal', 'jcal', argv)


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

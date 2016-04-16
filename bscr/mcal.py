#!/usr/bin/env python
"""
Usage:
    mcal.py [-y <year>] [-m <month>] [-w] [-d]

Options:
    -d          Run the debugger
    -y <year>   Year of calendar
    -m <month>  Month of calendar
    -w          Print a wide calendar showing two months
"""
import pdb
import sys
import time

import docopt

# -----------------------------------------------------------------------------
def main(args=None):
    """
    This is the entry point
    """
    opts = docopt.docopt(__doc__, args)
    if opts['-d']:
        pdb.set_trace()

    today = time.localtime()
    year = int(opts['-y'] or today.tm_year)
    month = int(opts['-m'] or today.tm_mon)

    mlist = gen_month(year, month)
    if opts['-w']:
        year, month = next_month(year, month)
        nlist = gen_month(year, month)
        mlist = [a+'   '+b for a,b in zip(mlist, nlist)]

    return '\n'.join(mlist)

# -----------------------------------------------------------------------------
def gen_month(year, month):
    """
    Generate the layout for a month
    """
    date = first_day(year, month)
    rval = []
    rval.append(title(year, month))
    rval.append(week_header())

    line = ''
    # blanks before first day
    for _ in range(date.tm_wday):
        line += '   '

    # build the rest of the first line
    base = date.tm_wday
    for _ in range(base, 7):
        line += ' {0:2}'.format(date.tm_mday)
        date = next_day(date)
    rval.append(line)

    while date.tm_mon == month:
        line = ''
        for _ in range(7):
            if date.tm_mon != month:
                line += '   '
            else:
                line += ' {0:2}'.format(date.tm_mday)
            date = next_day(date)
        rval.append(line)

    while len(rval) < 8:
        rval.append(' ' * 21)
    return rval

# -----------------------------------------------------------------------------
def title(year, month):
    """
    Generate a title for a month display containing the *year* and *month*
    """
    rval = "{0}.{1:02}".format(year, month)
    return rval.center(21)

# -----------------------------------------------------------------------------
def week_header():
    """
    Generate the header line for a month display
    """
    wdnames = " Mo Tu We Th Fr Sa Su"
    return wdnames

# -----------------------------------------------------------------------------
def first_day(year=None, month=None):
    """
    Given *year* and *month*, return the epoch time at the begining of the
    first day of the month
    """
    today = time.localtime()
    if year is None:
        year = today.tm_year
    if month is None:
        month = today.tm_mon

    epoch = time.mktime((year, month, 1, 0, 0, 0, 0, 0, 0))
    rval = time.localtime(epoch)
    return rval

# -----------------------------------------------------------------------------
def next_day(date):
    """
    Given a specific *date*, return the successor date
    """
    epoch = time.mktime((date.tm_year, date.tm_mon, date.tm_mday+1,
                         0, 0, 0, 0, 0, 0))
    rval = time.localtime(epoch)
    return rval

# -----------------------------------------------------------------------------
def next_month(year, month):
    """
    Given *year* and *month*, return the successor year and month
    """
    epoch = time.mktime((year, month+1, 1, 0, 0, 0, 0, 0, 0))
    succ = time.localtime(epoch)
    year = succ.tm_year
    month = succ.tm_mon
    return year, month

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    print main(sys.argv[1:])

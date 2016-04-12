#!/usr/bin/env python
"""
Usage:
    mcal.py [-y <year>] [-m <month>] [-w] [-d]

Options:
    -d          Run the debugger
    -y <year>   Year of calendar
    -m <month>  Month of calendar
    -w          Print a wide calendar showing three months
"""
import docopt
import pdb
import sys
import time

def main(args=None):
    args = args or sys.argv
    opts = docopt.docopt(__doc__, args[1:])
    if opts['-d']:
        pdb.set_trace()

    today = time.localtime()
    # print opts
    year = int(opts['-y'] or today.tm_year)
    month = int(opts['-m'] or today.tm_mon)

    mlist = gen_month(year, month)
    if opts['-w']:
        year, month = next_month(year, month)
        nlist = gen_month(year, month)
        mlist = [a+'   '+b for a,b in zip(mlist, nlist)]

    for line in mlist:
        print line

def gen_month(year, month):
    date = first_day(year, month)
    rval = []
    rval.append(title(year, month))
    rval.append(week_header())

    line = ''
    # blanks before first day
    for day in range(date.tm_wday):
        line += '   '

    # build the rest of the first line
    base = date.tm_wday
    for day in range(base, 7):
        line += ' {0:2}'.format(date.tm_mday)
        date = next_day(date)
    rval.append(line)

    while date.tm_mon == month:
        line = ''
        for day in range(7):
            if date.tm_mon != month:
                line += '   '
            else:
                line += ' {0:2}'.format(date.tm_mday)
            date = next_day(date)
        rval.append(line)

    while len(rval) < 8:
        rval.append(' ' * 21)
    return rval

def title(year, month):
    rval = "{0}.{1:02}".format(year, month)
    return rval.center(21)

def week_header():
    wdnames = " Mo Tu We Th Fr Sa Su"
    return wdnames

def first_day(year=None, month=None):
    today = time.localtime()
    if year is None:
        year = today.tm_year
    if month is None:
        month = today.tm_mon

    epoch = time.mktime((year, month, 1, 0, 0, 0, 0, 0, 0))
    rval = time.localtime(epoch)
    return rval

def next_day(date):
    epoch = time.mktime((date.tm_year, date.tm_mon, date.tm_mday+1,
                         0, 0, 0, 0, 0, 0))
    rval = time.localtime(epoch)
    return rval

def next_month(year, month):
    epoch = time.mktime((year, month+1, 1, 0, 0, 0, 0, 0, 0))
    next = time.localtime(epoch)
    year = next.tm_year
    month = next.tm_mon
    return year, month

if __name__ == '__main__':
    main(sys.argv)


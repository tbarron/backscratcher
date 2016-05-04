#!/usr/bin/python
"""
stopwatch or countdown timer

chron -c/--count up
chron -c/--count down hh:mm:ss [-a/--action command]

For '-count up', print a '.' every second, divided into 10s with one
minute per line.

For '-count down', begin with the specified time and count down to 0.
If command is specified, once 0 is reached, run the command.

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
import os
import sys
import time

import toolframe
import util as U
BSCR = U.package_module(__name__)


# ---------------------------------------------------------------------------
def main(argv=None):
    """
    CLEP
    """
    if argv is None:
        argv = sys.argv

    prs = optparse.OptionParser(usage=usage())
    prs.add_option('-c', '--count',
                   action='store', default='up',
                   dest='count', type='string',
                   help='whether to count up or down')
    prs.add_option('-a', '--action',
                   action='store', default='', dest='action', type='string',
                   help='optional action at end of countdown')
    (opts, args) = prs.parse_args(argv)

    if opts.count.lower() != 'down' and opts.action != '':
        raise BSCR.Error('--action is only meaningful for --count down')

    if opts.count.lower() == 'down':
        count_down(args[1], opts.action)
    else:
        count_up()


# ---------------------------------------------------------------------------
def count_down(hms, action):
    """
    Count from high to low -- countdown timer
    """
    print 'hms = ', hms
    print 'action = ', action
    if ':' in hms:
        secs = hms_seconds(hms)
    else:
        secs = int(hms)

    # print "secs = ", secs
    while 0 < secs:
        sys.stdout.write("%d     " % secs)
        sys.stdout.flush()
        time.sleep(1.0)
        sys.stdout.write("\r")
        secs = secs - 1

    if action != '':
        print action
        os.system(action)


# ---------------------------------------------------------------------------
def count_up():
    """
    Count from low to high -- stopwatch
    """
    minute = 0
    sys.stdout.write('%02d: ' % minute)
    minute += 1
    dec = 0
    while True:
        if (0 == ((dec+1) % 60)):
            sys.stdout.write('%d\n%02d: ' % (int((dec+1)/10), minute))
            minute += 1
            dec = 0
        elif 0 == ((dec+1) % 10):
            sys.stdout.write('%d' % int((dec+1)/10))
            dec += 1
        elif 0 == ((dec+1) % 5):
            sys.stdout.write('+')
            dec += 1
        else:
            sys.stdout.write('.')
            dec += 1
        sys.stdout.flush()
        time.sleep(1.0)


# ---------------------------------------------------------------------------
def hms_seconds(hms):
    """
    Convert HH:MM:SS to seconds
    !@! should this go in util?
    """
    hour, minute, second = hms.split(':')
    return int(second) + 60 * (int(minute) + 60 * int(hour))


# ---------------------------------------------------------------------------
def usage():
    """
    usage
    """
    return """chron

    chronometer/stopwatch"""

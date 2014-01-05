#!/usr/bin/python
"""
replay - monitor the output of a command

Repetitively clear the screen and run a command so changes in its
output can be observed in real time.

USAGE

   replay -c "<command>"
   replay [-i <time>] "<command>"

OPTIONS

   -c        Update the screen when the output changes
   -i <sec>  Update the screen every <sec> seconds

DESCRIPTION

Repeatedly display the output of a command or series of commands until
the user interrupts the program.

With the -c option, the output is updated when it changes. The command
is run once per second.

With the -i option, the output is updated every <interval> seconds.

The default interval is 10 seconds

LICENSE

Copyright (C) 2011 - <the end of time>  Tom Barron
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
import pdb
import sys
import time
import toolframe


# -----------------------------------------------------------------------------
def main(argv=None):
    p = optparse.OptionParser()
    p.add_option('-c', '--change',
                 action='store_true', default=False, dest='change',
                 help='update on change')
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under debugger')
    p.add_option('-i', '--interval',
                 action='store', default=10, dest='interval', type='int',
                 help='seconds between updates')
    p.add_option('-p', '--prompt',
                 action='store_true', default=False, dest='prompt',
                 help='update on user input')
    (o, a) = p.parse_args(argv)

    if o.debug:
        pdb.set_trace()

    start = time.time()
    cmd = " ".join(a[1:])
    old_stuff_s = ""
    while True:
        f = os.popen(cmd, "r")
        stuff = f.readlines()
        f.close()
        stuff_s = " ".join(stuff)

        if o.prompt:
            report(start, cmd, stuff_s)
            x = raw_input('Press ENTER to continue...')
        elif o.change:
            if stuff_s != old_stuff_s:
                report(start, cmd, stuff_s)
                old_stuff_s = stuff_s
            time.sleep(1.0)
        else:
            report(start, cmd, stuff_s)
            time.sleep(o.interval)


# -----------------------------------------------------------------------------
def report(start, cmd, stuff_s):
    os.system("clear")
    print("Running %s since %s" % (ymdhms(time.time() - start),
                                   time.strftime("%Y.%m%d %H:%M:%S",
                                                 time.localtime(start))))
    print(cmd)
    print(" " + stuff_s)


# -----------------------------------------------------------------------------
def ymdhms(seconds):
    S = seconds % 60
    minutes = (seconds - S)/60
    rval = "%02d" % S

    M = minutes % 60
    hours = (minutes - M)/60
    if 0 < minutes:
        rval = "%02d:%s" % (M, rval)

    H = hours % 24
    days = (hours - H)/24
    if 0 < hours:
        rval = "%02d:%s" % (H, rval)

    if 0 < days:
        rval = "%d %s" % (days, rval)

    return rval

try:
    toolframe.ez_launch(main)
except KeyboardInterrupt:
    sys.exit(0)

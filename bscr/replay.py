#!/usr/bin/env python
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
import os
import pdb
import sys
import time
import toolframe
import util as U


# -----------------------------------------------------------------------------
def main(argv=None):
    """
    Main entry point for replay program.

    Run a command repeatedly to view its changing output on a time scheule
    (say, once every five seconds) or to regenerate an output when a file
    is updated.
    """
    cmdline = U.cmdline([{'opts': ['-c', '--change'],
                          'action': 'store_true',
                          'default': False,
                          'dest': 'change',
                          'help': 'update on change',
                         },
                         {'opts': ['-d', '--debug'],
                          'action': 'store_true',
                          'default': False,
                          'dest': 'debug',
                          'help': 'run under debugger',
                         },
                         {'opts': ['-i', '--interval'],
                          'action': 'store',
                          'default': 10,
                          'dest': 'interval',
                          'help': 'seconds between updates',
                         },
                         {'opts': ['-p', '--prompt'],
                          'action': 'store_true',
                          'default': False,
                          'dest': 'prompt',
                          'help': 'update on user input',
                         },
                         {'opts': ['-t', '--trigger'],
                          'action': 'store',
                          'default': '',
                          'dest': 'pathname',
                          'help': 'update when mtime on pathname changes',
                         },
                        ])
    (opts, args) = cmdline.parse(argv)
    if opts.debug:
        pdb.set_trace()

    try:
        start = time.time()
        cmd = " ".join(args)
        old_stuff_s = ""
        while True:
            rbl = os.popen(cmd, "r")
            stuff = rbl.readlines()
            rbl.close()
            stuff_s = " ".join(stuff)

            if opts.prompt:
                report(start, cmd, stuff_s)
                _ = raw_input('Press ENTER to continue...')
            elif opts.change:
                if stuff_s != old_stuff_s:
                    report(start, cmd, stuff_s)
                    old_stuff_s = stuff_s
                time.sleep(1.0)
            elif opts.pathname != '':
                when = U.mtime(opts.pathname)
                report(start, cmd, stuff_s)
                while when == U.mtime(opts.pathname):
                    time.sleep(1.0)
            else:
                report(start, cmd, stuff_s)
                time.sleep(float(opts.interval))
    except KeyboardInterrupt:
        print("")
        sys.exit()


# -----------------------------------------------------------------------------
def report(start, cmd, stuff_s):
    """
    Clear the screen and output 1) info about how long we've been going,
    2) the command we're running, and 3) the command's output
    """
    os.system("clear")
    print("Running %s since %s" % (ymdhms(time.time() - start),
                                   time.strftime("%Y.%m%d %H:%M:%S",
                                                 time.localtime(start))))
    print(cmd)
    print(" " + stuff_s)


# -----------------------------------------------------------------------------
def ymdhms(seconds):
    """
    Convert a number of seconds to day-HH:MM:SS. This might be replaceable
    with something from util.
    """
    rem_s = seconds % 60
    minutes = (seconds - rem_s)/60
    rval = "%02d" % rem_s

    rem_m = minutes % 60
    hours = (minutes - rem_m)/60
    if 0 < minutes:
        rval = "%02d:%s" % (rem_m, rval)

    rem_h = hours % 24
    days = (hours - rem_h)/24
    if 0 < hours:
        rval = "%02d:%s" % (rem_h, rval)

    if 0 < days:
        rval = "%d %s" % (days, rval)

    return rval

# -----------------------------------------------------------------------------
# try:
#     toolframe.ez_launch(__name__, main)
# except KeyboardInterrupt:
#     sys.exit(0)

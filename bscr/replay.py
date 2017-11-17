#!/usr/bin/env python
"""
replay - monitor the output of a command

Repetitively clear the screen and run a command so changes in its
output can be observed in real time.

Usage:   replay [-d] [-i ITERS] COMMAND
         replay [-d] [-i ITERS] -s INTERVAL COMMAND
         replay [-d] [-i ITERS] -p COMMAND
         replay [-d] [-i ITERS] -t FILEPATH COMMAND

OPTIONS

   -d           Use the python debugger
   -s INTERVAL  Run the command every INTERVAL seconds
   -i ITERS     Run the command ITERS times then exit
   -p           Run the command when user hits ENTER
   -t FILEPATH  Run the command when FILEPATH timestamp changes

DESCRIPTION

Repeatedly display the output of a command or series of commands until
the user interrupts the program.

With the no option (other than -d), the output is updated when it changes. The
command is run once per second but the output is only reported when it changes.

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
from docopt_dispatch import dispatch
import os
import pdb
import pexpect
import time


# -----------------------------------------------------------------------------
def main(args=None):
    """
    Let's get it started in here!
    """
    dispatch(__doc__)


# -----------------------------------------------------------------------------
@dispatch.on('-i', '-s', 'COMMAND')
def rp_iter_ival(**kwa):
    """
    Replay COMMAND whenever its output changes. If -s SECONDS is specified,
    pause for that many seconds betwen iterations. Execute the number of
    iterations specified by -i.
    """
    if kwa['d']:
        pdb.set_trace()

    cmd = kwa['COMMAND']
    stime = int(kwa['s'])
    iters = int(kwa['i'])

    result_a = pexpect.run(cmd)
    print result_a
    iters -= 1
    while 0 < iters:
        time.sleep(stime)
        result_a = pexpect.run(cmd)
        print result_a
        iters -= 1


# -----------------------------------------------------------------------------
@dispatch.on('-s', 'COMMAND')
def rp_interval(**kwa):
    """
    Replay COMMAND whenever its output changes. If -s SECONDS is specified,
    pause for that many seconds betwen iterations.
    """
    if kwa['d']:
        pdb.set_trace()

    cmd = kwa['COMMAND']
    stime = int(kwa['s'])
    # iters = int(kwa['i'])

    result = pexpect.run(cmd)
    print result
    while True:
        time.sleep(stime)
        result = pexpect.run(cmd)
        print result


# -----------------------------------------------------------------------------
@dispatch.on('-p', 'COMMAND')
def rp_prompt(**kwa):
    """
    Replay COMMAND whenever user hits ENTER.
    """
    if kwa['d']:
        pdb.set_trace()

    cmd = kwa['COMMAND']
    while True:
        result = pexpect.run(cmd)
        print " "
        print result
        raw_input("Hit ENTER...")
        cmd = kwa['COMMAND']


# -----------------------------------------------------------------------------
@dispatch.on('-i', 'COMMAND')
def rp_iters(**kwa):
    if kwa['d']:
        pdb.set_trace()

    cmd = kwa['COMMAND']
    icount = int(kwa['i'])
    for _ in range(icount):
        result = pexpect.run(cmd)
        print result
        time.sleep(1.0)


# -----------------------------------------------------------------------------
@dispatch.on('COMMAND')
def rp_change(**kwa):
    """
    Replay COMMAND whenever its output changes.
    """
    if kwa['d']:
        pdb.set_trace()

    cmd = kwa['COMMAND']
    result_a = pexpect.run(cmd)
    print result_a
    result_b = pexpect.run(cmd)
    while True:
        while result_b == result_a:
            time.sleep(1.0)
            result_b = pexpect.run(cmd)
        print result_b
        result_a = result_b


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

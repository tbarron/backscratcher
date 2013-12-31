#!/usr/bin/python
"""
show lineage of the current process

pstrack

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

import glob
import optparse
import os
import pdb
import re
import sys
import toolframe
import unittest

try:
    subproc_available = True
    import subprocess
except:
    subproc_available = False


# ---------------------------------------------------------------------------
def main(args):
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
#     p.add_option('-v', '--verbose',
#                  action='store_true', default=False, dest='verbose',
#                  help='report more of what is going on')
    (o, a) = p.parse_args(args)

    if (o.debug):
        pdb.set_trace()

    pt = get_process_list()

    pid = str(os.getpid())
    while pid in pt.keys():
        print("%s %s" % (pid, pt[pid]['cmd']))
        pid = pt[pid]['ppid']


# ---------------------------------------------------------------------------
def get_process_list():
    """
    Build a process tree of the form

       pd = {pid1: {'pid': pid1, 'ppid': parent-pid, 'cmd': command},
             pid2: {'pid': pid2, 'ppid': parent-pid, 'cmd': command},
             ...}
    """
    pd = {}
    if os.path.exists("/proc/%d" % os.getpid()):
        # We have a /proc directory -- get the tree from there
        procs = glob.glob("/proc/[0-9]*")
        for pdir in procs:
            d = {}
            d['pid'] = pdir.replace("/proc/", "")
            d['ppid'] = get_ppid(pdir)
            d['cmd'] = get_cmd(pdir)
            pd[d['pid']] = d
    else:
        if subproc_available:
            p = subprocess.Popen("ps -ef".split(),
                                 stdin=None,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            (out, err) = p.communicate()
            ptxt = out.split('\n')
        else:
            p = os.popen("ps -ef", "r")
            ptxt = [x.strip('\n') for x in p.readlines()]

        rgx = r'\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)' \
              + '\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'
        for pline in ptxt:
            q = re.search(rgx, pline)
            d = {}
            if q:
                d['pid'] = q.groups()[1]
                d['ppid'] = q.groups()[2]
                d['cmd'] = q.groups()[7]
                pd[d['pid']] = d

    return pd


# ---------------------------------------------------------------------------
def get_cmd(pdir):
    f = open("%s/cmdline" % pdir)
    line = f.readline()
    f.close()
    rval = line.replace("\000", " ").strip()
    return rval


# ---------------------------------------------------------------------------
def get_ppid(pdir):
    f = open("%s/stat" % pdir)
    line = f.readline()
    f.close()
    rval = line.split()[3]
    return rval


# ---------------------------------------------------------------------------
def usage():
    print("usage: pstrack")
    sys.exit(1)

# ---------------------------------------------------------------------------
toolframe.ez_launch(main)

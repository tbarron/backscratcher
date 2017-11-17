"""
show lineage of the current process

Usage:
    pstrack [-d] [-v]

Options:
    -d          debug
    -v          verbose

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

import docopt
import glob
import optparse
import os
import pdb
import re
import sys

try:
    import subprocess
except ImportError:
    pass


# ---------------------------------------------------------------------------
def main(args=None):
    """
    Entry point
    """
    args = args or sys.argv
    opts = docopt.docopt(__doc__, args)
    if opts['-d']:
        pdb.set_trace()

    procd = get_process_list()

    pid = str(os.getpid())
    while pid in procd.keys():
        print("%s %s" % (pid, procd[pid]['cmd']))
        pid = procd[pid]['ppid']


# ---------------------------------------------------------------------------
def get_process_list():
    """
    Build a process tree of the form

       pd = {pid1: {'pid': pid1, 'ppid': parent-pid, 'cmd': command},
             pid2: {'pid': pid2, 'ppid': parent-pid, 'cmd': command},
             ...}
    """
    proctree = {}
    if os.path.exists("/proc/%d" % os.getpid()):
        # We have a /proc directory -- get the tree from there
        procs = glob.glob("/proc/[0-9]*")
        for pdir in procs:
            pdat = {}
            pdat['pid'] = pdir.replace("/proc/", "")
            pdat['ppid'] = get_ppid(pdir)
            pdat['cmd'] = get_cmd(pdir)
            proctree[pdat['pid']] = pdat
    else:
        if 'subprocess' in sys.modules:
            xbl = subprocess.Popen("ps -ef".split(),
                                   stdin=None,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
            (out, _) = xbl.communicate()
            ptxt = out.split('\n')
        else:
            pipe = os.popen("ps -ef", "r")
            ptxt = [x.strip('\n') for x in pipe.readlines()]

        rgx = ''.join([r'\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',
                       r'\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'])
        for pline in ptxt:
            result = re.search(rgx, pline)
            pdat = {}
            if result:
                pdat['pid'] = result.groups()[1]
                pdat['ppid'] = result.groups()[2]
                pdat['cmd'] = result.groups()[7]
                proctree[pdat['pid']] = pdat

    return proctree


# ---------------------------------------------------------------------------
def get_cmd(pdir):
    """
    Read the command associated with a process id
    """
    rbl = open("%s/cmdline" % pdir)
    line = rbl.readline()
    rbl.close()
    rval = line.replace("\000", " ").strip()
    return rval


# ---------------------------------------------------------------------------
def get_ppid(pdir):
    """
    Retrieve a process' parent process id
    """
    rbl = open("%s/stat" % pdir)
    line = rbl.readline()
    rbl.close()
    rval = line.split()[3]
    return rval


# ---------------------------------------------------------------------------
def usage():
    """
    Show the usage for this program
    """
    print("usage: pstrack")
    sys.exit(1)

#!/usr/bin/python
"""
file manipulator

History
  2006.0306     tpb   0.9    add functions add_cr, rm_cr
  2009.1025     tpb   0.10   convert to python
  2011.0202     tpb   0.11   add -L trick
                             add stubs for future routines

Usage:
          fl [-d] [-n] diff FILE ...
          fl [-d] [-n] edit
          fl [-d] [-n] revert FILE
          fl [-d] [-n] rm_cr
          fl [-d] [-n] save FILE ...
          fl [-d] [-n] set_atime_to_mtime FILE ...
          fl [-d] [-n] set_mtime_to_atime FILE ...
          fl [-d] [-n] times
          fl [-d] [-n] unreadable

Examples:

  fl [-n/--noexec] {save|diff|revert} file1 file2 file3 ...
  fl [-n/--noexec] [--nopreserve] {apply|backout} filename

The script fl contains a number of subfunctions. In the order they are
most likely to be used, they are:

 - help: display a list of functions and information about each

 - save: saving the current version of file as a dated generation
   file (a generation is a previous version of a file)

 - diff: examining the differences between the current version of a
   file and its most recently saved generation

 - revert: reverting to the most recently saved generation of a
   file

 - set_atime_to_mtime: for each file listed on the command line, set
   its atime to be equal to its mtime

 - set_mtime_to_atime: for each file listed on the command line, set
   its mtime to be equal to its atime

 - apply: applying a set of individual files

 - backout: backing out a set of files applied with apply

The first three operate on individual files, although multiple
filenames can be given on the command line. The last two operate on
groups of files.

Options
-------

The --noexec option causes the script to report what it would do
without actually copying or moving any files. The option can be
abbreviated to -n.

Subfunctions
------------

In alphabetical order, each of the subfunctions are
described below:

diff

   Run diff on the current file and the most recently saved copy.

revert

   The most recent saved copy of the file is retrieved. The updated
   copy of the file is moved to <filename>.new. If, in the directory
   where the file lives, there is a subdirectory named 'old', it is
   expected that old generations of files will be in the 'old'
   subdirectory.

save

   Make a copy of each file mentioned on the command line, appending
   it's mtime in the form YYYY-MM-DD to the name and preserving mtime
   on the the copy. This is generally a good thing to do before making
   changes to sensitive system configuration files, important admin
   scripts, etc. In the jargon of this document, each saved copy of a
   file is called a 'generation'.

   If necessary, to avoid filename collisions, the script will append
   a lowercase letter to the end of the filename, beginning with "a".

   If a filename includes a path, the generation will be created under
   the same directory that contains the original file. If an 'old'
   sub-directory is present, the generation will be written there.

License
-------

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
from docopt_dispatch import dispatch
import optparse
import os
import pdb
import re
import string
import sys

import util
BSCR = util.package_module(__name__)


# -----------------------------------------------------------------------------
def main(args=None):
    """
    CLEP
    """
    dispatch(__doc__)


# ---------------------------------------------------------------------------
@dispatch.on('diff')
def fl_diff(**kwa):
    """
    diff - compare file to its most recently 'saved' version

    usage: fl diff file1 file2 file3 ...

    """
    if kwa["d"]:
        pdb.set_trace()

    for filename in kwa["FILE"]:
        dirname = os.path.dirname(filename)
        if dirname == '':
            dirname = '.'

        counterpath = most_recent_prefix_match(dirname,
                                               os.path.basename(filename))
        if counterpath is None:
            print("No prefix match found for {}".format(filename))
        else:
            cmd = 'diff %s %s' % (counterpath, filename)
            print cmd
            print util.run(cmd, not kwa['n'])
            sys.stdout.flush()


# ---------------------------------------------------------------------------
def fl_edit(argl):
    """edit - edit files in place

    usage: fl edit [-i <suffix>] -e <edit-cmd> file1 file2 file3 ...

    """
    prs = optparse.OptionParser()
    prs.add_option('-d', '--debug',
                   default=False, action='store_true', dest='debug',
                   help='run the debugger')
    prs.add_option('-e', '--edit',
                   default='', action='store', dest='edit_cmd',
                   help='edit command')
    prs.add_option('-i', '--init',
                   default='', action='store', dest='suffix',
                   help='suffix for original files')
    (opts, args) = prs.parse_args(argl)

    if opts.debug:
        pdb.set_trace()

    if opts.suffix == '':
        suffix = 'original'
    else:
        suffix = opts.suffix

    if opts.edit_cmd == '':
        util.fatal("usage: fl edit [-i <suffix>] -e <cmd> f1 f2 ...")

    ecmd = opts.edit_cmd.split(opts.edit_cmd[1])
    if all([ecmd[0] != 's', ecmd[0] != 'y']):
        raise BSCR.Error("Only 's' and 'y' supported for -e right now")

    if 4 != len(ecmd):
        raise BSCR.Error("usage: ... -e '[sy]/before/after/' ...")

    (opn, prev, post) = ecmd[0:3]

    if 0 == len(args):
        util.fatal("no files on command line to edit")
    else:
        for filename in args:
            editfile(filename, opn, prev, post, suffix)


# ---------------------------------------------------------------------------
def editfile(filename, opn, prev, post, suffix=None):
    """
    Edit *filename*, replacing *prev* with *post* and renaming the original
    file by appending *suffix* to its name
    """
    if opn != 's' and opn != 'y':
        raise BSCR.Error("Invalid operation: '%s'" % opn)
    if suffix is None or suffix == '':
        suffix = 'original'

    fn_orig = "%s.%s" % (filename, suffix)
    fn_new = "%s.%s" % (filename, "new")
    inc = open(filename, 'r')
    out = open(fn_new, 'w')

    if opn == 's':
        for line in inc.readlines():
            nline = re.sub(prev, post, line)
            out.write(nline)
    elif opn == 'y':
        prev = prev.decode('string_escape')
        if post == '':
            for line in inc.readlines():
                nline = line.translate(None, prev)
                out.write(nline)
        else:
            tbl = string.maketrans(prev, post)
            for line in inc.readlines():
                nline = line.translate(tbl)
                out.write(nline)

    out.close()
    inc.close()

    os.rename(filename, fn_orig)
    os.rename(fn_new, filename)


# ---------------------------------------------------------------------------
@dispatch.on('revert')
def fl_revert(**kwa):
    """revert - revert <file> back to its most recent saved version

    usage: fl revert <file> <file> <file> ...

    For each file listed in the command line, look for 'save'd version
    and bring it back. The current file is renamed <file>.new.
    """
    if kwa["d"]:
        pdb.set_trace()
    for filename in kwa["FILE"]:
        dirn = os.path.dirname(filename)
        if dirn == '':
            dirn = '.'

        counterpath = most_recent_prefix_match(dirn,
                                               os.path.basename(filename))

        newname = filename + ".new"
        if kwa["n"]:
            print("would do 'os.rename({0}, {1})'".format(filename,
                                                          newname))
            print("would do 'os.rename({0}, {1})'".format(counterpath,
                                                          filename))
        else:
            print("os.rename({0}, {1})".format(filename, newname))
            os.rename(filename, newname)
            print("os.rename({0}, {1})".format(counterpath, filename))
            os.rename(counterpath, filename)


# ---------------------------------------------------------------------------
def fl_rm_cr(args):
    """rm_cr - remove carriage returns from file

    usage: fl rm_cr file file file ...

    Filter out CR charaters from a file.
    """
    for filename in args:
        rble = open(filename, 'r')
        data = rble.readlines()
        rble.close()

        edited = [x.replace('\r', '') for x in data]

        wname = "%s.%d" % (filename, os.getpid())
        wble = open(wname, 'w')
        wble.writelines(edited)
        wble.close()

        os.rename(filename, "%s~" % filename)
        os.rename(wname, filename)


# ---------------------------------------------------------------------------
def fl_save(args):
    """save - snapshot a file with a timestamp in the name

    usage: fl save file file file

    For each file, create file.YYYY.mmdd.
    """
    print("under construction")


# ---------------------------------------------------------------------------
@dispatch.on('set_atime_to_mtime')
def fl_set_atime_to_mtime(**kwa):
    """set_atime_to_mtime - atime <= mtime

    usage: fl set_atime_to_mtime file file file ...

    For each file listed, set the file's atime to be the same as its
    mtime value.
    """
    if kwa["d"]:
        pdb.set_trace()
    for filename in kwa["FILE"]:
        mdat = os.stat(filename)
        os.utime(filename, (mdat.st_mtime, mdat.st_mtime))


# ---------------------------------------------------------------------------
@dispatch.on('set_mtime_to_atime')
def fl_set_mtime_to_atime(**kwa):
    """set_mtime_to_atime - mtime <= atime

    usage: fl set_mtime_to_atime file file file ...

    For each file listed, set the file's mtime to be the same as its
    atime value.
    """
    if kwa["d"]:
        pdb.set_trace()
    for filename in kwa["FILE"]:
        mdat = os.stat(filename)
        os.utime(filename, (mdat.st_atime, mdat.st_atime))


# ---------------------------------------------------------------------------
def fl_times(args):
    """times - report the times associated with a file

    usage: fl times file file file ...

    For each file, report the access, mod, and create times.
    """
    print("under construction")


# ---------------------------------------------------------------------------
def fl_unreadable(args):
    """unreadable - descend a tree and report unreadable files

    usage: fl unreadable <root>

    Descend the directory at <root> and report unreadable files.
    """
    print("under construction")


# ---------------------------------------------------------------------------
def most_recent_prefix_match(dirn, filename):
    """
    Return the path of the newest file in dir that prefix-matches filename
    but does not match exactly (filename is not a path, only a filename).
    """
    dirl = os.listdir(dirn)
    if os.path.exists('%s/old' % dirn):
        dirl.extend(['old/%s' % x for x in os.listdir('%s/old' % dirn)])
    # print list

    recent_time = 0
    recent_file = ''
    for candidate in dirl:
        mdat = os.stat('%s/%s' % (dirn, candidate))
        bfile = os.path.basename(candidate)
        if all([candidate != filename,
                bfile.startswith(filename),
                recent_time < mdat.st_mtime]):
            recent_time = mdat.st_mtime
            recent_file = candidate

    # print 'recent_file = %s' % recent_file
    if recent_file != '':
        # print 'mrpm returning %s/%s' % (dir, recent_file)
        return '%s/%s' % (dirn, recent_file)
    else:
        return None

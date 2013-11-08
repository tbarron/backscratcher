#!/usr/bin/python
"""
file manipulator

History
  2006.0306     tpb   0.9    add functions add_cr, rm_cr
  2009.1025     tpb   0.10   convert to python
  2011.0202     tpb   0.11   add -L trick
                             add stubs for future routines

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

import os
import pdb
import random
import re
import stat
import sys
import tpbtools
import testhelp
import time
import toolframe
import unittest

from optparse import *


# ---------------------------------------------------------------------------
def fl_help(args):
    """help - show this list

    usage: fl help [function-name]

    If a function name is given, show the __doc__ member of the function.
    Otherwise, show a list of functions based on the first line of
    each __doc__ member.
    """
    global d

    p = OptionParser()
    # p = add_option('-e', '--exec',
    #                action='store_true', default=False, dest='xable',
    #                help='otherwise dryrun')
    (o, a) = p.parse_args(args)
    if 0 < len(a) and 'fl_%s' % a[0] in d:
        x = eval('fl_%s.__doc__' % a[0])
        print '\n    ' + x
        return

    for fcn in d:
        if 'fl_' in fcn:
            x = eval('%s.__doc__' % fcn)
            f = x.split('\n')[0]
            print '   %s' % f


# ---------------------------------------------------------------------------
def fl_diff(args):
    """diff - compare file to its most recently 'saved' version

    usage: fl diff file1 file2 file3 ...

    """
    p = OptionParser()
    p.add_option('-n', '--noexec',
                 default=True, action='store_false', dest='xable',
                 help='just do a dry run')
    (o, a) = p.parse_args(args)

    for filename in a:
        dirname = os.path.dirname(filename)
        if dirname == '':
            dirname = '.'

        counterpath = most_recent_prefix_match(dirname,
                                               os.path.basename(filename))

        cmd = 'diff %s %s' % (counterpath, filename)
        print cmd
        sys.stdout.flush()
        tpbtools.run(cmd, o.xable)


# ---------------------------------------------------------------------------
def fl_revert(args):
    """revert - revert <file> back to its most recent saved version

    usage: fl revert <file> <file> <file> ...

    For each file listed in the command line, look for 'save'd version
    and bring it back. The current file is renamed <file>.new.
    """
    p = OptionParser()
    p.add_option('-n', '--noexec',
                 default=True, action='store_false', dest='xable',
                 help='just do a dry run')
    (o, a) = p.parse_args(args)

    for f in a:
        dir = os.path.dirname(f)
        if dir == '':
            dir = '.'

        counterpath = most_recent_prefix_match(dir, os.path.basename(f))

        tpbtools.run('mv %s %s.new' % (f, f), o.xable)
        tpbtools.run('mv %s %s' % (counterpath, f), o.xable)


# ---------------------------------------------------------------------------
def fl_rm_cr(args):
    """rm_cr - remove carriage returns from file

    usage: fl rm_cr file file file ...

    Filter out CR charaters from a file.
    """
    for filename in args:
        f = open(filename, 'r')
        d = f.readlines()
        f.close()

        r = [x.replace('\r', '') for x in d]

        wname = "%s.%d" % (filename, os.getpid())
        f = open(wname, 'w')
        f.writelines(r)
        f.close()

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
def fl_set_atime_to_mtime(args):
    """set_atime_to_mtime - atime <= mtime

    usage: fl set_atime_to_mtime file file file ...

    For each file listed, set the file's atime to be the same as its
    mtime value.
    """
    for filename in args:
        s = os.stat(filename)
        os.utime(filename, (s[stat.ST_MTIME], s[stat.ST_MTIME]))


# ---------------------------------------------------------------------------
def fl_set_mtime_to_atime(args):
    """set_mtime_to_atime - mtime <= atime

    usage: fl set_mtime_to_atime file file file ...

    For each file listed, set the file's mtime to be the same as its
    atime value.
    """
    for filename in args:
        s = os.stat(filename)
        os.utime(filename, (s[stat.ST_ATIME], s[stat.ST_ATIME]))


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
def most_recent_prefix_match(dir, filename):
    """
    Return the path of the newest file in dir that prefix-matches filename
    but does not match exactly (filename is not a path, only a filename).
    """
    list = os.listdir(dir)
    if os.path.exists('%s/old' % dir):
        list.extend(['old/%s' % x for x in os.listdir('%s/old' % dir)])
    # print list

    recent_time = 0
    recent_file = ''
    for file in list:
        s = os.stat('%s/%s' % (dir, file))
        bfile = os.path.basename(file)
        if (file != filename and bfile.startswith(filename)
                and recent_time < s[stat.ST_MTIME]):
            recent_time = s[stat.ST_MTIME]
            recent_file = file

    # print 'recent_file = %s' % recent_file
    if recent_file != '':
        # print 'mrpm returning %s/%s' % (dir, recent_file)
        return '%s/%s' % (dir, recent_file)


# ---------------------------------------------------------------------------
def cleanup_tests():
    if os.path.basename(os.getcwd()) == 'fl_tests':
        os.chdir('..')

    if os.path.exists('./fl_tests'):
        tpbtools.rmrf('./fl_tests')


# ---------------------------------------------------------------------------
class FLTests(unittest.TestCase):
    # -----------------------------------------------------------------------
    def setUp(self):
        if os.path.basename(os.getcwd()) == 'fl_tests':
            return

        if not os.path.exists('fl_tests'):
            os.mkdir('fl_tests')
            os.mkdir('fl_tests/old')

        os.chdir('fl_tests')

    # -----------------------------------------------------------------------
    def test_most_recent_prefix_match(self):
        """
        Test the routine most_recent_prefix_match()
        """
        tpbtools.writefile('mrpm1', ['this is a test file'])
        tpbtools.writefile('mrpm2', ['this is another test file'])
        os.system('cp mrpm1 mrpm1.2009-10-01')
        os.system('cp mrpm2 old/mrpm2.2009-08-31')

        a = most_recent_prefix_match('.', 'mrpm1')
        testhelp.expectVSgot('./mrpm1.2009-10-01', a)

        a = most_recent_prefix_match('.', 'mrpm2')
        testhelp.expectVSgot('./old/mrpm2.2009-08-31', a)

    # -----------------------------------------------------------------------
    def test_diff(self):
        """
        Test diff
        """
        tpbtools.writefile('mrpm1', ['this is a test file\n'])
        tpbtools.writefile('mrpm2', ['this is another test file\n'])
        tpbtools.writefile('mrpm1.2009-10-01', ['copy of test file\n'])
        tpbtools.writefile('old/mrpm2.2009-08-31',
                           ['copy of another test file\n'])

        expected = ['diff ./mrpm1.2009-10-01 mrpm1\n',
                    '1c1\n',
                    '< copy of test file\n',
                    '---\n',
                    '> this is a test file\n']
        f = os.popen('../fl diff mrpm1')
        got = f.readlines()
        f.close()
        testhelp.expectVSgot(expected, got)

        expected = ['diff ./old/mrpm2.2009-08-31 mrpm2\n',
                    '1c1\n',
                    '< copy of another test file\n',
                    '---\n',
                    '> this is another test file\n']
        f = os.popen('../fl diff mrpm2')
        got = f.readlines()
        f.close()
        testhelp.expectVSgot(expected, got)

    # -----------------------------------------------------------------------
    def test_revert(self):
        """
        Test revert
        """
        tpbtools.writefile('mrpm1', ['this is a test file\n'])
        tpbtools.writefile('mrpm2', ['this is another test file\n'])
        tpbtools.writefile('mrpm1.2009-10-01', ['reverted\n'])
        tpbtools.writefile('old/mrpm2.2009-08-31',
                           ['REVERTED\n'])

        os.system('../fl revert mrpm1')
        assert(os.path.exists('mrpm1.new'))
        assert(os.path.exists('mrpm1'))
        assert(not os.path.exists('mrpm1.2009-10-01'))
        assert(tpbtools.contents('mrpm1') == ['reverted\n'])

        os.system('../fl revert mrpm2')
        assert(os.path.exists('mrpm2.new'))
        assert(os.path.exists('mrpm2'))
        assert(not os.path.exists('old/mrpm2.2009-08-31'))
        assert(tpbtools.contents('mrpm2') == ['REVERTED\n'])

    # -----------------------------------------------------------------------
    def test_atom(self):
        """
        Test set_atime_to_mtime
        """
        filename = 'atom'
        open(filename, 'w').close()
        os.utime(filename, (time.time() - random.randint(1000, 2000),
                            time.time() + random.randint(1000, 2000)))
        s = os.stat(filename)
        assert(s[stat.ST_ATIME] != s[stat.ST_MTIME])
        fl_set_atime_to_mtime([filename])
        s = os.stat(filename)
        assert(s[stat.ST_ATIME] == s[stat.ST_MTIME])

    # -----------------------------------------------------------------------
    def test_mtoa(self):
        """
        Test set_mtime_to_atime
        """
        filename = 'mtoa'
        open(filename, 'w').close()
        os.utime(filename, (time.time() - random.randint(1000, 2000),
                            time.time() + random.randint(1000, 2000)))
        s = os.stat(filename)
        assert(s[stat.ST_ATIME] != s[stat.ST_MTIME])
        fl_set_mtime_to_atime([filename])
        s = os.stat(filename)
        assert(s[stat.ST_ATIME] == s[stat.ST_MTIME])

# ---------------------------------------------------------------------------
toolframe.tf_launch('fl')

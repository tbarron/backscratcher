#!/usr/bin/python
"""
filter.py - Distinguish interesting from ignorable strings in a list.

Use:
   import filter

   fobj = filter.filter()
   fobj.ignore(r'^\s*#')      # ignore comments
   fobj.ignore(...)           # other regexes to ignore

   for item in list:
       if fobj.is_interesting(item):
           # do something
       else:
           # something else

   Alternatively, fobj.keep() will accept regexes matching items to keep
   and fobj.is_keepable() will return True or False based on whether any
   of the regexes in the keep list match the item.

License:
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

import re
import unittest


# -----------------------------------------------------------------------------
class filter(object):
    # -------------------------------------------------------------------------
    def __init__(self):
        self.IGN = []
        self.KEEP = []

    # -------------------------------------------------------------------------
    def ignore(self, rgx):
        self.IGN.append(rgx)

    # -------------------------------------------------------------------------
    def is_interesting(self, item):
        rval = True
        for r in self.IGN:
            if re.search(r, item):
                rval = False
                break
        return rval

    # -------------------------------------------------------------------------
    def is_keepable(self, item):
        rval = False
        for r in self.KEEP:
            if re.search(r, item):
                rval = True
                break
        return rval

    # -------------------------------------------------------------------------
    def keep(self, rgx):
        self.KEEP.append(rgx)


# -----------------------------------------------------------------------------
class FilterTests(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_constructor(self):
        xyz = filter()
        for attr in ['ignore', 'is_interesting', 'is_keepable',
                     'keep', 'IGN', 'KEEP', '__new__']:
            assert(attr in dir(xyz))

    # -------------------------------------------------------------------------
    def test_ignore(self):
        x = filter()
        x.ignore('12345')
        assert('12345' in x.IGN)
        assert(len(x.IGN) == 1)
        assert('foobar' not in x.IGN)

    # -------------------------------------------------------------------------
    def test_is_interesting(self):
        x = filter()
        x.ignore('abccd')
        assert(not x.is_interesting('one two abccd three four'))
        assert(x.is_interesting('foo bar wokka wokka'))

    # -------------------------------------------------------------------------
    def test_keep(self):
        x = filter()
        x.keep('precious')
        assert('precious' in x.KEEP)
        assert(len(x.KEEP) == 1)
        assert('frippery' not in x.KEEP)

    # -------------------------------------------------------------------------
    def test_is_keepable(self):
        x = filter()
        x.keep('precious')
        assert(x.is_keepable('woo hoo! precious little got done today!'))
        assert(not x.is_keepable('not worth nuthin'))

if __name__ == '__main__':
    unittest.main()

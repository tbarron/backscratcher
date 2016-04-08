#!/usr/bin/python
# pylint: disable=anomalous-backslash-in-string,redefined-builtin
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
class Filter(object):
    """
    A Filter object can be used to select items based on a set of ignorable vs
    keepable regexes
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Initialize
        """
        self.ign = []
        self.keepl = []

    # -------------------------------------------------------------------------
    def ignore(self, rgx):
        """
        Build a list of stuff to ignore
        """
        self.ign.append(rgx)

    # -------------------------------------------------------------------------
    def is_interesting(self, item):
        """
        Return True or False to indicate whether the item is interesting or
        ignorable.
        """
        rval = True
        for element in self.ign:
            if re.search(element, item):
                rval = False
                break
        return rval

    # -------------------------------------------------------------------------
    def is_keepable(self, item):
        """
        Return True or False to indicate whether the item is keepable
        """
        rval = False
        for element in self.keepl:
            if re.search(element, item):
                rval = True
                break
        return rval

    # -------------------------------------------------------------------------
    def keep(self, rgx):
        """
        Add a regex to the keep list
        """
        self.keepl.append(rgx)

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

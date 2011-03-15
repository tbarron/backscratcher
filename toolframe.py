#!/usr/bin/python
"""
toolframe - creating a script with commandline-callable subfunctions

To use this, a script must

To build a tool-style program (i.e., one with multiple entry points
that can be called individually from the command line with a list of
options and arguments):

    * provide a prefix() routine that returns the prefix that will
      indicate command line callable subfunctions

    * provide a collection of callable subfunctions with names like
      '%s_callme' % prefix()

    * Call toolframe.tf_launch() (no args) outside any function

    * Additional features:
    
       * When run as 'program.py -L', symlink program -> program.py is
         created so the program can be easily called from the command
         line without typing the .py suffix.

       * When run as 'program.py', any unittest cases that are defined
         will be run.

       * When run as 'program subfunc <options> <arguments>',
         subfunction prefix_subfunc will be called.

Non-tool-style programs can call toolfram.ez_launch(main) to get the
following:

    * When run as 'program.py -L', a symlink program -> program.py
      will be created so the program can be easily called from the
      command line.

    * When run as 'program.py', any unittest test cases defined will
      be run.

    * When run as 'program <options> <args>', routine main (the one
      passed to ez_launch) will be called with sys.argv as an
      argument.

History
   2011.0209   inception
   2011.0304   figured out to pass routine main to ez_launch
   
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
import re
import sys
import testhelp
import unittest

# ---------------------------------------------------------------------------
def tf_main(args, prefix=None):
    if prefix == None:
        prefix = sys.modules['__main__'].prefix()
    if len(args) < 2:
        tf_help([], prefix=prefix)
    elif args[1] == "help":
        tf_help(args[2:], prefix=prefix)
    else:
        try:
            eval("sys.modules['__main__'].%s_%s(args[2:])" % (prefix, args[1]))
        except IndexError:
            tf_help([], prefix=prefix)
        except NameError:
            print("unrecognized subfunction: %s" % args[1])
            tf_help([], prefix=prefix)
        except:
            raise

# ---------------------------------------------------------------------------
def tf_help(A, prefix=None):
    """help - show this list

    usage: <program> help [function-name]

    If a function name is given, show the functions __doc__ member.
    Otherwise, show a list of functions based on the first line of
    each __doc__ member.
    """
    d = dir(sys.modules['__main__'])
    if prefix == None:
        prefix = sys.modules['__main__'].prefix()
    if 0 < len(A):
        if '%s_%s' % (prefix, A[0]) in d:
            dname = "sys.modules['__main__'].%s_%s.__doc__" % (prefix, A[0])
            x = eval(dname)
            print x
        elif A[0] == 'help':
            x = tf_help.__doc__
            print x
        return

    d.append('tf_help')
    for o in d:
        if o.startswith(prefix + '_'):
            f = o.replace(prefix + '_', '')
            x = eval("sys.modules['__main__'].%s.__doc__" % o)
            docsum = x.split('\n')[0]
            print "   %s" % (docsum)
        elif o == 'tf_help':
            f = 'help'
            docsum = tf_help.__doc__.split('\n')[0]
            print "   %s" % (docsum)
            

# ---------------------------------------------------------------------------
def tf_launch(prefix, cleanup_tests = None):
    if len(sys.argv) == 1 and sys.argv[0] == '':
        return
    sname = sys.argv[0]
    pname = re.sub('.py$', '', sname)
    if sname.endswith('.py') and not os.path.exists(pname):
        print("creating symlink: %s -> %s" % (pname, sname))
        os.symlink(sname, pname)
    elif sys._getframe(1).f_code.co_name in ['?', '<module>']:
        if sname.endswith('.py'):
            testhelp.main(sys.argv)
            if None != cleanup_tests:
                cleanup_tests()
        else:
            tf_main(sys.argv, prefix=prefix)

# ---------------------------------------------------------------------------
def ez_launch(main = None):
    # pdb.set_trace()
    if len(sys.argv) == 1 and sys.argv[0] == '':
        return
    sname = sys.argv[0]
    pname = re.sub('.py$', '', sname)
    if sname.endswith('.py') and not os.path.exists(pname):
        print("creating symlink: %s -> %s" % (pname, sname))
        os.symlink(sname, pname)
    elif sys._getframe(1).f_code.co_name in ['?', '<module>']:
        if sname.endswith('.py'):
            unittest.main()
        elif main == None:
            raise StandardError("Pass your main routine to ez_launch")
        else:
            main(sys.argv)

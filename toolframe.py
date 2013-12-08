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
import shlex
import sys
import testhelp
import traceback as tb
import unittest


# ---------------------------------------------------------------------------
def tf_main(args, prefix=None, noarg='help'):
    if prefix is None:
        prefix = sys.modules['__main__'].prefix()

    args = tf_dispatch_prolog(prefix, args)

    if len(args) < 2:
        if noarg == 'help':
            tf_help([], prefix=prefix)
        elif noarg == 'shell':
            tf_shell(prefix, args)
        else:
            raise StandardError('noarg must be "help" or "shell", not "%s"' %
                                noarg)
    elif args[1] == "help":
        tf_help(args[2:], prefix=prefix)
    else:
        tf_dispatch(prefix, args[1:])

    tf_dispatch_epilog(prefix, args)


# ---------------------------------------------------------------------------
def tf_dispatch(prefix, args):
    if args[0] == 'help':
        tf_help(args[1:], prefix=prefix)
    else:
        try:
            eval("sys.modules['__main__'].%s_%s(args[1:])" % (prefix, args[0]))
        except IndexError:
            tb.print_exc()
            tf_help([], prefix=prefix)
        except NameError:
            tb.print_exc()
            print("unrecognized subfunction: %s" % args[0])
            tf_help([], prefix=prefix)
        except AttributeError:
            tb.print_exc()
            print("unrecognized subfunction: %s" % args[0])
            tf_help([], prefix=prefix)
        except SystemExit as e:
            tb.print_exc()
            print(e)


# ---------------------------------------------------------------------------
def tf_dispatch_epilog(prefix, args):
    try:
        eval("sys.modules['__main__'].%s_epilog(args)" % prefix)
    except:
        # no epilog defined -- carry on
        pass


# ---------------------------------------------------------------------------
def tf_dispatch_prolog(prefix, args):
    rval = args
    try:
        rval = eval("sys.modules['__main__'].%s_prolog(args)" % prefix)
    except SystemExit:
        sys.exit(0)
    except:
        # no prolog defined -- carry on
        pass
    return rval


# ---------------------------------------------------------------------------
def tf_help(A, prefix=None):
    """help - show this list

    usage: <program> help [function-name]

    If a function name is given, show the functions __doc__ member.
    Otherwise, show a list of functions based on the first line of
    each __doc__ member.
    """
    d = dir(sys.modules['__main__'])
    if prefix is None:
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
            x = getattr(sys.modules['__main__'], o)
            ds = x.__doc__
            f = o.replace(prefix + '_', '')
            if ds is not None:
                docsum = ds.split('\n')[0]
            else:
                docsum = "%s - no docstring provided" % f
            print "   %s" % (docsum)
        elif o == 'tf_help':
            f = 'help'
            docsum = tf_help.__doc__.split('\n')[0]
            print "   %s" % (docsum)


# -----------------------------------------------------------------------------
def tf_launch(prefix, noarg='help', cleanup_tests=None, testclass='',
              logfile=''):
    if len(sys.argv) == 1 and sys.argv[0] == '':
        return
    sname = sys.argv[0]
    pname = re.sub('.py$', '', sname)
    if sname.endswith('.py') and not os.path.exists(pname):
        print("creating symlink: %s -> %s" % (pname, sname))
        os.symlink(sname, pname)
    elif sys._getframe(1).f_code.co_name in ['?', '<module>']:
        if sname.endswith('.py'):
            keep = testhelp.main(sys.argv, testclass, logfile=logfile)
            if not keep and None != cleanup_tests:
                cleanup_tests()
        else:
            tf_main(sys.argv, prefix=prefix, noarg=noarg)


# ---------------------------------------------------------------------------
def tf_shell(prefix, args):
    prompt = "%s> " % prefix
    req = raw_input(prompt)
    while req != 'quit':
        r = shlex.split(req)
        tf_dispatch(prefix, r)

        req = raw_input(prompt)


# ---------------------------------------------------------------------------
def ez_launch(main=None, cleanup=None, test=None):
    # pdb.set_trace()
    if len(sys.argv) == 1 and sys.argv[0] == '':
        return
    sname = sys.argv[0]
    pname = re.sub('.py$', '', sname)
    if (sname.endswith('.py') and
            not os.path.exists(pname) and '-L' in sys.argv):
        print("creating symlink: %s -> %s" % (pname, sname))
        os.symlink(sname, pname)
    elif sys._getframe(1).f_code.co_name in ['?', '<module>']:
        if sname.endswith('.py'):
            if '-d' in sys.argv:
                sys.argv.remove('-d')
                # pdb.set_trace()
            if test is None:
                unittest.main()
            else:
                if not testhelp.main(sys.argv) and cleanup is not None:
                    cleanup()
        elif main is None:
            raise StandardError("Pass your main routine to ez_launch")
        else:
            main(sys.argv)

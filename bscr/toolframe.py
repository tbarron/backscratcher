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
import inspect
import os
import pdb
import re
import shlex
import sys
import traceback as tb
import unittest

import testhelp


# ---------------------------------------------------------------------------
def tf_main(args, prefix=None, noarg='help'):
    """
    Command line entry point
    """
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
    """
    Dispatch a subfunction call
    """
    if args[0] == 'help':
        tf_help(args[1:], prefix=prefix)
    else:
        try:
            funcname = '{0}_{1}'.format(prefix, args[0])
            module = sys.modules['__main__']
            try:
                func = getattr(module, funcname)
            except AttributeError:
                sys.exit("unrecognized subfunction: {0}".format(funcname))
            func(args[1:])
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
        except SystemExit as err:
            tb.print_exc()
            print(err)


# ---------------------------------------------------------------------------
def tf_dispatch_epilog(prefix, args):
    """
    What to do after each dispatched function returns
    """
    # eval("sys.modules['__main__'].%s_epilog(args)" % prefix)
    func = None
    epiname = '{0}_epilog'.format(prefix)
    try:
        func = getattr(sys.modules['__main__'], epiname)
    except AttributeError:
        # if epilog doesn't exist, don't whine
        pass
    if func:
        func(args)


# ---------------------------------------------------------------------------
def tf_dispatch_prolog(prefix, args):
    """
    What to do before calling each dispatched function
    """
    rval = args
    func = None
    plname = '{0}_prolog'.format(prefix)
    try:
        func = getattr(sys.modules['__main__'], plname)
    except AttributeError:
        # if prolog does not exist, just carry on without whining
        pass
    if func:
        rval = func(args)
    return rval


# ---------------------------------------------------------------------------
def tf_help(argl, prefix=None):
    """help - show this list

    usage: <program> help [function-name]

    If a function name is given, show the functions __doc__ member.
    Otherwise, show a list of functions based on the first line of
    each __doc__ member.
    """
    if prefix is None:
        prefix = sys.modules['__main__'].prefix()
    if 0 < len(argl):
        head = argl.pop(0)
        if head == 'help':
            text = tf_help.__doc__
            print text
        else:
            try:
                func = getattr(sys.modules['__main__'],
                               '{0}_{1}'.format(prefix, head))
                text = func()
                print text
            except AttributeError:
                pass
        return

    mattrl = dict(inspect.getmembers(sys.modules['__main__'],
                                     inspect.isfunction))
    mattrl['tf_help'] = tf_help
    for name in mattrl:
        if name.startswith(prefix + '_'):
            dstr = mattrl[name].__doc__
            fname = name.replace(prefix + '_', '')
            if dstr:
                summary = dstr.split('\n')[0]
            else:
                summary = '{0} - no docstring provided'.format(fname)
            print "   %s" % (summary)
        elif name == 'tf_help':
            fname = 'help'
            summary = tf_help.__doc__.split('\n')[0]
            print "   %s" % (summary)


# -----------------------------------------------------------------------------
def tf_launch(prefix, noarg='help', cleanup_tests=None, testclass='',
              logfile=''):
    """
    Launch a toolframe'd program
    """
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
            if not keep and cleanup_tests is not None:
                cleanup_tests()
        else:
            tf_main(sys.argv, prefix=prefix, noarg=noarg)


# ---------------------------------------------------------------------------
def tf_shell(prefix, args):
    """
    Provide a shell in which subfunctions can be run
    """
    prompt = "%s> " % prefix
    req = raw_input(prompt)
    while req != 'quit':
        result = shlex.split(req)
        tf_dispatch(prefix, result)

        req = raw_input(prompt)


# ---------------------------------------------------------------------------
def ez_launch(modname,
              main=None,
              setup=None,
              cleanup=None,
              test=None,
              logfile=''):
    """
    For a simple (non-tool-style) program, figure out what needs to happen and
    call the invoker's 'main' callback.
    """
    if len(sys.argv) == 1 and sys.argv[0] == '':
        return
    if modname != '__main__':
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
                pdb.set_trace()
            if test is None:
                unittest.main()
            else:
                if setup is not None:
                    setup()
                keep = testhelp.main(sys.argv, test, logfile=logfile)
                if not keep and cleanup is not None:
                    cleanup()
        elif main is not None:
            main(sys.argv)

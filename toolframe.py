#!/usr/bin/python
"""
toolframe - creating a script with commandline-callable subfunctions

To use this, a script must

    * provide a prefix() routine that returns the prefix that will
      indicate and callable subfunction

    * provide a collection of callable subfunctions with names like
      '%s_callme' % prefix()

    * call toolframe.tf_launch() (no args) outside any function

History
   2011.0209   inception
"""
import os
import pdb
import re
import sys
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
def tf_launch(prefix):
    sname = sys.argv[0]
    pname = re.sub('.py$', '', sname)
    if sname.endswith('.py') and not os.path.exists(pname):
        print("creating symlink: %s -> %s" % (pname, sname))
        os.symlink(sname, pname)
    elif sys._getframe(1).f_code.co_name == '?':
        if sname.endswith('.py'):
            unittest.main()
        else:
            tf_main(sys.argv, prefix=prefix)

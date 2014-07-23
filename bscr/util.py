#!/usr/bin/env python
import glob
import os
import pdb
import pexpect
import re
import sys
import testhelp
import time
import unittest


# -----------------------------------------------------------------------------
class Chdir(object):
    """
    This class allows for doing the following:

        with Chdir('/some/other/directory'):
            assert(in '/some/other/directory')
            do_stuff()
        assert(back at our starting point)

    No matter what happens in do_stuff(), we're guaranteed that at the assert,
    we'll be back in the directory we started from.
    """
    # ------------------------------------------------------------------------
    def __init__(self, target):
        """
        This is called at instantiattion. Here we just initialize.
        """
        self.start = os.getcwd()
        self.target = target

    # ------------------------------------------------------------------------
    def __enter__(self):
        """
        This is called as control enters the with block. We jump to the target
        directory.
        """
        os.chdir(self.target)
        return self.target

    # ------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        """
        This is called as control leaves the with block. We jump back to our
        starting directory.
        """
        os.chdir(self.start)


# ---------------------------------------------------------------------------
def abspath(rpath, start=None):
    """
    Convenience wrapper for os.path.abspath(), plus the ability to compute the
    absolute path from a starting path other than cwd.
    """
    if start is None:
        path = os.path.abspath(rpath)
    elif not os.path.isabs(rpath):
        if isinstance(rpath, unicode):
            start = unicode(start)
        path = os.path.join(start, rpath)

    return os.path.normpath(path)


# ---------------------------------------------------------------------------
def basename(rpath):
    """
    Convenience wrapper for os.path.basename()
    """
    return os.path.basename(rpath)


# ---------------------------------------------------------------------------
def contents(filename):
    '''
    Contents of filename in a list, one line per element. If filename does
    not exist or is not readable, an IOError is thrown.
    '''
    f = open(filename, 'r')
    rval = [l.rstrip() for l in f.readlines()]
    f.close()
    return rval


# ---------------------------------------------------------------------------
def dirname(rpath):
    """
    Convenience wrapper for os.path.dirname()
    """
    return os.path.dirname(rpath)


# -----------------------------------------------------------------------------
def dispatch(mname, prefix, args):
    # pdb.set_trace()
    called_as = args[0]
    try:
        func_name = args[1]
    except IndexError:
        dispatch_help(mname, prefix, args)
        return

    if func_name == 'help':
        dispatch_help(mname, prefix, args)
        return

    try:
        func = getattr(sys.modules[mname], "_".join([prefix, func_name]))
        func(args[2:])
    except AttributeError:
        fatal("Subcommand '%s' not found" % func_name)

# -----------------------------------------------------------------------------
def dispatch_help(mname, prefix, args):
    mod = sys.modules[mname]
    if 3 <= len(args) and args[1] == 'help' and args[2] == "help":
        print("\n".join(["help - show a list of available commands",
                         "",
                         "   With no arguments, show a list of commands",
                         "   With a command as argument, show help for " +
                         "that command",
                         ""
                         ]))
    elif 3 <= len(args) and args[1] == 'help':
        fname = "_".join([prefix, args[2]])
        func = getattr(mod, fname)
        print func.__doc__
    elif len(args) < 2 or args[1] == 'help':
        fnlist = [x for x in dir(mod) if x.startswith(prefix)]
        clist = [getattr(mod, x) for x in fnlist]
        dlist = [x.__doc__.split("\n")[0] for x in clist]
        dlist.append("help - show this list")
        dlist.sort()
        for line in dlist:
            print("   %s" % line)


# ---------------------------------------------------------------------------
def expand(path):
    """
    Return a pathname with any "~" or env variables expanded.
    """
    return os.path.expanduser(os.path.expandvars(path))


# ---------------------------------------------------------------------------
def fatal(msg):
    """
    Print an error message and exit.
    """
    print ' '
    print '   %s' % msg
    print ' '
    sys.exit(1)


# ---------------------------------------------------------------------------
def function_name():
    """
    Return the name of the caller.
    """
    return sys._getframe(1).f_code.co_name


# -----------------------------------------------------------------------------
def git_root(path=None):
    if path is None:
        path = os.getcwd()
    dotgit = os.path.join(path, ".git")
    while not os.path.isdir(dotgit) and path != "/":
        path = os.path.dirname(path)

    if os.path.isdir(dotgit):
        rval = path
    else:
        rval = None

    return rval


# -----------------------------------------------------------------------------
def in_bscr_repo():
    try:
        c = contents("./.git/description")
    except IOError:
        return False

    if "backscratcher" not in "".join(c):
        return False

    return True


# -----------------------------------------------------------------------------
def bscr_root(filename=None):
    """
    Compute the install root for an imported module.
    TODO: This should probably move to testhelp at some point
    """
    if filename is None:
        filename = __file__
    return(dirname(abspath(filename)))


# -----------------------------------------------------------------------------
def bscr_test_root(filename):
    """
    Compute the install root for a test module.
    TODO: This should probably move to testhelp at some point
    """
    home = dirname(abspath(filename))
    if basename(home) != 'test':
        raise StandardError("'%s' should be 'test'" % basename(home))
    rval = dirname(home)
    if basename(rval) != 'bscr':
        rval = pj(rval, 'bscr')
    return rval


# -----------------------------------------------------------------------------
def pj(*args):
    """
    pathjoin -- convenience wrapper for os.path.join()
    """
    return os.path.join(*args)


# ---------------------------------------------------------------------------
def rmrf(path):
    '''
    Remove the tree rooted at path.
    '''
    if os.path.isdir(path):
        for d in os.listdir(path):
            # print("rmrf directory %s/%s" % (path, d))
            rmrf('%s/%s' % (path, d))
        # print("os.rmdir(%s)" % path)
        os.rmdir(path)
    else:
        # print("os.unlink(%s)" % path)
        os.unlink(path)


# ---------------------------------------------------------------------------
def run(cmd, xable, verbose=False):
    # print "run: cmd='%s', %s" % (cmd, xable)
    if xable:
        if verbose:
            print cmd
        os.system(cmd)
    else:
        print "would do '%s'" % cmd


# ---------------------------------------------------------------------------
def safe_unlink(path):
    if type(path) == str:
        if os.path.exists(path):
            os.unlink(path)
    elif type(path) == list:
        for item in path:
            if os.path.exists(item):
                os.unlink(item)
    else:
        raise Exception('safe_unlink: argument must be str or list')


# -----------------------------------------------------------------------------
def pythonpath_bscrroot():
    """
    Find the git root and add it to $PYTHONPATH
    TODO: This should probably move to testhelp eventually.
    """
    where = dirname(dirname(abspath(__file__)))
    prev = os.getenv("PYTHONPATH")
    if prev is None:
        os.environ["PYTHONPATH"] = where
    elif where not in prev:
        os.environ["PYTHONPATH"] = ":".join([where, prev])


# -----------------------------------------------------------------------------
def script_location(script):
    """
    Compute where we expect to find the named script.
    TODO: This should probably move to testhelp eventually.
    """
    rval = pexpect.which(script)
    if rval is None:
        groot = os.getcwd()
        while not os.path.exists(os.path.join(groot, ".git")) and groot != "/":
            groot = os.path.dirname(groot)
        if groot != "/":
            rval = os.path.join(groot, "bin", script)
            if groot not in sys.path:
                sys.path.append(groot)
        else:
            raise StandardError("Can't find script %s" % script)
    return rval


# -----------------------------------------------------------------------------
def touch(touchables, times=None):
    """
    touch -- ensure file exists and update its *times* (atime, mtime)
    """
    if times is None:
        now = int(time.time())
        times = (now, now)
    if type(touchables) == list:
        for f in touchables:
            open(f, 'a').close()
            os.utime(f, times)
    elif type(touchables) == str:
        open(touchables, 'a').close()
        os.utime(touchables, times)
    else:
        raise StandardError('argument must be list or string')


# ---------------------------------------------------------------------------
def writefile(filepath, lines):
    f = open(filepath, 'w')
    f.writelines(lines)
    f.close()


# ---------------------------------------------------------------------------
def lquote(text):
    return '\n'.join(['"""', text.rstrip(), '"""'])


# ---------------------------------------------------------------------------
def findroot():
    afile = os.path.abspath(__file__)
    bscr = os.path.dirname(afile)
    return bscr

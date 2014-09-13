#!/usr/bin/env python
import pdb
import fcntl
import glob
import os
import pexpect
import re
import shlex
import struct
import subprocess as subp
import sys
import termios
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
def terminal_size():
    """
    Best effort to determine and return the width and height of the terminal
    """
    if not sys.stdout.isatty():
        return -1, -1
    # import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
                                 fcntl.ioctl(sys.stdout.fileno(),
                                             termios.TIOCGWINSZ,
                                             struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h


# ---------------------------------------------------------------------------
def contents(filename, string=False):
    '''
    Contents of filename in a list, one line per element. If filename does
    not exist or is not readable, an IOError is thrown.
    '''
    with open(filename, 'r') as f:
        if string:
            rval = "".join(f.readlines())
        else:
            rval = [l.rstrip() for l in f.readlines()]
    return rval


# ---------------------------------------------------------------------------
def dirname(rpath):
    """
    Convenience wrapper for os.path.dirname()
    """
    return os.path.dirname(rpath)


# -----------------------------------------------------------------------------
def dispatch(mname, prefix, args):
    """
    Call a subfunction from module *mname* based on *prefix* and *args*
    """
    # pdb.set_trace()
    called_as = args[0]
    try:
        func_name = args[1]
    except IndexError:
        dispatch_help(mname, prefix, args)
        return

    if func_name in ['help', '-h', '--help']:
        dispatch_help(mname, prefix, args)
        return

    try:
        func = getattr(sys.modules[mname], "_".join([prefix, func_name]))
        func(args[2:])
    except AttributeError:
        fatal("Subcommand '%s' not found" % func_name)


# -----------------------------------------------------------------------------
def dispatch_help(mname, prefix, args):
    """
    Standard help function for dispatch-based tool programs
    """
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
    elif len(args) < 2 or args[1] in ['help', '-h', '--help']:
        fnlist = [x for x in dir(mod) if x.startswith(prefix)]
        clist = [getattr(mod, x) for x in fnlist]
        try:
            dlist = [x.__doc__.split("\n")[0] for x in clist]
        except AttributeError:
            fatal("Function %s.%s() needs a __doc__ string" % (mname,
                                                               x.func_name))
        dlist.append("help - show this list")
        dlist.sort()
        for line in dlist:
            print("   %s" % line)


# ---------------------------------------------------------------------------
def exists(path):
    """
    Shortcut wrapper for os.path.exists()
    """
    return os.path.exists(path)


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
def git_describe():
    """
    Last resort retrieval of the current version
    """
    result = pexpect.run("git describe")
    return result.strip()


# -----------------------------------------------------------------------------
def git_root(path=None):
    """
    If we're in a git repository, return its root. Otherwise return None.
    """
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
def in_bscr_repo(path=None):
    """
    We are in a backscratcher repo -- true or false?
    """
    if path is None:
        here = os.getcwd()
    else:
        here = path

    while not exists(pj(here, ".git")) and here != "/":
        here = dirname(here)

    if exists(pj(here, ".git")):
        try:
            c = contents(pj(here, ".git", "description"))
        except IOError:
            return False
        if "backscratcher" not in "".join(c):
            return False
    else:
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
def pj(*args):
    """
    pathjoin -- convenience wrapper for os.path.join()
    """
    return os.path.join(*args)


# ---------------------------------------------------------------------------
def run(cmd, xable, verbose=False):
    """
    Run *cmd* if *xable*, otherwise just report what would happen
    """
    # print "run: cmd='%s', %s" % (cmd, xable)
    if xable:
        if verbose:
            print cmd
        p = subp.Popen(shlex.split(cmd))
        p.wait()
        # os.system(cmd)
    else:
        print "would do '%s'" % cmd


# ---------------------------------------------------------------------------
def safe_unlink(path):
    """
    As long as *path* is a string or a list, this will not throw an exception.
    Unlink all the file(s) named if they exist.
    """

    if type(path) == str:
        if os.path.exists(path):
            os.unlink(path)
    elif type(path) == list:
        for item in path:
            if os.path.exists(item):
                os.unlink(item)
    else:
        raise bscr.Error('safe_unlink: argument must be str or list')


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
            raise bscr.Error("Can't find script %s" % script)
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
        raise bscr.Error('argument must be list or string')


# ---------------------------------------------------------------------------
def writefile(filepath, lines, newlines=False):
    """
    Write the contents of *lines* to *filepath*
    """
    f = open(filepath, 'w')
    if newlines:
        if type(lines) == str:
            f.writelines(lines + '\n')
        elif type(lines) == list:
            f.writelines([z.rstrip() + '\n' for z in lines])
        else:
            f.writelines(str(lines))
    else:
        f.writelines(lines)
    f.close()


# ---------------------------------------------------------------------------
def package_module(module_name):
    """
    Return the parent package module for the named module
    """
#     print module_name
#     print sys.modules[module_name]
#     print sys.modules[module_name].__package__
#     print sys.modules[sys.modules[module_name].__package__]
    rval = sys.modules[sys.modules[module_name].__package__]
    return rval


# ---------------------------------------------------------------------------
def lquote(text):
    """
    Return *text* wrapped in triple-quotes
    """
    return '\n'.join(['"""', text.rstrip(), '"""'])


# ---------------------------------------------------------------------------
def findroot():
    """
    Best effort to find the install root of this file
    """
    afile = os.path.abspath(__file__)
    bscr = os.path.dirname(afile)
    return bscr


bscr = package_module(__name__)

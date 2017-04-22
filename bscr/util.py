#!/usr/bin/env python
"""
Utility stuff
"""
import contextlib
import fcntl
import inspect
import optparse
import os
import pdb
import random
import shlex
import string
import struct
import subprocess as subp
import sys
import termios
import time

import pexpect


# -----------------------------------------------------------------------------
@contextlib.contextmanager
def Chdir(path):
    """
    This class allows for doing the following:

        with Chdir('/some/other/directory'):
            assert(in '/some/other/directory')
            do_stuff()
        assert(back at our starting point)

    No matter what happens in do_stuff(), we're guaranteed that at the assert,
    we'll be back in the directory we started from.
    """
    origin = os.getcwd()
    try:
        os.chdir(path)
        yield path
    finally:
        os.chdir(origin)


# -----------------------------------------------------------------------------
class cmdline(object):
    """
    Handle command line parsing
    """
    arg_default = {
        'store_true': lambda: False,
        'store_false': lambda: True,
        'append': lambda: list()
        }

    def __init__(self,
                 optdef,
                 default_action='store',
                 default_type='string',
                 usage=None):
        """
        The constructor expects a dictionary in *optdef* defining the arguments
        to be parsed from the command line.
        """
        debug_absent = True
        self.p = optparse.OptionParser(usage=usage)
        for arg in optdef:
            if 'name' in arg and 'opts' not in arg:
                name = arg['name']
                arg['opts'] = ['-' + name[0], '--' + name]
            elif 'opts' in arg and 'name' not in arg:
                arg['name'] = self.pick_name(arg['opts'])

            if 'action' not in arg:
                arg['action'] = default_action

            if 'default' not in arg:
                func = self.arg_default.get(arg['action'], lambda: None)
                arg['default'] = func()

            if 'type' not in arg:
                if arg['action'] == 'store':
                    arg['type'] = default_type

            if 'dest' not in arg:
                arg['dest'] = name

            if '--debug' in arg['opts']:
                debug_absent = False

            kw = dict((k, arg[k]) for k in arg if k != 'opts' and k != 'name')
            self.p.add_option(*arg['opts'], **kw)

        if debug_absent:
            self.p.add_option('-d', '--debug',
                              action='store_true',
                              default=False,
                              dest='debug',
                              help='run under the debugger')

    # -----------------------------------------------------------------------
    def parse(self, arglist):
        """
        Parse the command line based on the dictionary passed in to the
        constructor
        """
        (o, a) = self.p.parse_args(arglist)

        if o.debug:
            pdb.set_trace()

        return(o, a)

    # -----------------------------------------------------------------------
    def pick_name(self, opt_l):
        """
        Choose a reasonable name from the list of option expressions. Use the
        long option if it's present. If not, use the short option. If we don't
        find either one, generate a short random name and return that.
        """
        rval = ''
        for o in opt_l:
            if o.startswith('--'):
                rval = o.replace('--', '')
                break
            elif o.startswith('-') and rval == '':
                rval = o.replace('-', '')
        if rval == '':
            rval = random_word(4)
        return rval


# ---------------------------------------------------------------------------
def abspath(rpath, start=None):
    """
    Convenience wrapper for os.path.abspath(), plus the ability to compute the
    absolute path from a starting path other than cwd.
    !@!: needs test
    """
    if start is None:
        path = os.path.abspath(rpath)
        rval = os.path.normpath(path)
    elif not os.path.isabs(rpath):
        if isinstance(rpath, unicode):
            ustart = unicode(start)
            upath = os.path.join(ustart, rpath)
            rval = os.path.normpath(upath)
        else:
            path = os.path.join(start, rpath)
            rval = os.path.normpath(path)
    return rval


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
    !@! test?
    """
    if not sys.stdout.isatty():
        return -1, -1
    # import fcntl, termios, struct
    tiocwinsz = fcntl.ioctl(sys.stdout.fileno(),
                            termios.TIOCGWINSZ,
                            struct.pack('HHHH', 0, 0, 0, 0))
    (height, width, _, _) = struct.unpack('HHHH', tiocwinsz)
    return width, height


# ---------------------------------------------------------------------------
def contents(filename, string=False):
    """
    Contents of filename in a list, one line per element. If filename does
    not exist or is not readable, an IOError is thrown.
    """
    with open(filename, 'r') as rbl:
        if string:
            rval = "".join(rbl.readlines())
        else:
            rval = [_.rstrip() for _ in rbl.readlines()]
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
    !@! test?
    """
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
    !@! test?
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
def epoch(ymd):
    """
    Convert a YYYY.mmdd date into an epoch (seconds since 1970.0101)
    !@! test?
    """
    tms = time.strptime(ymd, "%Y.%m%d")
    return time.mktime(tms)


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
    !@! test?
    """
    print ' '
    print '   %s' % msg
    print ' '
    sys.exit(1)


# ---------------------------------------------------------------------------
def function_name(level=1):
    """
    Return the name of the caller.
    !@! test?
    """
    stk = inspect.stack()
    rval = stk[level][3]
    return rval
    # return sys._getframe(1).f_code.co_name


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
    !@! test?
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
    !@! test?
    """
    if path is None:
        here = os.getcwd()
    else:
        here = path

    while not exists(pj(here, ".git")) and here != "/":
        here = dirname(here)

    if exists(pj(here, ".git")):
        try:
            content = contents(pj(here, ".git", "description"))
        except IOError:
            return False
        if "backscratcher" not in "".join(content):
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
    !@! test?
    """
    if xable:
        if verbose:
            print cmd
        pipe = subp.Popen(shlex.split(cmd))
        pipe.wait()
    else:
        print "would do '%s'" % cmd


# ---------------------------------------------------------------------------
def safe_unlink(path):
    """
    As long as *path* is a string or a list, this will not throw an exception.
    Unlink all the file(s) named if they exist.
    !@! test?
    """

    if isinstance(path, str):
        if os.path.exists(path):
            os.unlink(path)
    elif isinstance(path, list):
        for item in path:
            if os.path.exists(item):
                os.unlink(item)
    else:
        raise BSCR.Error('safe_unlink: argument must be str or list')


# -----------------------------------------------------------------------------
def mtime(pathname):
    """
    Return the mtime of pathname
    !@! deprecate -- use os.path.getmtime or py.path.local
    """
    sinfo = os.stat(pathname)
    return sinfo.st_mtime


# -----------------------------------------------------------------------------
def normalize_path(path):
    """
    Fully normalize a path -- apply python's abspath and normpath, but then
    also resolve any symlink components and return the result.
    """
    apath = os.path.abspath(path)
    comps = apath.split(os.sep)
    ppath = ''
    for comp in comps:
        if comp == '':
            continue
        ppath += os.sep + comp
        if os.path.islink(ppath):
            ppath = os.readlink(ppath)
    rval = os.path.normpath(ppath)
    return rval


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
            raise BSCR.Error("Can't find script %s" % script)
    return rval


# -----------------------------------------------------------------------------
def touch(touchables, times=None):
    """
    touch -- ensure file exists and update its *times* (atime, mtime)
    """
    if times is None:
        now = int(time.time())
        times = (now, now)
    if isinstance(touchables, list):
        for fname in touchables:
            open(fname, 'a').close()
            os.utime(fname, times)
    elif isinstance(touchables, str):
        open(touchables, 'a').close()
        os.utime(touchables, times)
    else:
        raise BSCR.Error('argument must be list or string')


# ---------------------------------------------------------------------------
def writefile(filepath, lines, newlines=False):
    """
    Write the contents of *lines* to *filepath*
    """
    wbl = open(filepath, 'w')
    if newlines:
        if isinstance(lines, str):
            wbl.writelines(lines + '\n')
        elif isinstance(lines, list):
            wbl.writelines([z.rstrip() + '\n' for z in lines])
        else:
            wbl.writelines(str(lines))
    else:
        wbl.writelines(lines)
    wbl.close()


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
    rval = os.path.dirname(afile)
    return rval


# ---------------------------------------------------------------------------
def random_word(length):
    """
    Make up a random name of length *length*
    """
    rval = ''.join([random.choice(string.lowercase) for _ in range(length)])
    return rval


BSCR = package_module(__name__)

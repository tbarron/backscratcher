#!/usr/bin/env python
import os
import pdb
import re
import sys
import testhelp
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
def abspath(rpath):
    """
    Convenience wrapper for os.path.abspath()
    """
    return os.path.abspath(rpath)


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
    rval = f.readlines()
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
    else:
        func = getattr(sys.modules[mname], "_".join([prefix,func_name]))
        func(args)

# ---------------------------------------------------------------------------
def dispatch_help(mname, prefix, args):
    mod = sys.modules[mname]
    if 3 <= len(args) and args[1] == 'help' and args[2] == "help":
        print("\n".join(["help - show a list of available commands",
                         "",
                         "   With no arguments, show a list of commands",
                         "   With a command as argument, show help for that command",
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
    return os.path.expandvars(os.path.expanduser(path))


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
def in_bscr_repo():
    try:
        c = contents("./.git/description")
    except IOError:
        return False

    if "backscratcher" not in "".join(c):
        return False

    return True


# -----------------------------------------------------------------------------
def bscr_root(filename):
    """
    Compute the install root for an imported module.
    TODO: This should probably move to testhelp at some point
    """
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
def script_location(script):
    """
    Compute where we expect to find the named script.
    TODO: This should probably move to testhelp eventually.
    """
    if in_bscr_repo():
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rval = "%s/bin/%s" % (root, script)
    else:
        site = os.path.dirname(os.path.dirname(__file__))
        fl = glob.glob("%s/backscratcher*egg-info")
        egg = fl[0]
        el = glob.glob("%s/installed-files.txt" % egg)
        z = contents(el[0])
        for fn in z:
            if fn.strip().endswith(script):
                rpath = fn.strip()
                break
        rval = os.path.abspath(os.path.join(egg, rpath))
    return rval

# -----------------------------------------------------------------------------
def touch(filepath, times=None):
    """
    touch -- ensure file exists and update its *times* (atime, mtime)
    """
    open(filepath, 'a').close()
    os.utime(filepath, times)

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
    
# ---------------------------------------------------------------------------
def tpb_cleanup_tests():
    global testdir
    if os.path.basename(os.getcwd()) == testdir:
        os.chdir('..')
    if os.path.isdir(testdir):
        rmrf(testdir)


# ---------------------------------------------------------------------------
class TpbtoolsTest(unittest.TestCase):
    # -----------------------------------------------------------------------
    def setUp(self):
        global testdir
        testdir = testhelp.into_test_dir()

    # -----------------------------------------------------------------------
    def test_expand(self):
        home = os.environ['HOME']
        logname = os.environ['LOGNAME']

        assert(expand('$HOME') == home)
        assert(expand('~') == home)
        assert(expand('~%s' % logname) == home)
        assert(expand('### $PYTHONPATH ###')
               == '### %s ###' % os.environ['PYTHONPATH'])


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    if not testhelp.main(sys.argv):
        tpb_cleanup_tests()

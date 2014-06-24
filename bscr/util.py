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
def contents(filename):
    '''
    Contents of filename in a list, one line per element. If filename does
    not exist or is not readable, an IOError is thrown.
    '''
    f = open(filename, 'r')
    rval = f.readlines()
    f.close()
    return rval


# -----------------------------------------------------------------------------
def dispatch(args, prefix, mname):
    called_as = args.pop(0)
    try:
        func_name = args.pop(0)
    except IndexError:
        func_name = 'help'
    func = getattr(sys.modules[mname], "_".join([prefix,func_name]))
    return func(args)

# ---------------------------------------------------------------------------
def expand(path):
    return os.path.expandvars(os.path.expanduser(path))


# ---------------------------------------------------------------------------
def fatal(msg):
    print ' '
    print '   %s' % msg
    print ' '
    sys.exit(1)


# ---------------------------------------------------------------------------
def function_name():
    return sys._getframe(1).f_code.co_name


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
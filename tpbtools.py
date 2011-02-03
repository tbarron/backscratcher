#!/usr/bin/env python

import os
import re
import sys
import testhelp
import unittest

# ---------------------------------------------------------------------------
# def ahash(arglist):
#     mylist = []
#     mylist.extend(arglist)
    
#     rval = {}
#     for i in range(0,len(mylist)):
#         item = mylist[i]
#         if re.search(r'^!', item):
#             pass
#         elif re.search(r'^-', item):
#             k = item.strip('-')
#             if i < len(mylist)-1:
#                 v = mylist[i+1]
#                 if not re.search(r'^-', v):
#                     mylist[i+1] = '!' + mylist[i+1]
#                     rval[k] = v
#                 else:
#                     rval[k] = True
#             else:
#                 rval[k] = True
#         else:
#             try:
#                 rval['noname'].append(item)
#             except KeyError:
#                 rval['noname'] = [item]

#     return rval

# # ---------------------------------------------------------------------------
# def Avalue(hash, key, default=None, error=None):
#     try:
#         rval = hash[key]
#     except KeyError:
#         if default != None:
#             rval = default
#         elif error != None:
#             fatal(error)
#         else:
#             raise 'No value for -%s' % key
#     return rval

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

# # ---------------------------------------------------------------------------
# def parse_args(arglist):
#     """
#     Parse the arguments into a hash (er, dictionary).

#     The hash is returned.
#     """
#     # load up the return hash with the defaults
#     rval = { 'aix_host' : "larry",
#              'linux_host' : "sam",
#              'user' : "tbarron",
#              'port' : "20716",
#              'gw' : "clkprox.clearlake.ibm.com",
#              'parse' : None,
#              'fetch' : None }

#     # update arguments provided by the user from the command line
#     for adx in range(len(arglist)):
#         arg = re.sub("^--?", "", arglist[adx])
#         if arg in rval:
#             if (len(arglist) <= adx+1):
#                 rval[arg] = 1
#             elif (arglist[adx+1][0:2] == "--"):
#                 rval[arg] = 1
#             else:
#                 rval[arg] = arglist[adx + 1]
                
#     # return the updated hash
#     return rval

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
        
# ---------------------------------------------------------------------------
def writefile(filepath, lines):
    f = open(filepath, 'w')
    f.writelines(lines)
    f.close()
    
# ---------------------------------------------------------------------------
def tpb_cleanup_tests():
    if os.path.basename(os.getcwd()) == 'tpbtools_test':
        os.chdir('..')
    if os.path.isdir('tpbtools_test'):
        rmrf('tpbtools_test')
        
# ---------------------------------------------------------------------------
def prepare_tests():
    global intestdir
    testdir = 'tpbtools_test'
    try:
        if intestdir:
            return
    except NameError:
        intestdir = False

    if os.path.basename(os.getcwd()) == testdir:
        intestdir = True
        return

    if not os.path.exists(testdir):
        os.mkdir(testdir)

    os.chdir(testdir)
    intestdir = True
    
# ---------------------------------------------------------------------------
class TpbtoolsTest(unittest.TestCase):
    # -----------------------------------------------------------------------
    def setUp(self):
        global intestdir
        testdir = 'tpbtools_test'
        try:
            if intestdir:
                return
        except NameError:
            intestdir = False

        if os.path.basename(os.getcwd()) == testdir:
            intestdir = True
            return

        if not os.path.exists(testdir):
            os.mkdir(testdir)

        os.chdir(testdir)
        intestdir = True
        
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

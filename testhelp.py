#!/usr/bin/python

import os
import pdb
import pexpect
import sys
import unittest
import StringIO

from optparse import *

def main(args=None, filter=None):
    if args == None:
        args = sys.argv
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='debug')
    p.add_option('-k', '--keep',
                 action='store_true', default=False, dest='keep',
                 help='keep test files')
    p.add_option('-l', '--list',
                 action='store_true', default=False, dest='list',
                 help='list tests')
    p.add_option('-q', '--quiet',
                 action='store_true', default=False, dest='quiet',
                 help='quieter')
    p.add_option('-t', '--to',
                 action='store', default='', dest='final',
                 help='run all tests up to this one')
    p.add_option('-v', '--verbose',
                 action='store_true', default=False, dest='verbose',
                 help='louder')
    (o, a) = p.parse_args(args)

    debug_flag(o.debug)
    
    if o.verbose:
        volume = 2
    elif o.quiet:
        volume = 0
    else:
        volume = 1

    # print sys.modules.keys()
    # print sys.modules['__main__']

    testlist = all_tests('__main__', filter)
    if o.list:
        list_tests(a, o.final, testlist)
        o.keep = True
    else:
        run_tests(a, o.final, testlist, volume)

    return o.keep

# ---------------------------------------------------------------------------
def all_tests(name, filter=None):
    '''
    Return a list of tests in the module <name>.
    Limit the list to those which contain the string <filter>.
    '''
    # print("all_tests(%s, %s)" % (name, filter))
    testclasses = []
    cases = []
    if filter == None:
        filter = 'Test'
    # print("all_tests(%s, %s)" % (name, filter))
    # print dir(sys.modules[name])
    for item in dir(sys.modules[name]):
        if filter in item:
            testclasses.append(item)
    for c in testclasses:
        cobj = getattr(sys.modules[name], c)
        for case in unittest.TestLoader().getTestCaseNames(cobj):
            cases.append('%s.%s' % (c, case))
    return cases

# ---------------------------------------------------------------------------
def debug_flag(value=None):
    global dval

    if value != None:
        dval = value
        
    try:
        rval = dval
    except NameError:
        dval = False
        rval = dval

    return rval

# ---------------------------------------------------------------------------
def expectVSgot(expected, got):
    try:
        assert(expected == got)
    except AssertionError, e:
        if type(expected) == list:
            if 5 < len(expected):
                for i in range(0, len(expected)):
                    try:
                        if expected[i] != got[i]:
                            print "EXPECTED: '%s'" % expected[i]
                            print "GOT:      '%s'" % got[i]
                    except IndexError:
                        print "EXPECTED: '%s'" % expected[i]
                        print "GOT:      None"
            else:
                print "EXPECTED '%s'" % expected
                print "GOT      '%s'" % got
            raise e
        elif type(expected) == str:
            print "EXPECTED: '%s'" % expected
            print "GOT:      '%s'" % got
            raise e
        
# ---------------------------------------------------------------------------
def into_test_dir():
    tdname = '_test.%d' % os.getpid()
    bname = os.path.basename(os.getcwd())
    if bname != tdname:
        os.mkdir(tdname)
        os.chdir(tdname)
    return tdname

# ---------------------------------------------------------------------------
def list_tests(a, final, testlist):
    if len(a) <= 1:
        for c in testlist:
            print c
            if final != '' and final in c:
                break
    else:
        for arg in a[1:]:
            for c in testlist:
                if arg in c:
                    print c
                if final != '' and final in c:
                    break

# ---------------------------------------------------------------------------
def run_tests(a, final, testlist, volume):
    mainmod = sys.modules['__main__']
    if len(a) <= 1:
        suite = unittest.TestSuite()
        for c in testlist:
            s = unittest.TestLoader().loadTestsFromName(c, mainmod)
            suite.addTest(s)
            if final != '' and final in c:
                break
    else:
        suite = unittest.TestSuite()
        for arg in a[1:]:
            for c in testlist:
                if arg in c:
                    s = unittest.TestLoader().loadTestsFromName(c, mainmod)
                    suite.addTest(s)
                if final != '' and final in c:
                    break

    unittest.TextTestRunner(verbosity=volume).run(suite)

# ---------------------------------------------------------------------------
class UnderConstructionError(Exception):
    def __init__(self, value='under construction'):
        self.value = value
    def __str__(self):
        return repr(self.value)
            
# ---------------------------------------------------------------------------
class TesthelpTest(unittest.TestCase):
    # -----------------------------------------------------------------------
    def test_all_tests(self):
        all = ['TesthelpTest.test_all_tests',
               'TesthelpTest.test_list_tests',
               'TesthelpTest.test_expected_vs_got'].sort()
        l = all_tests('__main__').sort()
        expectVSgot(all, l)
        l = all_tests('__main__', 'no such tests')
        expectVSgot([], l)
        l = all_tests('__main__', 'helpTest').sort()
        expectVSgot(all, l)

    def test_list_tests(self):
        tlist = ['one', 'two', 'three', 'four', 'five']
        self.redirected_list_test([],
                                  '',
                                  tlist,
                                  "one\ntwo\nthree\nfour\nfive\n")
        self.redirected_list_test(['', 'o'],
                                  '',
                                  tlist,
                                  "one\ntwo\nfour\n")
        self.redirected_list_test(['', 'e'],
                                  '',
                                  tlist,
                                  "one\nthree\nfive\n")

    def redirected_list_test(self, args, final, testlist, expected):
        s = StringIO.StringIO()
        save_stdout = sys.stdout
        sys.stdout = s
        list_tests(args, final, testlist)
        sys.stdout = save_stdout

        r = s.getvalue()
        s.close()
        assert(r == expected)

    def test_expected_vs_got(self):
        self.redirected_evg('', '', '')
        self.redirected_evg('one', 'two',
                            "EXPECTED: 'one'\n" +
                            "GOT:      'two'\n")

    def redirected_evg(self, exp, got, expected):
        s = StringIO.StringIO()
        save_stdout = sys.stdout
        sys.stdout = s
        try:
            expectVSgot(exp, got)
        except AssertionError:
            pass
        r = s.getvalue()
        s.close()
        sys.stdout = save_stdout

        try:
            assert(r.startswith(expected))
        except AssertionError:
            print "expected: '''\n%s'''" % expected
            print "got:      '''\n%s'''" % r
        
# ---------------------------------------------------------------------------
global d
d = dir()
if __name__ == '__main__':
    main(sys.argv)

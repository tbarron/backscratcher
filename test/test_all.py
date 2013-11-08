#!/usr/bin/env python
import os
import sys
sys.path.insert(0, os.getcwd())

import glob
import pdb
import testhelp
import toolframe


# -----------------------------------------------------------------------------
def main(args):
    launchdir = os.path.dirname(sys.argv[0])
    tlist = [os.path.basename(x.replace('.py', ''))
             for x in glob.glob(launchdir + '/test_*.py')]
    if 'test_all' in tlist:
        tlist.remove('test_all')
    testlist = []
    for mod in tlist:
        mhandle = __import__(mod)
        for item in dir(mhandle):
            if item.endswith('Test'):
                tclass = getattr(mhandle, item)
                testlist.append((mhandle, tclass))
        for testset in testlist:
            run_tests(testset)
        if hasattr(mhandle, 'tearDownModule'):
            tdf = getattr(mhandle, 'tearDownModule')
            tdf()


# -----------------------------------------------------------------------------
def run_tests(mt_tup):
    suite = testhelp.LoggingTestSuite(logfile='bstest.log')
    (m, t) = mt_tup
    print t.__module__ + '.' + t.__name__ + ':'
    cases = testhelp.unittest.TestLoader().getTestCaseNames(t)
    for c in cases:
        s = testhelp.unittest.TestLoader().loadTestsFromName(c, t)
        suite.addTests(s)

    result = testhelp.unittest.TextTestRunner().run(suite)

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    toolframe.ez_launch(main=main)

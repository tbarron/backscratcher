#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.getcwd())

import glob
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
        __import__(mod)
        for item in dir(sys.modules[mod]):
            if item.endswith('Test'):
                testlist.append(mod + '.' + item)
    print testlist
    run_tests(testlist)

    
# -----------------------------------------------------------------------------
def run_tests(tests):
    suite = testhelp.LoggingTestSuite(logfile='bstest.log')
    for t in tests:
        (module, tclass) = t.split('.')
        m = sys.modules[module]
        t = getattr(m, tclass)
        cases = testhelp.unittest.TestLoader().getTestCaseNames(t)
        for c in cases:
            s = testhelp.unittest.TestLoader().loadTestsFromName(c, t)
            suite.addTests(s)

    result = testhelp.unittest.TextTestRunner().run(suite)

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    toolframe.ez_launch(main=main)
    

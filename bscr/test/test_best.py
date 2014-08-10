import glob
from importlib import import_module
import inspect
import os
import pdb
import pexpect
import re
import sys
from nose.plugins.skip import SkipTest
from bscr import testhelp as th
import types
import unittest
from bscr import util as U

"""
This file checks for best practice compliance.
 - Does my code conform to PEP8?
 - Do I have any inadvertent duplicate routines?
 - Do I have routines with no __doc__?
"""


# -----------------------------------------------------------------------------
class Test_BEST(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_pep8(self):
        """
        Check the code in this package for PEP8 conformance.
        """
        # pdb.set_trace()
        pep8 = pexpect.which('pep8')
        if pep8 is None:
            raise SkipTest("Pep8 tool not found")
        else:
            root = U.bscr_test_root(__file__)
            for r, d, f in os.walk(root):
                pylist = [U.pj(r, x) for x in f if x.endswith(".py")]
                args = " ".join(pylist)
                if args != '':
                    cmd = "pep8 %s" % args
                    # print cmd
                    result = pexpect.run(cmd)
                    self.assertEqual('', result,
                                     "Pep8 report: %s" % result)

    # -------------------------------------------------------------------------
    def test_nodoc(self):
        bscr = sys.modules['bscr']
        result = self.nodoc_check(bscr, 0, 't')
        if result != '':
            self.fail(result)

    # -------------------------------------------------------------------------
    def nodoc_check(self, mod, depth, why):
        try:
            already = self.already
        except AttributeError:
            self.already = ['glob', 'fcntl', 're', 'pexpect', 'unittest',
                            'difflib', 'pprint', 'warnings', 'heapq', 'os',
                            'pdb', 'optparse', 'traceback', 'linecache',
                            'bdb', 'logging', 'StringIO', 'inspect', 'stat',
                            'tokenize', 'socket', 'dis', 'getopt', 'shlex',
                            'pickle', 'shutil',
                            ]
            already = self.already
        rval = ''
        for name, item in inspect.getmembers(mod,
                                             inspect.isroutine):
            if all([not inspect.isbuiltin(item),
                    name not in dir(unittest.TestCase),
                    item.__name__ not in already,
                    not name.startswith('_')]):
                already.append(":".join([mod.__name__, name]))
                if item.__doc__ is None:
                    rval += "\n%s(%s): %s" % (mod.__name__, why, name)
        for name, item in inspect.getmembers(mod,
                                             inspect.isclass):
            if all([hasattr(item, 'tearDown'),
                    item.__name__ not in already,
                    depth < 5]):
                already.append(item.__name__)
                rval += self.nodoc_check(item, depth+1, 'c')
        for name, item in inspect.getmembers(mod,
                                             inspect.ismodule):
            if all([not inspect.isbuiltin(item),
                    item.__name__ not in already,
                    not name.startswith('@'),
                    not name.startswith('_'),
                    depth < 5]):
                already.append(item.__name__)
                rval += self.nodoc_check(item, depth+1, 'm')
        return rval

    # -------------------------------------------------------------------------
    def test_duplicates(self):
        root = U.bscr_test_root(__file__)
        rpt = ''
        for r, d, f in os.walk(root):
            pylist = [U.pj(r, x) for x in f if x.endswith(".py")]
            for filename in pylist:
                z = self.duplicate_check(filename)
                if z != '':
                    rpt += z
        if rpt != '':
            self.fail(rpt)

    # -------------------------------------------------------------------------
    def duplicate_check(self, filename):
        rval = ''
        with open(filename, 'r') as f:
            d = f.readlines()
            last = ''
            for l in d:
                q = re.findall("^\s*def\s+(\w+)\s*\(", l)
                if q:
                    name = q[0]
                    if name == last:
                        rval += "%s: %s" % (filename, name)
                    last = name
        return rval

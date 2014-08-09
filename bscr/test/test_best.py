from bscr import testhelp as th
from bscr import util as U
from nose.plugins.skip import SkipTest
import os
import pdb
import pexpect
import re

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

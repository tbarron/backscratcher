from bscr import testhelp as th
from bscr import util as U
from nose.plugins.skip import SkipTest
import os
import pdb
import pexpect


# -----------------------------------------------------------------------------
class Test_PEP8(th.HelpedTestCase):
    def test_pep8(self):
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

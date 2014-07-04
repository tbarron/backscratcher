#!/usr/bin/env python
from bscr import mag
from bscr import util
import os
import pdb
import sys
import testhelp as th
import unittest

# ---------------------------------------------------------------------------
class TestMag(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_usage(self):
        a = mag.main(['./mag'], True)
        assert(a == mag.usage())

    # -------------------------------------------------------------------------
    def test_bit(self):
        a = mag.main(['./mag', '999'], True)
        self.magtest('999 = 999.00 b')

    # -------------------------------------------------------------------------
    def test_bbit(self):
        a = mag.main(['./mag', '999', '-b'], True)
        self.magtest('999 = 999.00 b')

    # -------------------------------------------------------------------------
    def test_kilo(self):
        a = mag.main(['./mag', '98765'], True)
        self.magtest('98765 = 98.77 Kb')

    # -------------------------------------------------------------------------
    def test_bkilo(self):
        a = mag.main(['./mag', '-b', '98765'], True)
        self.magtest('98765 = 96.45 Kib')

    # -------------------------------------------------------------------------
    def test_mega(self):
        a = mag.main(['./mag', '98765432'], True)
        self.magtest('98765432 = 98.77 Mb')

    # -------------------------------------------------------------------------
    def test_bmega(self):
        a = mag.main(['./mag', '-b', '98765432'], True)
        self.magtest('98765432 = 94.19 Mib')

    # -------------------------------------------------------------------------
    def test_giga(self):
        a = mag.main(['./mag', '12398765432'], True)
        self.magtest('12398765432 = 12.40 Gb')

    # -------------------------------------------------------------------------
    def test_bgiga(self):
        a = mag.main(['./mag', '-b', '12398765432'], True)
        self.magtest('12398765432 = 11.55 Gib')

    # -------------------------------------------------------------------------
    def test_tera(self):
        a = mag.main(['./mag', '12390008765432'], True)
        self.magtest('12390008765432 = 12.39 Tb')

    # -------------------------------------------------------------------------
    def test_btera(self):
        self.magtest('12398700065432 = 11.28 Tib')

    # -------------------------------------------------------------------------
    def test_peta(self):
        self.magtest('17239090087685432 = 17.24 Pb')

    # -------------------------------------------------------------------------
    def test_bpeta(self):
        self.magtest('71233986700065432 = 63.27 Pib')

    # -------------------------------------------------------------------------
    def test_exa(self):
        self.magtest('41873239090087685432 = 41.87 Eb')

    # -------------------------------------------------------------------------
    def test_bexa(self):
        self.magtest('87271233986700065432 = 75.70 Eib')

    # -------------------------------------------------------------------------
    def test_zetta(self):
        self.magtest('43541873239090087685432 = 43.54 Zb')

    # -------------------------------------------------------------------------
    def test_bzetta(self):
        self.magtest('23487271233986700065432 = 19.89 Zib')

    # -------------------------------------------------------------------------
    def test_yotta(self):
        self.magtest('75843541873239090087685432 = 75.84 Yb')

    # -------------------------------------------------------------------------
    def test_byotta(self):
        self.magtest('39423487271233986700065432 = 32.61 Yib')

    def magtest(self, string):
        d = string.split()
        v = d[0]
        if 'i' in d[3]:
            args = ['./mag', '-b', v]
        else:
            args = ['./mag', v]

        a = mag.main(args, True)
        try:
            assert(a == string)
        except AssertionError:
            print "\nexpected: '%s'" % a
            print "result:   '%s'" % string

    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    # -------------------------------------------------------------------------
    def test_mag_help(self):
        """
        Verify that 'mag --help' does the right thing
        """
        pass
    
    # -------------------------------------------------------------------------
    def test_which_file(self):
        # pdb.set_trace()
        idir = os.path.dirname(sys.modules['bscr.mag'].__file__)
        exp = os.path.dirname(os.path.abspath(__file__))
        self.assertEqual(os.path.basename(exp), 'test')
        exp = os.path.dirname(exp)
        if os.path.basename(exp) != 'bscr':
            exp = util.pj(exp, 'bscr')
        self.assertEqual(exp, idir,
                         "Expected '%s', got '%s'" % (exp, idir))

    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.fail("construction")
        
    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_which_script(self):
        """
        Verify that we're running the right script
        """
        self.fail('construction')

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()


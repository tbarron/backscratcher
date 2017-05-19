#!/usr/bin/env python
from bscr import mag
from bscr import util as U
import pexpect
import pytest
from bscr import testhelp as th


# -----------------------------------------------------------------------------
def test_mag_standalone():
    """
    Make these tests stand-alone
    """
    pytest.fail("Make mag tests stand-alone")


# ---------------------------------------------------------------------------
class TestMag(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_usage(self):
        """
        'mag' with no args should get the usage message
        """
        a = mag.main(['./mag'], True)
        assert(a == mag.usage())

    # -------------------------------------------------------------------------
    def test_bit(self):
        """
        Test 'mag' for bits (1000^0)
        """
        self.magtest('999 = 999.00 b')

    # -------------------------------------------------------------------------
    def test_bbit(self):
        """
        Test 'mag' for bits (1024^0)
        """
        self.magtest('999 = 999.00 b')

    # -------------------------------------------------------------------------
    def test_kilo(self):
        """
        Test 'mag' for kilobits (1000^1)
        """
        self.magtest('98765 = 98.77 Kb')

    # -------------------------------------------------------------------------
    def test_bkilo(self):
        """
        Test 'mag' for kibibits (1024^1)
        """
        self.magtest('98765 = 96.45 Kib')

    # -------------------------------------------------------------------------
    def test_mega(self):
        """
        Test 'mag' for megabits (1000^2)
        """
        self.magtest('98765432 = 98.77 Mb')

    # -------------------------------------------------------------------------
    def test_bmega(self):
        """
        Test 'mag' for mebibits (1024^2)
        """
        self.magtest('98765432 = 94.19 Mib')

    # -------------------------------------------------------------------------
    def test_giga(self):
        """
        Test 'mag' for gigabits (1000^3)
        """
        self.magtest('12398765432 = 12.40 Gb')

    # -------------------------------------------------------------------------
    def test_bgiga(self):
        """
        Test 'mag' for gibibits (1024^3)
        """
        self.magtest('12398765432 = 11.55 Gib')

    # -------------------------------------------------------------------------
    def test_tera(self):
        """
        Test 'mag' for terabits (1000^4)
        """
        self.magtest('12390008765432 = 12.39 Tb')

    # -------------------------------------------------------------------------
    def test_btera(self):
        """
        Test 'mag' for tebibits (1024^4)
        """
        self.magtest('12398700065432 = 11.28 Tib')

    # -------------------------------------------------------------------------
    def test_peta(self):
        """
        Test 'mag' for petabits (1000^5)
        """
        self.magtest('17239090087685432 = 17.24 Pb')

    # -------------------------------------------------------------------------
    def test_bpeta(self):
        """
        Test 'mag' for pebibits (1024^5)
        """
        self.magtest('71233986700065432 = 63.27 Pib')

    # -------------------------------------------------------------------------
    def test_exa(self):
        """
        Test mag for exabits (1000^6)
        """
        self.magtest('41873239090087685432 = 41.87 Eb')

    # -------------------------------------------------------------------------
    def test_bexa(self):
        """
        Test 'mag' for ebibits (1024^6)
        """
        self.magtest('87271233986700065432 = 75.70 Eib')

    # -------------------------------------------------------------------------
    def test_zetta(self):
        """
        Test 'mag' for zettabits (1000^7)
        """
        self.magtest('43541873239090087685432 = 43.54 Zb')

    # -------------------------------------------------------------------------
    def test_bzetta(self):
        """
        Test 'mag' for zebibits (1024^7)
        """
        self.magtest('23487271233986700065432 = 19.89 Zib')

    # -------------------------------------------------------------------------
    def test_yotta(self):
        """
        Test 'mag' for yottabits (1024^8)
        """
        self.magtest('75843541873239090087685432 = 75.84 Yb')

    # -------------------------------------------------------------------------
    def test_byotta(self):
        """
        Test 'mag' for yobibits (1024^8)
        """
        self.magtest('39423487271233986700065432 = 32.61 Yib')

    # -------------------------------------------------------------------------
    def magtest(self, string):
        """
        Test 'mag' for a specific value
        """
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
    def test_mag_help(self):
        """
        Verify that 'mag --help' does the right thing
        """
        cmd = U.script_location("mag")
        result = pexpect.run("%s --help" % cmd)
        exp = ["Usage: mag [-b] <number>",
               "Report the order of magnitude of <number>",
               "Options:",
               "-h, --help    show this help message and exit",
               "-b, --binary  div=1024 rather than 1000",
               ]
        self.assertTrue("Traceback" not in result,
                        "Traceback not expected in %s" %
                        U.lquote(result))
        for item in exp:
            self.assertTrue(item in result,
                            "Expected '%s' in %s" %
                            (item, U.lquote(result)))

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right mag module
        """
        self.assertModule('bscr.mag', __file__)

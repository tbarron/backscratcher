#!/usr/bin/env python
from bscr import odx
from bscr import util as U
import pexpect
from bscr import testhelp

# odx(25)         => 25 -> 031 / 25 / 0x19
# odx(0124)       => 0124 -> 0124 / 84 / 0x54
# odx(0x1f1f)     => 0x1f1f -> 017437 / 7967 / 0x1f1f
# odx(2ab)        => ValueError
# odx(0987)       => ValueError
# odx(0x5234g7)   => ValueError


# -----------------------------------------------------------------------------
class TestOdx(testhelp.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_decimal_good(self):
        """
        Verify output of odx with good decimal input
        """
        exp = "25 -> 031 / 25 / 0x19"
        self.expgot(exp, odx.odx('25'))

    # -------------------------------------------------------------------------
    def test_decimal_bad(self):
        """
        Verify output of odx with bad decimal input
        """
        exp = "invalid literal for int() with base 10"
        self.assertRaisesMsg(ValueError, exp, odx.odx, '2ab')

    # -------------------------------------------------------------------------
    def test_octal_good(self):
        """
        Verify output of odx with good octal input
        """
        exp = "0124 -> 0124 / 84 / 0x54"
        self.expgot(exp, odx.odx('0124'))

    # -------------------------------------------------------------------------
    def test_octal_bad(self):
        """
        Verify output of odx with bad octal input
        """
        exp = "invalid literal for int() with base 8"
        self.assertRaisesMsg(ValueError, exp, odx.odx, '0987')

    # -------------------------------------------------------------------------
    def test_hex_good(self):
        """
        Verify output of odx with good hex input
        """
        exp = "0x1f1f -> 017437 / 7967 / 0x1f1f"
        self.expgot(exp, odx.odx('0x1f1f'))

    # -------------------------------------------------------------------------
    def test_hex_bad(self):
        """
        Verify output of odx with bad hex input
        """
        exp = "invalid literal for int() with base 16"
        self.assertRaisesMsg(ValueError, exp, odx.odx, '0x5234g7')

    # -------------------------------------------------------------------------
    def test_odx_help(self):
        """
        Verify that 'odx --help' does the right thing
        """
        exp = ["Usage: odx {0<octal-value>|<decimal-value>|0x<hex-value>} ...",
               "    report each argument in octal, decimal, and hex format",
               "",
               "Options:",
               "  -h, --help   show this help message and exit",
               "  -d, --debug  run under debugger",
               ]
        cmd = U.script_location("odx")
        actual = pexpect.run("%s --help" % cmd)
        for line in exp:
            self.assertTrue(line in actual,
                            "Expected '%s' in %s" %
                            (line, U.lquote(actual)))

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.odx', __file__)

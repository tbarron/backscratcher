#!/usr/bin/env python
from bscr import odx
from bscr import util as U
from contextlib import closing
import os
import pdb
import pexpect
import StringIO as sio
import sys
import testhelp
import unittest

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
        exp = "25 -> 031 / 25 / 0x19"
        self.expgot(exp, odx.odx('25'))

    # -------------------------------------------------------------------------
    def test_decimal_bad(self):
        exp = "invalid literal for int() with base 10"
        with self.assertRaises(ValueError) as v:
            odx.odx('2ab')

        self.exp_in_got(exp, str(v.exception))

    # -------------------------------------------------------------------------
    def test_octal_good(self):
        exp = "0124 -> 0124 / 84 / 0x54"
        self.expgot(exp, odx.odx('0124'))

    # -------------------------------------------------------------------------
    def test_octal_bad(self):
        exp = "invalid literal for int() with base 8"
        with self.assertRaises(ValueError) as v:
            odx.odx('0987')

        self.exp_in_got(exp, str(v.exception))

    # -------------------------------------------------------------------------
    def test_hex_good(self):
        exp = "0x1f1f -> 017437 / 7967 / 0x1f1f"
        self.expgot(exp, odx.odx('0x1f1f'))

    # -------------------------------------------------------------------------
    def test_hex_bad(self):
        exp = "invalid literal for int() with base 16"
        with self.assertRaises(ValueError) as v:
            odx.odx('0x5234g7')

        self.exp_in_got(exp, str(v.exception))

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
        idir = U.bscr_root(sys.modules['bscr.odx'].__file__)
        exp = U.bscr_test_root(__file__)
        self.assertEqual(exp, idir,
                         "Expected '%s', got '%s'" % (exp, idir))
        
if __name__ == '__main__':
    unittest.main()
    

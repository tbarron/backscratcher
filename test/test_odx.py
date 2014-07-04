#!/usr/bin/env python
from contextlib import closing
import odx
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
    @unittest.skip("under construction")
    def test_odx_help(self):
        """
        Verify that 'odx --help' does the right thing
        """
        pass
    
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

if __name__ == '__main__':
    unittest.main()
    

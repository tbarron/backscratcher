#!/usr/bin/python
"""
jcal tests
"""
from bscr import jcal
import unittest

# -----------------------------------------------------------------------------
class JcalTest(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_EMPTY(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_jcal_help(self):
        """
        Verify that 'jcal --help' does the right thing
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


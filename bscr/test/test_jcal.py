#!/usr/bin/python
"""
jcal tests
"""
from bscr import jcal
from nose.plugins.skip import SkipTest
import unittest

# -----------------------------------------------------------------------------
class JcalTest(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_EMPTY(self):
        pass

    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_jcal_help(self):
        """
        Verify that 'jcal --help' does the right thing
        """
        raise SkipTest(">>> WRITE ME <<<")
    
    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        raise SkipTest(">>> WRITE ME <<<")
        

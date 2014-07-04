#!/usr/bin/env python
from bscr import chron
import unittest

# -----------------------------------------------------------------------------
class TestChron(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_hms_seconds(self):
        exp = 3923
        act = chron.hms_seconds("1:05:23")
        self.assertEqual(exp, act,
                         "Expected %d, got %d" % (exp, act))

    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_chron_help(self):
        """
        Verify that 'chron --help' does the right thing
        """
        pass
    
    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        pass
        
    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_which_script(self):
        """
        Verify that we're running the right script
        """
        pass
        
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

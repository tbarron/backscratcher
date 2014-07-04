#!/usr/bin/env python

from bscr import bscr
from bscr import fl
import os
import pexpect
import unittest

#------------------------------------------------------------------------------
class TestScripts(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_bscr_help(self):
        where = pexpect.which('bscr')
        here = os.path.basename(os.getcwd())
        if where is None or here == 'backscratcher':
            cmd = "bin/bscr"
        else:
            cmd = "bscr"
            
        result = pexpect.run('%s help' % cmd)
        self.assertFalse('Traceback' in result)
        for f in [x for x in dir(bscr) if x.startswith('bscr_')]:
            subc = f.replace('bscr_', '')
            self.assertTrue('%s - ' % subc in result)
        
    # -------------------------------------------------------------------------
    def test_bscr_help_help(self):
        where = pexpect.which('bscr')
        here = os.path.basename(os.getcwd())
        if where is None or here == 'backscratcher':
            cmd = "bin/bscr"
        else:
            cmd = "bscr"
            
        result = pexpect.run('%s help help' % cmd)
        self.assertFalse('Traceback' in result)
        self.assertTrue('help - show a list' in result)
        self.assertTrue('With no arguments' in result)
        self.assertTrue('With a command as argument' in result)

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

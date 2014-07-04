#!/usr/bin/python
"""
perrno tests
"""
from bscr import perrno
import unittest
import testhelp as th

# -----------------------------------------------------------------------------
class TestPerrno(unittest.TestCase):
    def test_all(self):
        with th.StdoutExcursion() as getval:
            perrno.main(["bin/perrno", "--all"])
            result = getval()
        self.assertIn("13  EACCES           Permission denied", result)
        self.assertNotIn("['EACCES']", result)

    def test_mnemonic(self):
        result = perrno.etranslate("EBADF")
        self.assertEqual("    9  EBADF            Bad file descriptor", result)

    def test_numeric(self):
        result = perrno.etranslate("3")
        self.assertEqual("    3  ESRCH            No such process", result)

    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_perrno_help(self):
        """
        Verify that 'perrno --help' does the right thing
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


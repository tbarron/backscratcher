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


#!/usr/bin/env python
import os
import sys
sys.path.insert(0, os.getcwd())
import bscr.align
import pdb
import pexpect
from nose.plugins.skip import SkipTest
from bscr import testhelp as th
from bscr import toolframe
import unittest
from bscr import util as U


# ---------------------------------------------------------------------------
def setUpModule():
    U.pythonpath_bscrroot()


# ---------------------------------------------------------------------------
def tearDownModule():
    flist = ['testdata']
    if os.getenv('KEEPFILES') is not None:
        return
    for fname in flist:
        if os.path.exists(fname):
            os.unlink(fname)


# ---------------------------------------------------------------------------
class TestAlign(th.HelpedTestCase):
    """
    Test suite for align
    """
    tdata = [" 1234  -12342 2342.9324 -1234.9238 7.82734E+25 -2.2343E-17",
             "abc  def ghi jkl mno qprs",
             "foobard simplification denomination vituperation spalshy"]
    expected = ("   1234          -12342     2342.9324    -1234.9238  " +
                "7.82734E+25  -2.2343E-17  \r\n" +
                "abc      def             ghi           jkl           " +
                "mno          qprs         \r\n" +
                "foobard  simplification  denomination  vituperation" +
                "  spalshy      \r\n")

    # -------------------------------------------------------------------------
    def test_align_help(self):
        """
        Verify that 'align --help' does the right thing
        """
        cmd = U.script_location("align")
        result = pexpect.run("%s --help" % cmd)
        nexp = "Traceback"
        self.assertFalse(nexp in result,
                         "Not expecting '%s' in %s" %
                         (nexp, U.lquote(result)))
        exp = "Align columns from input"
        self.assertTrue(exp in result,
                        "Expected '%s' in %s" %
                        (exp, U.lquote(result)))

    # -------------------------------------------------------------------------
    def test_digit_alignment(self):
        """
        Words that contain valid numeric specifications should be right
        aligned. Words containing non-numeric values should be left aligned.
        """
        script = U.script_location("align")
        S = pexpect.spawn(script)
        S.setecho(False)
        for line in self.tdata:
            S.sendline(line)
        S.send("\004")
        S.expect(pexpect.EOF)
        x = S.before
        S.close()

        self.assertEqual(self.expected, x,
                         '"""\n%s\n"""(%d)\n\n' %
                         (self.expected.replace(' ', '-'),
                          len(self.expected)) +
                         ' does not match' +
                         '\n\n"""\n%s\n"""(%d)' %
                         (x.replace(' ', '-'), len(x)))

    # -------------------------------------------------------------------------
    def test_named_input(self):
        """
        Handle both input on stdin as well as input from a named file.
        """
        tfilename = 'testdata'
        f = open(tfilename, 'w')
        for line in self.tdata:
            f.write(line + "\n")
        f.close()

        script = U.script_location("align")
        x = pexpect.run("%s %s" % (script, tfilename))

        self.assertEqual(self.expected, x,
                         '"""\n%s\n"""(%d)\n\n' %
                         (self.expected.replace(' ', '-'),
                          len(self.expected)) +
                         ' does not match' +
                         '\n\n"""\n%s\n"""(%d)' %
                         (x.replace(' ', '-'), len(x)))

    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.align', __file__)

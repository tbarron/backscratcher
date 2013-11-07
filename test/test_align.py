#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.getcwd())
import align
import pdb
import pexpect
import testhelp
import toolframe
import unittest

# ---------------------------------------------------------------------------
class AlignTest(unittest.TestCase):
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
    def test_digit_alignment(self):
        """
        Words that contain valid numeric specifications should be right
        aligned. Words containing non-numeric values should be left aligned.
        """
        S = pexpect.spawn("./align")
        S.setecho(False)
        for line in self.tdata:
            S.sendline(line)
        S.send("\004")
        S.expect(pexpect.EOF)
        x = S.before
        S.close()

        self.assertEqual(self.expected, x,
                         '"""\n%s\n"""(%d)\n\n' %
                         (self.expected.replace(' ','-'),
                          len(self.expected)) +
                         ' does not match' +
                         '\n\n"""\n%s\n"""(%d)' %
                          (x.replace(' ','-'), len(x)))
        
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

        S = pexpect.spawn("./align %s" % tfilename)
        S.expect(pexpect.EOF)
        x = S.before
        S.close()

        self.assertEqual(self.expected, x,
                         '"""\n%s\n"""(%d)\n\n' %
                         (self.expected.replace(' ','-'),
                          len(self.expected)) +
                         ' does not match' +
                         '\n\n"""\n%s\n"""(%d)' %
                          (x.replace(' ','-'), len(x)))
        
        
    # -------------------------------------------------------------------------
    def test_next_steps(self):
        self.fail("""
         - arrange to clean up after test_align.py
         - run pep8 on all my python code and clean up the complaints
        """)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    toolframe.ez_launch(test=AlignTest)

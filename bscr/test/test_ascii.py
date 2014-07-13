#!/usr/bin/env python
from bscr import ascii
from bscr import util as U
import os
import sys
import pdb
import pexpect
import testhelp
import toolframe
import unittest

# ---------------------------------------------------------------------------
def tearDownModule():
    flist = ['testdata']
    if os.getenv('KEEPFILES') is not None:
        return
    for fname in flist:
        if os.path.exists(fname):
            os.unlink(fname)


# ---------------------------------------------------------------------------
class TestAscii(unittest.TestCase):
    """
    Test suite for ascii
    """
    expected = [
    "0x00 NUL 0x01 SOH 0x02 STX 0x03 ETX 0x04 EOT 0x05 ENQ 0x06 ACK 0x07 BEL",
    "0x08 BS  0x09 TAB 0x0a LF  0x0b VT  0x0c FF  0x0d CR  0x0e SO  0x0f SI",
    "0x10 DLE 0x11 DC1 0x12 DC2 0x13 DC3 0x14 DC4 0x15 NAK 0x16 SYN 0x17 ETB",
    "0x18 CAN 0x19 EM  0x1a SUB 0x1b ESC 0x1c FS  0x1d GS  0x1e RS  0x1f US",
    "0x20 SPC 0x21 !   0x22 \"   0x23 #   0x24 $   0x25 %   0x26 &   0x27 \'",
    "0x28 (   0x29 )   0x2a *   0x2b +   0x2c ,   0x2d -   0x2e .   0x2f /",
    "0x30 0   0x31 1   0x32 2   0x33 3   0x34 4   0x35 5   0x36 6   0x37 7",
    "0x38 8   0x39 9   0x3a :   0x3b ;   0x3c <   0x3d =   0x3e >   0x3f ?",
    "0x40 @   0x41 A   0x42 B   0x43 C   0x44 D   0x45 E   0x46 F   0x47 G",
    "0x48 H   0x49 I   0x4a J   0x4b K   0x4c L   0x4d M   0x4e N   0x4f O",
    "0x50 P   0x51 Q   0x52 R   0x53 S   0x54 T   0x55 U   0x56 V   0x57 W",
    "0x58 X   0x59 Y   0x5a Z   0x5b [   0x5c \   0x5d ]   0x5e ^   0x5f _",
    "0x60 `   0x61 a   0x62 b   0x63 c   0x64 d   0x65 e   0x66 f   0x67 g",
    "0x68 h   0x69 i   0x6a j   0x6b k   0x6c l   0x6d m   0x6e n   0x6f o",
    "0x70 p   0x71 q   0x72 r   0x73 s   0x74 t   0x75 u   0x76 v   0x77 w",
    "0x78 x   0x79 y   0x7a z   0x7b {   0x7c |   0x7d }   0x7e ~",
    ""
    ]
        
    # -------------------------------------------------------------------------
    def test_ascii(self):
        """
        Run ascii and see if its output matches what is expected.
        """
        # pdb.set_trace()
        ascii = U.script_location("ascii")
        result = pexpect.run(ascii)
        eidx = 0
        for rline in result.split("\r\n"):
            rline = rline.rstrip(" ")
            self.assertEqual(self.expected[eidx], rline,
                             'Expected \n' +
                             U.lquote('%s (%d)' %
                                         (repr(self.expected[eidx]),
                                          len(self.expected[eidx]))) +
                             '\n but got \n' +
                             U.lquote('%s (%d)' %
                                         (repr(rline),
                                          len(rline))))
            eidx += 1

    # -------------------------------------------------------------------------
    def test_ascii_help(self):
        """
        Run 'ascii --help' and validate the output
        """
        cmd = U.script_location("ascii")
        result = pexpect.run("%s --help" % cmd)
        exp = "Display ASCII collating sequence"
        self.assertTrue(exp in result, "Expected '%s' in %s" %
                        (exp, U.lquote(result)))

    # -------------------------------------------------------------------------
    def test_final_newline(self):
        """
        Run ascii and verify output ends with a newline
        """
        # pdb.set_trace()
        ascii = U.script_location("ascii")
        result = pexpect.run(ascii)
        self.assertTrue(result.endswith("\n"),
                        "ascii output should end with newline")

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        idir = U.bscr_root(sys.modules['bscr.ascii'].__file__)
        exp = U.bscr_test_root(__file__)
        self.assertEqual(exp, idir,
                         "Expected '%s', got '%s'" % (exp, idir))
        
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

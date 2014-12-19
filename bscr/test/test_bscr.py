#!/usr/bin/env python

import pdb
import os
import sys
import bscr
import bscr.bscr
from bscr import fl
from bscr import testhelp as th
from bscr import util as U
import pexpect
import pytest
import unittest


# -----------------------------------------------------------------------------
class TestScripts(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_bscr_help(self):
        """
        Test 'bscr help'
        """
        self.dbgfunc()
        cmd = pexpect.which('bscr')
        result = pexpect.run('%s help' % cmd)
        self.assertFalse('Traceback' in result)
        for f in [x for x in dir(bscr.bscr) if x.startswith('bscr_')]:
            subc = f.replace('bscr_', '')
            self.assertTrue('%s - ' % subc in result)

    # -------------------------------------------------------------------------
    def test_bscr_help_help(self):
        """
        Test 'bscr help help'
        """
        self.dbgfunc()
        cmd = pexpect.which('bscr')
        result = pexpect.run('%s help help' % cmd)
        self.assertFalse('Traceback' in result)
        self.assertTrue('help - show a list' in result)
        self.assertTrue('With no arguments' in result)
        self.assertTrue('With a command as argument' in result)

    # -------------------------------------------------------------------------
    def test_bscr_version(self):
        """
        Test 'bscr version'
        """
        self.dbgfunc()
        cmd = "bscr version -v"
        result = th.rm_cov_warn(pexpect.run(cmd))
        self.assertTrue("Traceback" not in result,
                        "Not expecting 'Traceback' in %s" %
                        U.lquote(result))
        self.assertTrue("Backscratcher version" in result)
        self.assertEqual(2, len(result.split("\n")),
                         "Expected only 1 newlines in %s" %
                         U.lquote(result))

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.dbgfunc()
        self.assertModule('bscr.bscr', __file__)

    # -------------------------------------------------------------------------
    def test_python_which(self):
        """
        Calling python_which('sys') should get back a string containing the
        same path as sys.__file__
        """
        self.dbgfunc()
        self.assertEq(U.dirname(unittest.__file__),
                      bscr.python_which('unittest'))
        self.assertEq(U.__file__, bscr.python_which('bscr/util'))
        self.assertEq(U.__file__, bscr.python_which('bscr.util'))

    # -------------------------------------------------------------------------
    def test_perl_which(self):
        """
        Calling perl_which('Digest::MD5') should get back a string containing
        the same path as sys.__file__
        """
        self.dbgfunc()
        exp = ("/System/Library/Perl/5.16/darwin-thread-multi-2level/" +
               "Digest/MD5.pm")
        self.assertEq(exp, bscr.perl_which('Digest::MD5'))

    # -------------------------------------------------------------------------
    def test_bash_which(self):
        """
        Calling bash_which('emacs') should get back a string with a path to the
        emacs executable
        """
        self.dbgfunc()
        self.assertEq("/usr/bin/emacs",
                      bscr.bash_which("emacs"))

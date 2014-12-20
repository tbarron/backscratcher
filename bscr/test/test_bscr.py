#!/usr/bin/env python

import bscr
import bscr.bscr
from bscr import fl
import glob
import pdb
import os
import sys
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
        def rshave(path, comp):
            while comp in path:
                path = U.dirname(path)
            return path

        self.dbgfunc()
        act = rshave(bscr.python_which('unittest'), 'unittest')
        exp = rshave(unittest.__file__, 'unittest')
        self.assertEq(exp, act)

        self.assertEq(rshave(U.__file__, 'util'),
                      rshave(bscr.python_which('bscr/util'), 'util'))
        self.assertEq(rshave(U.__file__, 'util'),
                      rshave(bscr.python_which('bscr.util'), 'util'))

    # -------------------------------------------------------------------------
    def test_perl_which(self):
        """
        Calling perl_which('Digest::MD5') should get back a string containing
        the same path as sys.__file__
        """
        self.dbgfunc()
        perlinc = pexpect.run("perl -e 'print(\"@INC\");'")
        found = False
        for path in perlinc.split():
            exp = U.pj(path, "Digest", "MD5.pm")
            if glob.glob(exp):
                found = True
                break
        if found:
            self.assertEq(exp, bscr.perl_which('Digest::MD5'))
        else:
            pytest.skip("Digest/MD5 not found in perl @INC")

    # -------------------------------------------------------------------------
    def test_bash_which(self):
        """
        Calling bash_which('emacs') should get back a string with a path to the
        emacs executable
        """
        self.dbgfunc()
        self.assertEq(pexpect.which("emacs"),
                      bscr.bash_which("emacs"))

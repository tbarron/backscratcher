#!/usr/bin/env python

import pdb
import os
import sys
from bscr import bscr
from bscr import fl
from bscr import testhelp as th
from bscr import util as U
import pexpect
from nose.plugins.skip import SkipTest
import unittest


# -----------------------------------------------------------------------------
class TestScripts(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def test_bscr_help(self):
        """
        Test 'bscr help'
        """
        cmd = pexpect.which('bscr')
        result = pexpect.run('%s help' % cmd)
        self.assertFalse('Traceback' in result)
        for f in [x for x in dir(bscr) if x.startswith('bscr_')]:
            subc = f.replace('bscr_', '')
            self.assertTrue('%s - ' % subc in result)

    # -------------------------------------------------------------------------
    def test_bscr_help_help(self):
        """
        Test 'bscr help help'
        """
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
        cmd = "bscr version -v"
        result = pexpect.run(cmd)
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
        self.assertModule('bscr.bscr', __file__)

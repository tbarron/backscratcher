#!/usr/bin/env python

from bscr import bscr
from bscr import fl
from bscr import testhelp as th
from bscr import util as U
import os
import pexpect
from nose.plugins.skip import SkipTest
import sys
import unittest


# -----------------------------------------------------------------------------
def setUpModule():
    U.pythonpath_bscrroot()


# -----------------------------------------------------------------------------
class TestScripts(th.HelpedTestCase):
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
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.bscr', __file__)

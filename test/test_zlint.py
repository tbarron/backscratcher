"""
This file checks for best practice compliance.
 - Does my code conform to PEP8?
 - Do I have any inadvertent duplicate routines?
 - Do I have routines with no __doc__?

Conveniently, pylint takes care of all of this
"""
import glob
import inspect
import os
import pdb
import pexpect
import re
import sys
from bscr import testhelp as th
import types
import unittest
from bscr import util as U

# -----------------------------------------------------------------------------
def test_pylint():
    """
    Run pylint to check the quality of the code
    """
    # result = pexpect.run("pylint -rn bscr")
    result = pexpect.run("flake8 bscr")
    assert result == ''

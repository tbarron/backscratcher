import os
import pdb
import shutil
import sys

import pexpect
import pytest

from bscr import testhelp as th
from bscr import util as U

            self.assertEqual(exp, got,
                             "\nExpected '%s',\n     got '%s'" %
                             (exp, got))

                    '',
                    'import optparse',
                    'import pdb',
                    'import sys',
                    'from bscr import toolframe',
                    'import unittest',
                    '',
                    'def main(argv = None):',
                    '    if argv == None:',
                    '        argv = sys.argv',
                    '',
                    '    prs = optparse.OptionParser()',
                    "    prs.add_option('-d', '--debug',",
                    "                   action='store_true', default=False,",
                    "                   dest='debug',",
                    "                   help='run the debugger')",
                    '    (opts, args) = prs.parse_args(argv)',
                    "",
                    "    if opts.debug:",
                    "        pdb.set_trace()",
                    '',
                    '    # process arguments',
                    '    for arg in args:',
                    '        process(arg)',
                    '',
                    'class XyzzyTest(unittest.TestCase):',
                    '    def test_example(self):',
                    '        pass',
                    '',
                    'toolframe.ez_launch(__name__, main)', ]

        return expected

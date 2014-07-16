#!/usr/bin/env python
from bscr import list
import pprint
from bscr import testhelp as th
from nose.plugins.skip import SkipTest
import unittest

class TestList(th.HelpedTestCase):
    # -----------------------------------------------------------------------
    def assertInList(self, exp, larg):
        self.assertIn(exp, larg,
                      "'%s' is not in list '%s'" %
                      (exp, pprint.pformat(larg)))
        
    # -----------------------------------------------------------------------
    def test_generate_list(self):
        """
        Generate a list from the output of a command
        """
        a = list.generate_list("ls")
        self.assertInList('LICENSE', a)
        self.assertInList("bin", a)
        self.assertInList("README.md", a)

    # -----------------------------------------------------------------------
    def test_list_minus(self):
        """
        Test the minus operation
        """
        a = list.list_minus(['one', 'two', 'three', 'four', 'five'],
                            ['two', 'four', 'six', 'eight'])
        assert(a == ['one', 'three', 'five'])

    # -----------------------------------------------------------------------
    def test_list_union(self):
        """
        Test the union operation
        """
        a = list.list_union(['one', 'three', 'five'],
                            ['two', 'four', 'five', 'six', 'two'])
        a.sort()
        assert(a == ['five', 'four', 'one', 'six', 'three', 'two'])

    # -----------------------------------------------------------------------
    def test_list_intersect(self):
        """
        Test the intersect operation
        """
        a = list.list_intersect(['one', 'two', 'three', 'four', 'five'],
                                ['two', 'four', 'six', 'eight', 'ten'])
        assert(a == ['two', 'four'])

    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_list_help(self):
        """
        Verify that 'list --help' does the right thing
        """
        raise SkipTest(">>> WRITE ME <<<")
    
    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        raise SkipTest(">>> WRITE ME <<<")
        
    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_which_script(self):
        """
        Verify that we're running the right script
        """
        raise SkipTest(">>> WRITE ME <<<")

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

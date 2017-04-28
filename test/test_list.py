#!/usr/bin/env python
from bscr import list
from bscr import testhelp as th
from bscr import util as U
import pprint


# -----------------------------------------------------------------------------
class TestList(th.HelpedTestCase):
    # -------------------------------------------------------------------------
    def assertInList(self, exp, larg):
        """
        Assert that *exp* is in *larg*
        """
        self.assertIn(exp, larg,
                      "'%s' is not in list '%s'" %
                      (exp, pprint.pformat(larg)))

    # -------------------------------------------------------------------------
    def test_generate_list(self):
        """
        Generate a list from the output of a command
        """
        with U.Chdir(U.dirname(__file__)):
            a = list.generate_list("ls")
            self.assertInList("__init__.py", a)
            self.assertInList("test_list.py", a)
            self.assertInList("test_util.py", a)

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
        self.assertOptionHelp("list",
                              "usage: list {minus|union|intersect} " +
                              "<list-1> <list-2>")

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.list', __file__)

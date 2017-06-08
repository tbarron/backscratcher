from bscr import list
from bscr import testhelp as th
from bscr import util as U
import pprint
import pytest


# -----------------------------------------------------------------------------
def test_generate_list(tmpdir):
    """
    Generate a list from the output of a command
    """
    pytest.debug_func()
    flist = ["abc", "def", "ghi"]
    for fname in flist:
        tmpdir.join(fname).ensure()
    with U.Chdir(tmpdir.strpath):
        a = list.generate_list("ls")
        for fname in flist:
            assert fname in a
    assert sorted(flist) == sorted(a)


# -----------------------------------------------------------------------
def test_list_minus():
    """
    Test the minus operation
    """
    a = list.list_minus(['one', 'two', 'three', 'four', 'five'],
                        ['two', 'four', 'six', 'eight'])
    assert a == ['one', 'three', 'five']


# -----------------------------------------------------------------------
def test_list_union():
    """
    Test the union operation
    """
    a_list = ['one', 'three', 'five']
    b_list = ['two', 'four', 'five', 'six', 'two']
    union = list.list_union(a_list, b_list)
    union.sort()
    assert(union == ['five', 'four', 'one', 'six', 'three', 'two'])


# -----------------------------------------------------------------------------
def test_list_standalone():
    """
    Make these tests stand-alone
    """
    pytest.fail("Make list tests stand-alone")


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

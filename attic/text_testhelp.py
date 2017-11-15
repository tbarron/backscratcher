from bscr import testhelp as th
import pytest


# -----------------------------------------------------------------------------
def test_deprecate():
    """
    Make these tests stand-alone
    """
    pytest.fail("Deprecate and remove testhelp tests and payload")


# ---------------------------------------------------------------------------
class TesthelpTest(th.HelpedTestCase):
    # -----------------------------------------------------------------------
    def test_all_tests(self):
        """
        Routine all_tests() should collect testables in a TestCase object. The
        optional second argument is used as a filter to match test names
        """
        all = ['TesthelpTest.test_all_tests',
               'TesthelpTest.test_list_tests',
               'TesthelpTest.test_expected_vs_got'].sort()
        l = th.all_tests('__main__').sort()
        self.assertEq(all, l)
        l = th.all_tests('__main__', 'no such tests')
        self.assertEq([], l)
        l = th.all_tests('__main__', 'helpTest').sort()
        self.assertEq(all, l)

    def test_list_tests(self):
        """
        Routine list_tests() sends a list of tests to stdout. The second
        element of the first argument filters the tests
        """
        tlist = [['one', None],
                 ['two', None],
                 ['three', None],
                 ['four', None],
                 ['five', None]]
        self.redirect_list([],
                           '',
                           tlist,
                           "one\ntwo\nthree\nfour\nfive\n")
        self.redirect_list(['', 'o'],
                           '',
                           tlist,
                           "one\ntwo\nfour\n")
        self.redirect_list(['', 'e'],
                           '',
                           tlist,
                           "one\nthree\nfive\n")

    def redirect_list(self, args, final, testlist, expected):
        """
        Manage the stdout redirection for one test
        """
        with th.StdoutExcursion() as getval:
            th.list_tests(args, final, testlist)
            result = getval()
        self.assertEqual(expected, result,
                         "Expected '%s', got '%s'" % (expected, result))

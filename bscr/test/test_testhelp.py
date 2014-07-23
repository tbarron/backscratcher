from bscr import testhelp as th
import StringIO
import sys


# ---------------------------------------------------------------------------
class TesthelpTest(th.HelpedTestCase):
    # -----------------------------------------------------------------------
    def test_all_tests(self):
        all = ['TesthelpTest.test_all_tests',
               'TesthelpTest.test_list_tests',
               'TesthelpTest.test_expected_vs_got'].sort()
        l = th.all_tests('__main__').sort()
        th.expectVSgot(all, l)
        l = th.all_tests('__main__', 'no such tests')
        th.expectVSgot([], l)
        l = th.all_tests('__main__', 'helpTest').sort()
        th.expectVSgot(all, l)

    def test_list_tests(self):
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
        with th.StdoutExcursion() as getval:
            th.list_tests(args, final, testlist)
            result = getval()
        self.assertEqual(expected, result,
                         "Expected '%s', got '%s'" % (expected, result))

    def test_expected_vs_got(self):
        self.redirected_evg('', '', '')
        self.redirected_evg('one', 'two',
                            "EXPECTED: 'one'\n" +
                            "GOT:      'two'\n")

    def redirected_evg(self, exp, got, expected):
        s = StringIO.StringIO()
        save_stdout = sys.stdout
        sys.stdout = s
        try:
            th.expectVSgot(exp, got)
        except AssertionError:
            pass
        r = s.getvalue()
        s.close()
        sys.stdout = save_stdout

        try:
            assert(r.startswith(expected))
        except AssertionError:
            print "expected: '''\n%s'''" % expected
            print "got:      '''\n%s'''" % r

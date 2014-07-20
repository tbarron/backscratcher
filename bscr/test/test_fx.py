from bscr import fx
from bscr import testhelp as th
from bscr import util as U
import glob
import re
import optparse
import os
import pdb
import pexpect
import shutil
import StringIO
import sys
import unittest


# ---------------------------------------------------------------------------
class TestFx(th.HelpedTestCase):
    """
    Tests for code in fx.py.
    """
    testdir = "/tmp/fx_test"

    # -----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(TestFx.testdir):
            os.mkdir(TestFx.testdir)

    # -----------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        kf = os.getenv("KEEPFILES")
        if kf is None or not int(kf):
            shutil.rmtree(TestFx.testdir)

    # -----------------------------------------------------------------------
    def test_BatchCommand_both(self):
        """
        Test BatchCommand with dryrun True and quiet True.
        """
        with U.Chdir(self.testdir):
            inlist = range(1, 250)
            f = open('tmpfile', 'w')
            for x in inlist:
                f.write(str(x) + '\n')
            f.close()

            v = optparse.Values({'dryrun': True, 'quiet': False, 'xargs': True,
                                 'cmd': 'echo %'})

            x = StringIO.StringIO(" ".join([str(z) for z in range(1, 250)]))
            q = fx.xargs_wrap("echo %", x)
            exp = ''
            for chunk in q:
                exp += re.sub('^echo ', "would do 'echo ", chunk) + "'\n"

            self.indirect('tmpfile')
            self.redirect()
            fx.BatchCommand(v, [])
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_BatchCommand_dryrun(self):
        """
        Test BatchCommand with dryrun True and quiet False.
        """
        with U.Chdir(self.testdir):
            inlist = range(1, 250)
            f = open('tmpfile', 'w')
            for x in inlist:
                f.write(str(x) + '\n')
            f.close()

            v = optparse.Values({'dryrun': True, 'quiet': False, 'xargs': True,
                                 'cmd': 'echo %'})

            x = StringIO.StringIO(" ".join([str(z) for z in range(1, 250)]))
            q = fx.xargs_wrap("echo %", x)
            exp = ''
            for chunk in q:
                exp += re.sub('^echo ', "would do 'echo ", chunk) + "'\n"

            self.indirect('tmpfile')
            self.redirect()
            fx.BatchCommand(v, [])
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_BatchCommand_neither(self):
        """
        Test BatchCommand with dryrun and quiet both False.
        """
        with U.Chdir(self.testdir):
            inlist = range(1, 250)
            f = open('tmpfile', 'w')
            for x in inlist:
                f.write(str(x) + '\n')
            f.close()

            v = optparse.Values({'dryrun': False, 'quiet': False,
                                 'xargs': True, 'cmd': 'echo %'})

            x = StringIO.StringIO(" ".join([str(z) for z in range(1, 250)]))
            q = fx.xargs_wrap("echo %", x)
            exp = ''
            for chunk in q:
                exp += chunk + '\n'
                exp += re.sub('^echo ', '', chunk) + '\n'

            self.indirect('tmpfile')
            self.redirect()
            fx.BatchCommand(v, [])
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_BatchCommand_quiet(self):
        """
        Test BatchCommand with dryrun False and quiet True.
        """
        with U.Chdir(self.testdir):
            inlist = range(1, 250)
            f = open('tmpfile', 'w')
            for x in inlist:
                f.write(str(x) + '\n')
            f.close()

            v = optparse.Values({'dryrun': False, 'quiet': True, 'xargs': True,
                                 'cmd': 'echo %'})

            x = StringIO.StringIO(" ".join([str(z) for z in range(1, 250)]))
            q = fx.xargs_wrap("echo %", x)
            exp = ''
            for chunk in q:
                # exp += chunk + '\n'
                exp += re.sub('^echo ', '', chunk) + '\n'

            self.indirect('tmpfile')
            self.redirect()
            fx.BatchCommand(v, [])
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_IterateCommand_both(self):
        """
        Test IterateCommand() with dryrun True and quiet True.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': True, 'quiet': True,
                                 'cmd': 'echo %',
                                 'irange': '5:10'})
            exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

            self.redirect()
            fx.IterateCommand(v, [])
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_IterateCommand_dryrun(self):
        """
        Test IterateCommand() with dryrun True and quiet False.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': True, 'quiet': False,
                                 'cmd': 'echo %',
                                 'irange': '5:10'})
            exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

            self.redirect()
            fx.IterateCommand(v, [])
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_IterateCommand_neither(self):
        """
        Test IterateCommand() with dryrun False and quiet False.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': False, 'quiet': False,
                                 'cmd': 'echo %',
                                 'irange': '5:10'})
            exp = "".join(["echo %d\n%d\n" % (i, i) for i in range(5, 10)])

            self.redirect()
            fx.IterateCommand(v, [])
            actual = self.undirect()
            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_IterateCommand_quiet(self):
        """
        Test IterateCommand() with dryrun False and quiet True.
        """
        # pdb.set_trace()
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': False, 'quiet': True,
                                 'cmd': 'echo %',
                                 'irange': '5:10'})
            exp = "".join(["%d\n" % i for i in range(5, 10)])

            self.redirect()
            fx.IterateCommand(v, [])
            actual = self.undirect()
            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_SubstCommand_both(self):
        """
        Test SubstCommand() with dryrun True and quiet True.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': True, 'quiet': True, 'cmd': 'ls %'})
            a = ['a.pl', 'b.pl', 'c.pl']
            exp = "".join(["would do 'ls %s'\n" % x for x in a])
            self.unlink(a)

            self.redirect()
            fx.SubstCommand(v, a)
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_SubstCommand_dryrun(self):
        """
        Test SubstCommand() with dryrun True and quiet False.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': True, 'quiet': False,
                                 'cmd': 'ls %'})
            a = ['a.pl', 'b.pl', 'c.pl']
            exp = "".join(["would do 'ls %s'\n" % x for x in a])
            self.unlink(a)

            self.redirect()
            fx.SubstCommand(v, a)
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_SubstCommand_neither(self):
        """
        Test SubstCommand() with dryrun False and quiet False.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': False, 'quiet': False,
                                 'cmd': 'ls %'})
            a = ['a.pl', 'b.pl', 'c.pl']
            exp = "".join(['ls %s\n%s\n' % (x, x) for x in a])
            U.touch(a)

            self.redirect()
            fx.SubstCommand(v, a)
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_SubstCommand_quiet(self):
        """
        Test SubstCommand() with dryrun False and quiet True.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': False, 'quiet': True,
                                 'cmd': 'ls %'})
            a = ['a.pl', 'b.pl', 'c.pl']
            exp = "".join(['%s\n' % x for x in a])
            U.touch(a)

            self.redirect()
            fx.SubstCommand(v, a)
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_SubstRename_both(self):
        """
        Test SubstRename() with dryrun True and quiet True.
        """
        with U.Chdir(self.testdir):
            arglist = ['a.pl', 'b.pl', 'c.pl']
            for a in arglist:
                U.touch(a)
            expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                                [q.replace('.pl', '') for q in arglist]])
            exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
            v = optparse.Values({'dryrun': True, 'quiet': True,
                                 'edit': 's/.pl/.xyzzy'})

            self.redirect()
            fx.SubstRename(v, arglist)
            actual = self.undirect()

            self.check_result(expected == actual, expected, actual)

            q = glob.glob('*.pl')
            q.sort()
            self.check_result(q == arglist, arglist, q)

    # -----------------------------------------------------------------------
    def test_SubstRename_dryrun(self):
        """
        Test SubstRename() with dryrun True and quiet False.
        """
        with U.Chdir(self.testdir):
            arglist = ['a.pl', 'b.pl', 'c.pl']
            for a in arglist:
                U.touch(a)
            expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                                [q.replace('.pl', '') for q in arglist]])
            exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
            v = optparse.Values({'dryrun': True, 'quiet': False,
                                 'edit': 's/.pl/.xyzzy'})

            self.redirect()
            fx.SubstRename(v, arglist)
            actual = self.undirect()

            self.check_result(expected == actual, expected, actual)

            q = glob.glob('*.pl')
            q.sort()
            self.check_result(q == arglist, arglist, q)

    # -----------------------------------------------------------------------
    def test_SubstRename_neither(self):
        """
        Test SubstRename() with dryrun False and quiet False.
        """
        with U.Chdir(self.testdir):
            arglist = ['a.pl', 'b.pl', 'c.pl']
            for a in arglist:
                U.touch(a)
            expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                                [q.replace('.pl', '') for q in arglist]])
            exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
            v = optparse.Values({'dryrun': False, 'quiet': False,
                                 'edit': 's/.pl/.xyzzy'})

            self.redirect()
            fx.SubstRename(v, arglist)
            actual = self.undirect()

            self.check_result(expected == actual, expected, actual)

            q = glob.glob('*.xyzzy')
            q.sort()
            self.check_result(q == exp, exp, q)

    # -----------------------------------------------------------------------
    def test_SubstRename_quiet(self):
        """
        Test SubstRename() with dryrun False and quiet True.
        """
        with U.Chdir(self.testdir):
            arglist = ['a.pl', 'b.pl', 'c.pl']
            for a in arglist:
                U.touch(a)
            expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                                [q.replace('.pl', '') for q in arglist]])
            exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
            v = optparse.Values({'dryrun': False, 'quiet': True,
                                 'edit': 's/.pl/.xyzzy'})

            self.redirect()
            fx.SubstRename(v, arglist)
            actual = self.undirect()

            self.check_result(expected == actual, expected, actual)

            q = glob.glob('*.pl')
            q.sort()
            self.check_result(q == [], [], q)

            q = glob.glob('*.xyzzy')
            q.sort()
            self.check_result(q == exp, exp, q)

    # -----------------------------------------------------------------------
    def test_psys_neither(self):
        """
        Test routine psys with dryrun False and quiet False.
        """
        # self.redirect()
        root = U.findroot()
        with th.StdoutExcursion() as getval:
            v = optparse.Values({'dryrun': False, 'quiet': False})
            fx.psys('ls -d %s/fx.py' % root, v)
            actual = getval()
        # actual = self.undirect()
        expected = "ls -d %s/fx.py\n%s/fx.py\n" % (root, root)
        self.assertEqual(expected, actual)

    # -----------------------------------------------------------------------
    def test_psys_dryrun(self):
        """
        Test routine psys with dryrun True and quiet False.
        """
        # self.redirect()
        with th.StdoutExcursion() as getval:
            v = optparse.Values({'dryrun': True, 'quiet': False})
            fx.psys('ls -d nosuchfile', v)
            actual = getval()
        expected = "would do 'ls -d nosuchfile'\n"
        self.assertEqual(expected, actual)

    # -----------------------------------------------------------------------
    def test_psys_quiet(self):
        """
        Test routine psys with dryrun False and quiet True.
        """
        with U.Chdir(self.testdir):
            with th.StdoutExcursion() as getval:
                v = optparse.Values({'dryrun': False, 'quiet': True})
                fx.psys('ls', v)
                actual = getval()
        expected = "a.xyzzy\nb.xyzzy\nc.xyzzy\ntmpfile\n"
        self.assertEqual(expected, actual,
                         "%s\n   !=\n%s" %
                         (U.lquote(expected), U.lquote(actual)))
        # self.check_result(expected == actual, expected, actual)

    # -----------------------------------------------------------------------
    def test_psys_both(self):
        """
        Test routine psys with dryrun True and quiet True.
        """
        with th.StdoutExcursion() as getval:
            v = optparse.Values({'dryrun': True, 'quiet': True})
            fx.psys('ls -d fx.py', v)
            actual = getval()
        expected = "would do 'ls -d fx.py'\n"
        assert(expected == actual)

    # -----------------------------------------------------------------------
    def test_usage(self):
        """
        Test the Usage routine.
        """
        exp = '\n'
        exp += '    fx [-n] -c <command> <files> (% in the command becomes'
        exp += ' filename)\n'
        exp += '            -e s/old/new/ <files> (rename file old to new'
        exp += ' name)\n'
        exp += '            -i low:high -c <command> (% ranges from low to'
        exp += ' high-1)\n            '
        actual = fx.Usage()
        self.assertEqual(actual, exp,
                         "%s != %s" %
                         (U.lquote(repr(actual)), U.lquote(repr(exp))))

    # -------------------------------------------------------------------------
    def test_fx_help(self):
        """
        Verify that 'fx --help' does the right thing
        """
        # pdb.set_trace()
        exp_l = ["Usage:",
                 "fx [-n] -c <command> <files> (% in the command becomes" +
                 " filename)",
                 "-e s/old/new/ <files> (rename file old to new name)",
                 "-i low:high -c <command> (% ranges from low to high-1)",
                 "Options:",
                 "",
                 "-c CMD, --command=CMD",
                 "command to apply to all arguments",
                 "-d, --debug           run under the debugger",
                 "-e EDIT, --edit=EDIT  file rename expression applied to " +
                 "all arguments",
                 " -i IRANGE, --integer=IRANGE",
                 "low:high -- generate range of numbers",
                 "-n, --dryrun          dryrun or execute",
                 "-q, --quiet           don't echo commands, just run them",
                 "-x, --xargs           batch input from stdin into command" +
                 " lines like xargs",
                 ]
        script = U.script_location("fx")
        result = pexpect.run("%s --help" % script)
        for exp_s in exp_l:
            self.assertTrue(exp_s in result,
                            "Expected '%s' in %s" %
                            (exp_s, U.lquote(result)))

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.fx', __file__)

    # -----------------------------------------------------------------------
    def check_result(self, expr, expected, actual):
        """
        Calling this is similar to saying 'assert(expected == actual)'.

        If it fails, we report expected and actual. Otherwise, just return.
        """
        if not expr:
            raise AssertionError("'''\n%s\n''' != '''\n%s\n'''"
                                 % (expected, actual))

    # -----------------------------------------------------------------------
    def indirect(self, filename):
        """
        Arrange stdin to read from filename.
        """
        self.stdin = sys.stdin
        sys.stdin = open(filename, 'r')

    # -----------------------------------------------------------------------
    def redirect(self):
        """
        Aim stdout at a memory string so we can capture a function's output.
        """
        self.stdout = sys.stdout
        sys.stdout = StringIO.StringIO()

    # -----------------------------------------------------------------------
    def touch(self, touchables):
        """
        Touch the file or files named in touchables (string or list).
        """
        if type(touchables) == list:
            for f in touchables:
                open(f, 'a').close()
        elif type(touchables) == str:
            open(touchables, 'a').close()
        else:
            raise StandardError('argument must be list or string')

    # -----------------------------------------------------------------------
    def undirect(self):
        """
        Reset stdout (and stdin if needed) back to the terminal.
        """
        rval = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = self.stdout
        if (not os.isatty(sys.stdin.fileno()) and
                os.isatty(self.stdin.fileno())):
            sys.stdin = self.stdin
        return rval

    # -----------------------------------------------------------------------
    def unlink(self, args):
        """
        Unlink the file or files named in args (may be string or list).
        """
        if type(args) == list:
            for f in args:
                if os.path.exists(f):
                    os.unlink(f)
        elif type(args) == str:
            if os.path.exists(args):
                os.unlink(args)
        else:
            raise StandardError('argument must be list or string')

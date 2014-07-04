from bscr import fx
import glob
import re
import optparse
import os
import pdb
import StringIO
import sys
import testhelp as th
import unittest
from bscr import util

# ---------------------------------------------------------------------------
class TestFx(unittest.TestCase):
    """
    Tests for code in fx.py.
    """
    testdir = "fx_test"
    
    # -----------------------------------------------------------------------
    def test_BatchCommand_both(self):
        """
        Test BatchCommand with dryrun True and quiet True.
        """
        with util.Chdir(self.testdir):
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
        # self.into_testdir()
        with util.Chdir(self.testdir):
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
        # self.into_testdir()
        with util.Chdir(self.testdir):
            inlist = range(1, 250)
            f = open('tmpfile', 'w')
            for x in inlist:
                f.write(str(x) + '\n')
            f.close()

            v = optparse.Values({'dryrun': False, 'quiet': False, 'xargs': True,
                                 'cmd': 'echo %'})

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
        # self.into_testdir()
        with util.Chdir(self.testdir):
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
        # self.into_testdir()
        with util.Chdir(self.testdir):
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
        # self.into_testdir()
        with util.Chdir(self.testdir):
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
        # self.into_testdir()
        with util.Chdir(self.testdir):
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
        # self.into_testdir()
        with util.Chdir(self.testdir):
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
        # self.into_testdir()
        with util.Chdir(self.testdir):
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
        # self.into_testdir()
        with util.Chdir(self.testdir):
            v = optparse.Values({'dryrun': True, 'quiet': False, 'cmd': 'ls %'})
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
        # self.into_testdir()
        with util.Chdir(self.testdir):
            v = optparse.Values({'dryrun': False, 'quiet': False, 'cmd': 'ls %'})
            a = ['a.pl', 'b.pl', 'c.pl']
            exp = "".join(['ls %s\n%s\n' % (x, x) for x in a])
            self.touch(a)

            self.redirect()
            fx.SubstCommand(v, a)
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_SubstCommand_quiet(self):
        """
        Test SubstCommand() with dryrun False and quiet True.
        """
        # self.into_testdir()
        with util.Chdir(self.testdir):
            v = optparse.Values({'dryrun': False, 'quiet': True, 'cmd': 'ls %'})
            a = ['a.pl', 'b.pl', 'c.pl']
            exp = "".join(['%s\n' % x for x in a])
            self.touch(a)

            self.redirect()
            fx.SubstCommand(v, a)
            actual = self.undirect()

            self.check_result(exp == actual, exp, actual)

    # -----------------------------------------------------------------------
    def test_SubstRename_both(self):
        """
        Test SubstRename() with dryrun True and quiet True.
        """
        # self.into_testdir()
        with util.Chdir(self.testdir):
            arglist = ['a.pl', 'b.pl', 'c.pl']
            for a in arglist:
                self.touch(a)
            expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                                [q.replace('.pl', '') for q in arglist]])
            exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
            v = optparse.Values({'dryrun': True, 'quiet': True, 'edit': 's/.pl/.xyzzy'})

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
        with util.Chdir(self.testdir):
            arglist = ['a.pl', 'b.pl', 'c.pl']
            for a in arglist:
                self.touch(a)
            expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                                [q.replace('.pl', '') for q in arglist]])
            exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
            v = optparse.Values({'dryrun': True, 'quiet': False, 'edit': 's/.pl/.xyzzy'})

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
        with util.Chdir(self.testdir):
            arglist = ['a.pl', 'b.pl', 'c.pl']
            for a in arglist:
                self.touch(a)
            expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                                [q.replace('.pl', '') for q in arglist]])
            exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
            v = optparse.Values({'dryrun': False, 'quiet': False, 'edit': 's/.pl/.xyzzy'})

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
        with util.Chdir(self.testdir):
            arglist = ['a.pl', 'b.pl', 'c.pl']
            for a in arglist:
                self.touch(a)
            expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                                [q.replace('.pl', '') for q in arglist]])
            exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
            v = optparse.Values({'dryrun': False, 'quiet': True, 'edit': 's/.pl/.xyzzy'})

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
    def test_expand(self):
        """
        Test the expand routine.
        """
        home = os.environ['HOME']
        input = '~/$PWD'
        expected = '%s/%s' % (home, os.environ['PWD'])
        actual = fx.expand(input)
        assert(expected == actual)

    # -----------------------------------------------------------------------
    def test_psys_neither(self):
        """
        Test routine psys with dryrun False and quiet False.
        """
        # self.redirect()
        root = util.findroot()
        with th.StdoutExcursion() as getval:
            v = optparse.Values({'dryrun': False, 'quiet': False})
            fx.psys('ls -d %s/fx.py' % root, v)
            actual = getval()
        # actual = self.undirect()
        expected = "ls -d %s/fx.py\n%s/fx.py\n" % (root,root)
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
        with th.StdoutExcursion() as getval:
            v = optparse.Values({'dryrun': False, 'quiet': True})
            fx.psys('ls -d bscr/fx.py', v)
            actual = getval()
        expected = "bscr/fx.py\n"
        self.check_result(expected == actual, expected, actual)

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
        self.redirect()
        fx.Usage()
        exp = '\n'
        exp += '  fx [-n] -c <command> <files> (% in the command becomes'
        exp += ' filename)\n'
        exp += '          -e s/old/new/ <files> (rename file old to new'
        exp += ' name)\n'
        exp += '          -i low:high <command> (% ranges from low to'
        exp += ' high-1)\n'
        exp += '\n'
        actual = self.undirect()
        assert(actual == exp)

    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_fx_help(self):
        """
        Verify that 'fx --help' does the right thing
        """
        pass
    
    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.fail("construction")
        
    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_which_script(self):
        """
        Verify that we're running the right script
        """
        self.fail('construction')

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
    def into_testdir(self):
        """
        Make sure we're in the test directory.

        Create it if necessary, then step down into it unless we're
        already there.
        """
        x = os.getcwd()
        if os.path.basename(x) != 'fx_test':
            if not os.path.exists('fx_test'):
                os.mkdir('fx_test')
            os.chdir('fx_test')

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


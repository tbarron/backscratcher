from bscr import fx
from bscr import testhelp as th
from bscr import util as U
import glob
import re
import optparse
import os
import pexpect
import shutil

import pytest


# -----------------------------------------------------------------------------
def test_standalone():
def test_batch_command_both(tmpdir, capsys):
    """
    Make these tests stand-alone
    Test batch_command with dryrun True and quiet True.
    """
    pytest.fail("Make {} tests stand-alone".format(__file__))
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        U.writefile('tmpfile',
                    [str(x) + '\n' for x in range(1, 250)])

        v = optparse.Values({'dryrun': True, 'quiet': True,
                             'xargs': True, 'cmd': 'echo %'})
        with open('tmpfile', 'r') as f:
            q = fx.xargs_wrap("echo %", f)
        exp = ''
        for chunk in q:
            exp += re.sub('^echo ', "would do 'echo ", chunk) + "'\n"
        with th.StdoutExcursion() as getval:
            with open('tmpfile', 'r') as f:
                fx.batch_command(v, [], f)
            actual = getval()

        assert exp == actual

# ---------------------------------------------------------------------------

# -----------------------------------------------------------------------------
def test_batch_command_dryrun(tmpdir):
    """
    Test batch_command with dryrun True and quiet False.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        U.writefile('tmpfile',
                    [str(x) + '\n' for x in range(1, 250)])
        v = optparse.Values({'dryrun': True, 'quiet': False, 'xargs': True,
                             'cmd': 'echo %'})
        with open('tmpfile', 'r') as f:
            q = fx.xargs_wrap("echo %", f)
        exp = ''
        for chunk in q:
            exp += re.sub('^echo ', "would do 'echo ", chunk) + "'\n"

        with th.StdoutExcursion() as getval:
            with open('tmpfile', 'r') as f:
                fx.batch_command(v, [], f)
            actual = getval()

        assert exp == actual


# -----------------------------------------------------------------------------
def test_batch_command_neither(tmpdir):
    """
    Test batch_command with dryrun and quiet both False.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        U.writefile('tmpfile',
                    [str(x) + '\n' for x in range(1, 250)])
        v = optparse.Values({'dryrun': False, 'quiet': False,
                             'xargs': True, 'cmd': 'echo %'})
        with open('tmpfile', 'r') as f:
            q = fx.xargs_wrap("echo %", f)
        exp = ''
        for chunk in q:
            exp += chunk + '\n'
            exp += re.sub('^echo ', '', chunk) + '\n'

        with th.StdoutExcursion() as getval:
            with open('tmpfile', 'r') as f:
                fx.batch_command(v, [], f)
            actual = getval()

        assert exp == actual


# -----------------------------------------------------------------------------
def test_batch_command_quiet(tmpdir):
    """
    Test batch_command with dryrun False and quiet True.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        U.writefile('tmpfile',
                    [str(x) + '\n' for x in range(1, 250)])
        v = optparse.Values({'dryrun': False, 'quiet': True, 'xargs': True,
                             'cmd': 'echo %'})

        with open('tmpfile', 'r') as f:
            q = fx.xargs_wrap("echo %", f)
        exp = ''
        for chunk in q:
            exp += re.sub('^echo ', '', chunk) + '\n'

        with th.StdoutExcursion() as getval:
            with open('tmpfile', 'r') as f:
                fx.batch_command(v, [], f)
            actual = getval()

        assert exp == actual


# -----------------------------------------------------------------------------
def test_fx_help():
    """
    Verify that 'fx --help' does the right thing
    """
    pytest.debug_func()
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
             "-n, --dry-run         dryrun or execute",
             "-q, --quiet           don't echo commands, just run them",
             "-x, --xargs           batch input from stdin into command" +
             " lines like xargs",
             ]
    script = U.script_location("fx")
    result = pexpect.run("%s --help" % script)
    for exp_s in exp_l:
        assert exp_s in result


# -----------------------------------------------------------------------------
def test_iterate_command_both(tmpdir):
    """
    Test iterate_command() with dryrun True and quiet True.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': True,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

        with th.StdoutExcursion() as getval:
            fx.iterate_command(v, [])
            actual = getval()

        assert exp == actual


# -----------------------------------------------------------------------------
def test_iterate_command_dryrun(tmpdir):
    """
    Test iterate_command() with dryrun True and quiet False.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': False,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

        with th.StdoutExcursion() as getval:
            fx.iterate_command(v, [])
            actual = getval()

        assert exp == actual


# -----------------------------------------------------------------------------
def test_iterate_command_neither(tmpdir):
    """
    Test iterate_command() with dryrun False and quiet False.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': False,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["echo %d\n%d\n" % (i, i) for i in range(5, 10)])

        with th.StdoutExcursion() as getval:
            fx.iterate_command(v, [])
            actual = getval()
        assert exp == actual


# -----------------------------------------------------------------------------
def test_iterate_command_quiet(tmpdir):
    """
    Test iterate_command() with dryrun False and quiet True.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': True,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["%d\n" % i for i in range(5, 10)])

        with th.StdoutExcursion() as getval:
            fx.iterate_command(v, [])
            actual = getval()
        assert exp == actual


# -----------------------------------------------------------------------------
def test_psys_both():
    """
    Test routine psys with dryrun True and quiet True.
    """
    with th.StdoutExcursion() as getval:
        v = optparse.Values({'dryrun': True, 'quiet': True})
        fx.psys('ls -d fx.py', v)
        actual = getval()
    expected = "would do 'ls -d fx.py'\n"
    assert(expected == actual)


# -----------------------------------------------------------------------------
def test_psys_dryrun():
    """
    Test routine psys with dryrun True and quiet False.
    """
    with th.StdoutExcursion() as getval:
        v = optparse.Values({'dryrun': True, 'quiet': False})
        fx.psys('ls -d nosuchfile', v)
        actual = getval()
    expected = "would do 'ls -d nosuchfile'\n"
    # self.assertEq(expected, actual)
    assert expected == actual


# -----------------------------------------------------------------------------
def test_psys_neither():
    """
    Test routine psys with dryrun False and quiet False.
    """
    root = U.findroot()
    with th.StdoutExcursion() as getval:
        v = optparse.Values({'dryrun': False, 'quiet': False})
        fx.psys('ls -d %s/fx.py' % root, v)
        actual = getval()
    expected = "ls -d %s/fx.py\n%s/fx.py\n" % (root, root)
    # self.assertEq(expected, actual)
    assert expected == actual


# -----------------------------------------------------------------------------
def test_psys_quiet(tmpdir, capsys, data):
    """
    Test routine psys with dryrun False and quiet True.
    """
    with U.Chdir(tmpdir.strpath):
        exp = "a.xyzzy\nb.xyzzy\nc.xyzzy\ntmpfile\n"
        v = optparse.Values({'dryrun': False, 'quiet': True})
        fx.psys('ls', v)
        actual, _ = capsys.readouterr()
        assert exp == actual


# -----------------------------------------------------------------------------
def test_subst_command_both(tmpdir):
    """
    Test subst_command() with dryrun True and quiet True.
    """
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': True, 'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(["would do 'ls %s'\n" % x for x in a])
        U.safe_unlink(a)

        with th.StdoutExcursion() as getval:
            fx.subst_command(v, a)
            actual = getval()

        assert exp == actual


# -----------------------------------------------------------------------
def test_subst_command_dryrun(tmpdir):
    """
    Test subst_command() with dryrun True and quiet False.
    """
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': False,
                             'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(["would do 'ls %s'\n" % x for x in a])
        U.safe_unlink(a)

        with th.StdoutExcursion() as getval:
            fx.subst_command(v, a)
            actual = getval()

        assert exp == actual


# -----------------------------------------------------------------------------
def test_subst_command_neither(tmpdir):
    """
    Test subst_command() with dryrun False and quiet False.
    """
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': False,
                             'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(['ls %s\n%s\n' % (x, x) for x in a])
        U.touch(a)

        with th.StdoutExcursion() as getval:
            fx.subst_command(v, a)
            actual = getval()

        assert exp == actual


# -----------------------------------------------------------------------------
def test_subst_command_quiet(tmpdir):
    """
    Test subst_command() with dryrun False and quiet True.
    """
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': True,
                             'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(['%s\n' % x for x in a])
        U.touch(a)

        with th.StdoutExcursion() as getval:
            fx.subst_command(v, a)
            actual = getval()

        assert exp == actual


# -----------------------------------------------------------------------------
def test_subst_rename_both(tmpdir):
    """
    Test subst_rename() with dryrun True and quiet True.
    """
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        v = optparse.Values({'dryrun': True, 'quiet': True,
                             'edit': 's/.pl/.xyzzy'})

        with th.StdoutExcursion() as getval:
            fx.subst_rename(v, arglist)
            actual = getval()
        assert expected == actual

        q = glob.glob('*.pl')
        q.sort()
        assert q == arglist


# -----------------------------------------------------------------------------
def test_subst_rename_dryrun(tmpdir):
    """
    Test subst_rename() with dryrun True and quiet False.
    """
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        v = optparse.Values({'dryrun': True, 'quiet': False,
                             'edit': 's/.pl/.xyzzy'})

        with th.StdoutExcursion() as getval:
            fx.subst_rename(v, arglist)
            actual = getval()
        assert expected == actual

        q = glob.glob('*.pl')
        q.sort()
        assert q == arglist


# -----------------------------------------------------------------------------
def test_subst_rename_neither(tmpdir):
    """
    Test subst_rename() with dryrun False and quiet False.
    """
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = optparse.Values({'dryrun': False, 'quiet': False,
                             'edit': 's/.pl/.xyzzy'})

        with th.StdoutExcursion() as getval:
            fx.subst_rename(v, arglist)
            actual = getval()

        assert expected == actual
        q = glob.glob('*.xyzzy')
        q.sort()
        assert exp == q


# -----------------------------------------------------------------------------
def test_subst_rename_quiet(tmpdir):
    """
    Test subst_rename() with dryrun False and quiet True.
    """
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = optparse.Values({'dryrun': False, 'quiet': True,
                             'edit': 's/.pl/.xyzzy'})

        with th.StdoutExcursion() as getval:
            fx.subst_rename(v, arglist)
            actual = getval()
        assert expected == actual

        q = glob.glob('*.pl')
        q.sort()
        assert [] == q

        q = glob.glob('*.xyzzy')
        q.sort()
        assert exp == q


# -----------------------------------------------------------------------------
def test_usage():
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
    actual = fx.usage()
    assert exp == actual


# ---------------------------------------------------------------------------
@pytest.fixture
def data(tmpdir, request):
    """
    set up some data
    """
    if request.function.func_name == "test_psys_quiet":
        for stem in ['a.xyzzy', 'b.xyzzy', 'c.xyzzy', 'tmpfile']:
            path = tmpdir.join(stem)
            path.ensure()


# ---------------------------------------------------------------------------
class TestFx(th.HelpedTestCase):
    """
    Tests for code in fx.py.
    """
    testdir = "/tmp/fx_test"

    # -----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """
        Create test directory if necessary
        """
        if not os.path.exists(TestFx.testdir):
            os.mkdir(TestFx.testdir)

    # -----------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        """
        Clean up after tests if appropriate (KEEPFILES not set)
        """
        kf = os.getenv("KEEPFILES")
        if kf is None or not int(kf):
            shutil.rmtree(TestFx.testdir)

    # -----------------------------------------------------------------------
    def test_batch_command_both(self):
        """
        Test batch_command with dryrun True and quiet True.
        """
        with U.Chdir(self.testdir):
            U.writefile('tmpfile',
                        [str(x) + '\n' for x in range(1, 250)])

            v = optparse.Values({'dryrun': True, 'quiet': True,
                                 'xargs': True, 'cmd': 'echo %'})
            with open('tmpfile', 'r') as f:
                q = fx.xargs_wrap("echo %", f)
            exp = ''
            for chunk in q:
                exp += re.sub('^echo ', "would do 'echo ", chunk) + "'\n"
            with th.StdoutExcursion() as getval:
                with open('tmpfile', 'r') as f:
                    fx.batch_command(v, [], f)
                actual = getval()

            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_batch_command_dryrun(self):
        """
        Test batch_command with dryrun True and quiet False.
        """
        with U.Chdir(self.testdir):
            U.writefile('tmpfile',
                        [str(x) + '\n' for x in range(1, 250)])
            v = optparse.Values({'dryrun': True, 'quiet': False, 'xargs': True,
                                 'cmd': 'echo %'})
            with open('tmpfile', 'r') as f:
                q = fx.xargs_wrap("echo %", f)
            exp = ''
            for chunk in q:
                exp += re.sub('^echo ', "would do 'echo ", chunk) + "'\n"

            with th.StdoutExcursion() as getval:
                with open('tmpfile', 'r') as f:
                    fx.batch_command(v, [], f)
                actual = getval()

            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_batch_command_neither(self):
        """
        Test batch_command with dryrun and quiet both False.
        """
        with U.Chdir(self.testdir):
            U.writefile('tmpfile',
                        [str(x) + '\n' for x in range(1, 250)])
            v = optparse.Values({'dryrun': False, 'quiet': False,
                                 'xargs': True, 'cmd': 'echo %'})
            with open('tmpfile', 'r') as f:
                q = fx.xargs_wrap("echo %", f)
            exp = ''
            for chunk in q:
                exp += chunk + '\n'
                exp += re.sub('^echo ', '', chunk) + '\n'

            with th.StdoutExcursion() as getval:
                with open('tmpfile', 'r') as f:
                    fx.batch_command(v, [], f)
                actual = getval()

            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_batch_command_quiet(self):
        """
        Test batch_command with dryrun False and quiet True.
        """
        with U.Chdir(self.testdir):
            U.writefile('tmpfile',
                        [str(x) + '\n' for x in range(1, 250)])
            v = optparse.Values({'dryrun': False, 'quiet': True, 'xargs': True,
                                 'cmd': 'echo %'})

            with open('tmpfile', 'r') as f:
                q = fx.xargs_wrap("echo %", f)
            exp = ''
            for chunk in q:
                # exp += chunk + '\n'
                exp += re.sub('^echo ', '', chunk) + '\n'

            with th.StdoutExcursion() as getval:
                with open('tmpfile', 'r') as f:
                    fx.batch_command(v, [], f)
                actual = getval()

            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_iterate_command_both(self):
        """
        Test iterate_command() with dryrun True and quiet True.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': True, 'quiet': True,
                                 'cmd': 'echo %',
                                 'irange': '5:10'})
            exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

            with th.StdoutExcursion() as getval:
                fx.iterate_command(v, [])
                actual = getval()

            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_iterate_command_dryrun(self):
        """
        Test iterate_command() with dryrun True and quiet False.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': True, 'quiet': False,
                                 'cmd': 'echo %',
                                 'irange': '5:10'})
            exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

            with th.StdoutExcursion() as getval:
                fx.iterate_command(v, [])
                actual = getval()

            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_iterate_command_neither(self):
        """
        Test iterate_command() with dryrun False and quiet False.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': False, 'quiet': False,
                                 'cmd': 'echo %',
                                 'irange': '5:10'})
            exp = "".join(["echo %d\n%d\n" % (i, i) for i in range(5, 10)])

            with th.StdoutExcursion() as getval:
                fx.iterate_command(v, [])
                actual = getval()
            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_iterate_command_quiet(self):
        """
        Test iterate_command() with dryrun False and quiet True.
        """
        # pdb.set_trace()
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': False, 'quiet': True,
                                 'cmd': 'echo %',
                                 'irange': '5:10'})
            exp = "".join(["%d\n" % i for i in range(5, 10)])

            with th.StdoutExcursion() as getval:
                fx.iterate_command(v, [])
                actual = getval()
            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_subst_command_both(self):
        """
        Test subst_command() with dryrun True and quiet True.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': True, 'quiet': True, 'cmd': 'ls %'})
            a = ['a.pl', 'b.pl', 'c.pl']
            exp = "".join(["would do 'ls %s'\n" % x for x in a])
            U.safe_unlink(a)

            with th.StdoutExcursion() as getval:
                fx.subst_command(v, a)
                actual = getval()

            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_subst_command_dryrun(self):
        """
        Test subst_command() with dryrun True and quiet False.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': True, 'quiet': False,
                                 'cmd': 'ls %'})
            a = ['a.pl', 'b.pl', 'c.pl']
            exp = "".join(["would do 'ls %s'\n" % x for x in a])
            U.safe_unlink(a)

            with th.StdoutExcursion() as getval:
                fx.subst_command(v, a)
                actual = getval()

            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_subst_command_neither(self):
        """
        Test subst_command() with dryrun False and quiet False.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': False, 'quiet': False,
                                 'cmd': 'ls %'})
            a = ['a.pl', 'b.pl', 'c.pl']
            exp = "".join(['ls %s\n%s\n' % (x, x) for x in a])
            U.touch(a)

            with th.StdoutExcursion() as getval:
                fx.subst_command(v, a)
                actual = getval()

            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_subst_command_quiet(self):
        """
        Test subst_command() with dryrun False and quiet True.
        """
        with U.Chdir(self.testdir):
            v = optparse.Values({'dryrun': False, 'quiet': True,
                                 'cmd': 'ls %'})
            a = ['a.pl', 'b.pl', 'c.pl']
            exp = "".join(['%s\n' % x for x in a])
            U.touch(a)

            with th.StdoutExcursion() as getval:
                fx.subst_command(v, a)
                actual = getval()

            self.assertEq(exp, actual)

    # -----------------------------------------------------------------------
    def test_subst_rename_both(self):
        """
        Test subst_rename() with dryrun True and quiet True.
        """
        with U.Chdir(self.testdir):
            arglist = ['a.pl', 'b.pl', 'c.pl']
            for a in arglist:
                U.touch(a)
            expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                                [q.replace('.pl', '') for q in arglist]])
            v = optparse.Values({'dryrun': True, 'quiet': True,
                                 'edit': 's/.pl/.xyzzy'})

            with th.StdoutExcursion() as getval:
                fx.subst_rename(v, arglist)
                actual = getval()

            self.assertEq(expected, actual)

            q = glob.glob('*.pl')
            q.sort()
            self.assertEq(q, arglist)

    # -----------------------------------------------------------------------
    def test_subst_rename_dryrun(self):
        """
        Test subst_rename() with dryrun True and quiet False.
        """
        with U.Chdir(self.testdir):
            arglist = ['a.pl', 'b.pl', 'c.pl']
            for a in arglist:
                U.touch(a)
            expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                                [q.replace('.pl', '') for q in arglist]])
            v = optparse.Values({'dryrun': True, 'quiet': False,
                                 'edit': 's/.pl/.xyzzy'})

            with th.StdoutExcursion() as getval:
                fx.subst_rename(v, arglist)
                actual = getval()

            self.assertEq(expected, actual)

            q = glob.glob('*.pl')
            q.sort()
            self.assertEq(q, arglist)

    # -----------------------------------------------------------------------
    def test_subst_rename_neither(self):
        """
        Test subst_rename() with dryrun False and quiet False.
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

            with th.StdoutExcursion() as getval:
                fx.subst_rename(v, arglist)
                actual = getval()

            self.assertEq(expected, actual)

            q = glob.glob('*.xyzzy')
            q.sort()
            self.assertEq(exp, q)

    # -----------------------------------------------------------------------
    def test_subst_rename_quiet(self):
        """
        Test subst_rename() with dryrun False and quiet True.
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

            with th.StdoutExcursion() as getval:
                fx.subst_rename(v, arglist)
                actual = getval()

            self.assertEq(expected, actual)

            q = glob.glob('*.pl')
            q.sort()
            self.assertEq([], q)

            q = glob.glob('*.xyzzy')
            q.sort()
            self.assertEq(exp, q)

    # -----------------------------------------------------------------------
    def test_psys_neither(self):
        """
        Test routine psys with dryrun False and quiet False.
        """
        root = U.findroot()
        with th.StdoutExcursion() as getval:
            v = optparse.Values({'dryrun': False, 'quiet': False})
            fx.psys('ls -d %s/fx.py' % root, v)
            actual = getval()
        expected = "ls -d %s/fx.py\n%s/fx.py\n" % (root, root)
        self.assertEq(expected, actual)

    # -----------------------------------------------------------------------
    def test_psys_dryrun(self):
        """
        Test routine psys with dryrun True and quiet False.
        """
        with th.StdoutExcursion() as getval:
            v = optparse.Values({'dryrun': True, 'quiet': False})
            fx.psys('ls -d nosuchfile', v)
            actual = getval()
        expected = "would do 'ls -d nosuchfile'\n"
        self.assertEq(expected, actual)

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
        actual = fx.usage()
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
                 "-n, --dry-run         dryrun or execute",
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

from bscr import fx
from bscr import util as U
import glob
import re
import optparse
import pexpect

import pytest


# -----------------------------------------------------------------------------
def test_batch_command_both(tmpdir, capsys):
    """
    Test batch_command with dryrun True and quiet True.
    """
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
        with open("tmpfile", "r") as f:
            fx.batch_command(v, [], f)
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_batch_command_dryrun(tmpdir, capsys):
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

        with open("tmpfile", 'r') as f:
            fx.batch_command(v, [], f)
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_batch_command_neither(tmpdir, capsys):
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

        with open('tmpfile', 'r') as f:
            fx.batch_command(v, [], f)
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_batch_command_quiet(tmpdir, capsys):
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

        with open('tmpfile', 'r') as f:
            fx.batch_command(v, [], f)
        assert exp in "".join(capsys.readouterr())


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
def test_iterate_command_both(tmpdir, capsys):
    """
    Test iterate_command() with dryrun True and quiet True.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': True,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_iterate_command_dryrun(tmpdir, capsys):
    """
    Test iterate_command() with dryrun True and quiet False.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': False,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_iterate_command_neither(tmpdir, capsys):
    """
    Test iterate_command() with dryrun False and quiet False.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': False,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["echo %d\n%d\n" % (i, i) for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_iterate_command_quiet(tmpdir, capsys):
    """
    Test iterate_command() with dryrun False and quiet True.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': True,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["%d\n" % i for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_both(capsys):
    """
    Test routine psys with dryrun True and quiet True.
    """
    pytest.debug_func()
    v = optparse.Values({'dryrun': True, 'quiet': True})
    expected = "would do 'ls -d fx.py'\n"
    fx.psys('ls -d fx.py', v)
    assert expected in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_dryrun(capsys):
    """
    Test routine psys with dryrun True and quiet False.
    """
    pytest.debug_func()
    v = optparse.Values({'dryrun': True, 'quiet': False})
    expected = "would do 'ls -d nosuchfile'\n"
    fx.psys('ls -d nosuchfile', v)
    assert expected in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_neither(capsys):
    """
    Test routine psys with dryrun False and quiet False.
    """
    pytest.debug_func()
    root = U.findroot()
    v = optparse.Values({'dryrun': False, 'quiet': False})
    expected = "ls -d %s/fx.py\n%s/fx.py\n" % (root, root)
    fx.psys('ls -d %s/fx.py' % root, v)
    assert expected in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_quiet(tmpdir, capsys, data):
    """
    Test routine psys with dryrun False and quiet True.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        exp = "a.xyzzy\nb.xyzzy\nc.xyzzy\ntmpfile\n"
        v = optparse.Values({'dryrun': False, 'quiet': True})
        fx.psys('ls', v)
        assert exp == "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_command_both(tmpdir, capsys):
    """
    Test subst_command() with dryrun True and quiet True.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': True, 'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(["would do 'ls %s'\n" % x for x in a])
        U.safe_unlink(a)

        fx.subst_command(v, a)
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------
def test_subst_command_dryrun(tmpdir, capsys):
    """
    Test subst_command() with dryrun True and quiet False.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': False,
                             'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(["would do 'ls %s'\n" % x for x in a])
        U.safe_unlink(a)

        fx.subst_command(v, a)
        assert exp in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_command_neither(tmpdir, capsys):
    """
    Test subst_command() with dryrun False and quiet False.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': False,
                             'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(['ls %s\n%s\n' % (x, x) for x in a])
        U.touch(a)

        fx.subst_command(v, a)
        assert exp in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_command_quiet(tmpdir, capsys):
    """
    Test subst_command() with dryrun False and quiet True.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': True,
                             'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(['%s\n' % x for x in a])
        U.touch(a)

        fx.subst_command(v, a)
        assert exp in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_rename_both(tmpdir, capsys):
    """
    Test subst_rename() with dryrun True and quiet True.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        v = optparse.Values({'dryrun': True, 'quiet': True,
                             'edit': 's/.pl/.xyzzy'})

        fx.subst_rename(v, arglist)
        assert expected in " ".join(capsys.readouterr())

        q = glob.glob('*.pl')
        q.sort()
        assert q == arglist


# -----------------------------------------------------------------------------
def test_subst_rename_dryrun(tmpdir, capsys):
    """
    Test subst_rename() with dryrun True and quiet False.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        v = optparse.Values({'dryrun': True, 'quiet': False,
                             'edit': 's/.pl/.xyzzy'})

        fx.subst_rename(v, arglist)
        assert expected in " ".join(capsys.readouterr())

        q = glob.glob('*.pl')
        q.sort()
        assert q == arglist


# -----------------------------------------------------------------------------
def test_subst_rename_neither(tmpdir, capsys):
    """
    Test subst_rename() with dryrun False and quiet False.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = optparse.Values({'dryrun': False, 'quiet': False,
                             'edit': 's/.pl/.xyzzy'})

        fx.subst_rename(v, arglist)
        assert expected in " ".join(capsys.readouterr())

        q = glob.glob('*.xyzzy')
        q.sort()
        assert exp == q


# -----------------------------------------------------------------------------
def test_subst_rename_quiet(tmpdir, capsys):
    """
    Test subst_rename() with dryrun False and quiet True.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = optparse.Values({'dryrun': False, 'quiet': True,
                             'edit': 's/.pl/.xyzzy'})

        fx.subst_rename(v, arglist)
        assert expected in " ".join(capsys.readouterr())

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
    pytest.debug_func()
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

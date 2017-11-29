import bscr
from bscr import util as U
import os
import pytest
import re
import stat
import time


# -----------------------------------------------------------------------------
def test_chdir(tmpdir):
    """
    Test util.Chdir()
    """
    pytest.debug_func()
    pre = os.getcwd()
    with U.Chdir(tmpdir.strpath):
        inter = os.getcwd()
        assert tmpdir.strpath == inter
    post = os.getcwd()
    assert pre == post
    assert inter != pre


# -----------------------------------------------------------------------------
def test_cmdline_attr(fx_arg_specified):
    """
    Verify the cmdline class has the expected attributes
    """
    pytest.debug_func()
    c = U.cmdline(fx_arg_specified)
    assert hasattr(c, 'p')


# -----------------------------------------------------------------------------
def test_cmdline_default_action(fx_arg_defaulted):
    """
    With default_action set to 'store_true' in the cmdline constructor,
    unspecified values in the command line should be set to True (e.g.,
    o.forward)
    """
    pytest.debug_func()
    c = U.cmdline(fx_arg_defaulted, default_action='store_true')
    try:
        (o, a) = c.parse(['cmd',
                          '--second', 'carniverous',
                          '--third',
                          '--Fourth',
                          ])
    except SystemExit:
        pass

    assert o.first is False
    assert o.second == ['carniverous']
    assert o.third is True
    assert o.forward is True


# -----------------------------------------------------------------------------
def test_cmdline_default_default(fx_arg_defaulted):
    """
    If no default is specified in the cmdline constructor, the default default
    to be used is None
    """
    pytest.debug_func()
    c = U.cmdline(fx_arg_defaulted)
    try:
        (o, a) = c.parse("cmd --first angular --second carniverous".split())
    except SystemExit:
        pass
    assert o.first == 'angular'
    assert o.second == ['carniverous']
    assert o.third is False
    assert o.forward is None


# -----------------------------------------------------------------------------
def test_cmdline_default_type(fx_arg_defaulted):
    """
    Verify default type set by the cmdline class
    """
    pytest.debug_func()

    c = U.cmdline(fx_arg_defaulted, default_type=float)
    try:
        (o, a) = c.parse('cmd --first 7.3 --second 9.452'.split())
    except SystemExit:
        pass

    assert o.first == 7.3
    assert o.second == [9.452]
    assert o.third is False
    assert o.forward is None


# -----------------------------------------------------------------------------
def test_cmdline_defaults(fx_arg_defaulted):
    """
    Verify defaults set by the cmdline class
    """
    pytest.debug_func()
    c = U.cmdline(fx_arg_defaulted)
    try:
        (o, a) = c.parse("cmd --first optarg --second two".split())
    except SystemExit:
        pass
    assert o.first == 'optarg'
    assert o.second == ['two']
    assert o.third is False
    assert o.forward is None


# -----------------------------------------------------------------------------
def test_cmdline_help(capsys, fx_arg_specified):
    """
    Check '-h' option passed to cmdline generates the expected help message
    """
    pytest.debug_func()
    c = U.cmdline(fx_arg_specified)
    try:
        c.parse(['cmd', '-h'])
    except SystemExit:
        pass
    o, e = capsys.readouterr()
    assert 'Usage:' in o
    assert '-h, --help     show this help message and exit' in o
    assert '-t, --test     help string' in o
    assert '-s, --special  help string' in o
    assert '-d, --debug    run under the debugger' in o


# -----------------------------------------------------------------------------
def test_cmdline_long_opts(fx_arg_specified):
    """
    Check how cmdline handles long options
    """
    pytest.debug_func()
    c = U.cmdline(fx_arg_specified)
    assert '--debug' in c.p._long_opt
    assert '--test' in c.p._long_opt
    assert '--special' in c.p._long_opt


# -----------------------------------------------------------------------------
def test_cmdline_parse(fx_arg_specified):
    """
    Check the cmdline parses the command line correctly
    """
    pytest.debug_func()
    c = U.cmdline(fx_arg_specified)

    (o, a) = c.parse("cmd -t --special".split())
    assert o.fribble is True
    assert o.special is True
    assert o.debug is False

    (o, a) = c.parse("cmd --test".split())
    assert o.fribble is True
    assert o.special is False
    assert o.debug is False

    (o, a) = c.parse("cmd -s".split())
    assert o.fribble is False
    assert o.special is True
    assert o.debug is False

    (o, a) = c.parse("cmd".split())
    assert o.fribble is False
    assert o.special is False
    assert o.debug is False


# -----------------------------------------------------------------------------
def test_cmdline_usage(capsys, fx_arg_specified):
    """
    Check that cmdline class puts out the correct usage message
    """
    pytest.debug_func()
    c = U.cmdline(fx_arg_specified, usage="This is a usage test message")
    try:
        c.parse(['cmd', '-h'])
    except SystemExit:
        pass
    o, e = capsys.readouterr()
    assert 'Usage:' in o
    assert 'This is a usage test message' in o
    assert '-h, --help     show this help message and exit' in o
    assert '-t, --test     help string' in o
    assert '-s, --special  help string' in o
    assert '-d, --debug    run under the debugger' in o


# -----------------------------------------------------------------------------
def test_contents_empty(tmpdir):
    """
    Calling contents() on an empty file should return an empty list
    """
    pytest.debug_func()
    empty = tmpdir.join("empty_file")
    empty.ensure()
    z = U.contents(empty.strpath)
    assert z == []


# -----------------------------------------------------------------------------
def test_contents_something(tmpdir):
    """
    Calling contents() on a non-empty file should return a list of lines from
    the file with newlines removed
    """
    pytest.debug_func()
    testdata = ["line 1", "line 2", "line 3"]
    something = tmpdir.join("something")
    something.write("\n".join(testdata + [""]))
    z = U.contents(something.strpath)
    assert testdata == z


# -----------------------------------------------------------------------------
def test_expand():
    """
    Test using expand to instantiate environment variables and ~user
    """
    pytest.debug_func()
    home = os.environ["HOME"]
    logname = os.environ["LOGNAME"]
    term = os.environ["TERM"]
    os.environ["UPATH"] = "~/prj/github"

    assert U.expand("$HOME") == home
    assert U.expand("~") == home
    assert U.expand("~{}".format(logname)) == home
    assert U.expand("### $TERM ###") == "### {} ###".format(term)
    assert U.expand("$UPATH") == "{}/prj/github".format(home)


# -----------------------------------------------------------------------------
def test_function_name():
    """
    Routine function_name() should return the name of its caller
    """
    pytest.debug_func()
    assert U.function_name() == "test_function_name"


# -----------------------------------------------------------------------------
def test_in_bscr_repo(tmpdir):
    """
    When cwd is in the bscr repo, U.in_bscr_repo() should return True.
    Otherwise, it should return False
    """
    pytest.debug_func()
    assert U.in_bscr_repo()
    with U.Chdir(tmpdir.strpath):
        assert not U.in_bscr_repo()
    assert U.in_bscr_repo()


# -----------------------------------------------------------------------------
def test_git_describe():
    """
    Test running git_describe and grabbing its output
    """
    pytest.debug_func()
    gdesc = U.git_describe()
    if "No names found" in gdesc:
        pytest.skip(gdesc)
    if not U.in_bscr_repo():
        pytest.skip("not in backscratcher repo")
    assert re.findall("\d{4}\.\d{4}\w*", gdesc)


# -----------------------------------------------------------------------------
def test_lquote():
    """
    Routine lquote() is supposed to wrap its input in triple quotes with
    newlines
    """
    pytest.debug_func()
    testdata = "The quick brown fox jumps over the lazy dog"
    assert '"""\n{}\n"""'.format(testdata) == U.lquote(testdata)


# -----------------------------------------------------------------------------
def test_touch_list(tmpdir):
    """
    Routine touch() should create the file if it does not exist and update its
    atime and mtime if it does. It takes a string or list.
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        now = int(time.time())
        flist = [tmpdir.join(x) for x in ["jabberwocky",
                                          "philodendron",
                                          "mcguffin"]]
        U.touch([x.strpath for x in flist])
        for fn in flist:
            assert fn.exists()
            s = os.stat(fn.strpath)
            assert now == s[stat.ST_ATIME]
            assert now == s[stat.ST_MTIME]


# -----------------------------------------------------------------------------
def test_touch_list_times(tmpdir):
    """
    Routine touch() should create the file if it does not exist and update its
    atime and mtime if it does. It takes a string or list. It also takes an
    optional second argument containing a tuple with the atime and mtime we
    want to set on the target file(s)
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        now = int(time.time())
        tt = (now+3, now-4)
        flist = [tmpdir.join(x) for x in ["jabberwocky",
                                          "philodendron",
                                          "mcguffin"]]
        U.touch([x.strpath for x in flist], tt)
        for fn in flist:
            assert fn.exists()
            s = os.stat(fn.strpath)
            assert tt[0] == s[stat.ST_ATIME]
            assert tt[1] == s[stat.ST_MTIME]


# -----------------------------------------------------------------------------
def test_touch_nlns():
    """
    Calling touch() with an argument that is not a list or a string should
    get an exception
    """
    pytest.debug_func()
    with pytest.raises(bscr.Error) as err:
        U.touch(17)
    assert "argument must be list or string" in str(err)


# -----------------------------------------------------------------------------
def test_touch_str(tmpdir):
    """
    Calling touch() with a string, setting the current time
    """
    pytest.debug_func()
    filename = tmpdir.join("pines")
    U.touch(filename.strpath)
    now = int(time.time())
    assert filename.exists()
    s = filename.stat()
    assert now == s.atime
    assert now == s.mtime


# -----------------------------------------------------------------------------
def test_touch_str_times(tmpdir):
    """
    Calling touch() with a string, setting some other time
    """
    pytest.debug_func()
    now = int(time.time())
    tt = (now-17, now+42)
    filename = tmpdir.join("pines")
    U.touch(filename.strpath, tt)
    assert filename.exists()
    s = filename.stat()
    assert tt[0] == s.atime
    assert tt[1] == s.mtime


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_arg_specified():
    """
    Example argument structure for testing U.cmdline(), specify everything
    """
    clargs = [{'opts': ['-t', '--test'],
               'action': 'store_true',
               'default': False,
               'dest': 'fribble',
               'help': 'help string'
               },
              {'opts': ['-s', '--special'],
               'action': 'store_true',
               'default': False,
               'dest': 'special',
               'help': 'help string'
               }
              ]
    return clargs


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_arg_defaulted():
    """
    Example argument structure for testing U.cmdline(), take lots of defaults
    """
    clargs = [{'name': 'first',
               'help': 'first option'},
              {'name': 'second',
               'action': 'append',
               'help': 'second option'},
              {'name': 'third',
               'default': False,
               'help': 'third option'},
              {'name': 'Fourth',
               'dest': 'forward',
               'help': 'fourth option'},
              ]
    return clargs

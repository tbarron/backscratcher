import bscr
from bscr import testhelp as th
from bscr import util as U
import os
import pytest
import re
import shutil
import stat
import time


# -----------------------------------------------------------------------------
def test_standalone():
    """
    Make these tests stand-alone
    """
    pytest.fail("Make {} tests stand-alone".format(__file__))


# -----------------------------------------------------------------------------
def cmdline_arg_list():
    """
    Example argument structure for U.cmdline()
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
def simple_arg_list():
    """
    Argument list assuming defaults
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


# -----------------------------------------------------------------------------
def test_cmdline_help(capsys):
    """
    Test the cmdline class for command line parsing
    """
    pytest.debug_func()
    c = U.cmdline(cmdline_arg_list())
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
def test_cmdline_usage(capsys):
    """
    Test the cmdline class for command line parsing
    """
    pytest.debug_func()
    c = U.cmdline(cmdline_arg_list(), usage="This is a usage test message")
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


# ---------------------------------------------------------------------------
class TestUtilCmdline(th.HelpedTestCase):
    clargs = cmdline_arg_list()

    # -----------------------------------------------------------------------
    def test_cmdline_attr(self):
        """
        Test the cmdline class for command line parsing
        """
        self.dbgfunc()
        c = U.cmdline(self.clargs)

        self.assertTrue(hasattr(c, 'p'),
                        "Expected attribute 'p' on cmdline object")

    # -------------------------------------------------------------------------
    def test_cmdline_defaults(self):
        """
        Have the cmdline class set defaults for us

            Attribute       Default       Override Argument
                action          'store'       default_action
                default         None          default_default
                dest            name          default_dest
                type            string        default_type

        So, for example, the default action is 'store', but you can override
        this by passing, say, default_action='store_true' to the cmdline
        constructor.

        You can also specify the action for a specific option in the dict
        defining that option.
        """
        pytest.debug_func()
        c = U.cmdline(simple_arg_list())
        try:
            (o, a) = c.parse(['cmd',
                              '--first', 'optarg',
                              '--second', 'two',
                              ])
        except SystemExit:
            pass

        assert o.first == 'optarg'
        assert o.second == ['two']
        assert o.third is False
        assert o.forward is None

    # -------------------------------------------------------------------------
    def test_cmdline_default_action(self):
        """
        Have the cmdline class set defaults for us

            Attribute       Default       Override Argument
                action          'store'       default_action
                default         None          default_default
                dest            name          default_dest
                type            string        default_type

        So, for example, the default action is 'store', but you can override
        this by passing, say, default_action='store_true' to the cmdline
        constructor.

        You can also specify the action for a specific option in the dict
        defining that option.
        """
        pytest.debug_func()
        c = U.cmdline(simple_arg_list(),
                      default_action='store_true')
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

    # -------------------------------------------------------------------------
    def test_cmdline_default_default(self):
        """
        Have the cmdline class set defaults for us

            Attribute       Default       Override Argument
                action          'store'       default_action
                default         None          default_default
                dest            name          default_dest
                type            string        default_type

        So, for example, the default action is 'store', but you can override
        this by passing, say, default_action='store_true' to the cmdline
        constructor.

        You can also specify the action for a specific option in the dict
        defining that option.
        """
        pytest.debug_func()
        c = U.cmdline(simple_arg_list())
        try:
            (o, a) = c.parse(['cmd',
                              '--first', 'angular',
                              '--second', 'carniverous',
                              ])
        except SystemExit:
            pass

        assert o.first == 'angular'
        assert o.second == ['carniverous']
        assert o.third is False
        assert o.forward is None

    # -------------------------------------------------------------------------
    def test_cmdline_default_type(self):
        """
        Have the cmdline class set defaults for us

            Attribute       Default       Override Argument
                action          'store'       default_action
                default         None          default_default
                dest            name          default_dest
                type            string        default_type

        So, for example, the default action is 'store', but you can override
        this by passing, say, default_action='store_true' to the cmdline
        constructor.

        You can also specify the action for a specific option in the dict
        defining that option.
        """
        pytest.debug_func()
        c = U.cmdline(simple_arg_list(),
                      default_type=float)
        try:
            (o, a) = c.parse(['cmd',
                              '--first', 7.3,
                              '--second', 9.452,
                              ])
        except SystemExit:
            pass

        assert o.first == 7.3
        assert o.second == [9.452]
        assert o.third is False
        assert o.forward is None

    # -----------------------------------------------------------------------
    def test_cmdline_long_opts(self):
        """
        Test the cmdline class for command line parsing
        """
        self.dbgfunc()
        c = U.cmdline(self.clargs)

        self.exp_in_got('--debug', c.p._long_opt)
        self.exp_in_got('--test', c.p._long_opt)
        self.exp_in_got('--special', c.p._long_opt)

    # -----------------------------------------------------------------------
    def test_cmdline_parse(self):
        """
        Test the cmdline class for command line parsing
        """
        self.dbgfunc()
        c = U.cmdline(self.clargs)

        (o, a) = c.parse(['cmd', '-t', '--special'])
        self.expected(True, o.fribble)
        self.expected(True, o.special)
        self.expected(False, o.debug)

        (o, a) = c.parse(['cmd', '--test'])
        self.expected(True, o.fribble)
        self.expected(False, o.special)
        self.expected(False, o.debug)

        (o, a) = c.parse(['cmd', '-s'])
        self.expected(False, o.fribble)
        self.expected(True, o.special)
        self.expected(False, o.debug)

        (o, a) = c.parse(['cmd'])
        self.expected(False, o.fribble)
        self.expected(False, o.special)
        self.expected(False, o.debug)


# ---------------------------------------------------------------------------
class TestUtil(th.HelpedTestCase):
    tmp = "/tmp"
    if os.path.islink(tmp):
        p = os.path.dirname(tmp)
        t = os.readlink(tmp)
        tmp = U.abspath(t, p)
        testdir = os.path.join(tmp, "test_util")
    else:
        testdir = "/tmp/test_util"

    # -----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """
        This is run before each test
        """
        if not os.path.exists(TestUtil.testdir):
            os.mkdir(TestUtil.testdir)

    # -----------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        """
        This gets run after each test
        """
        kf = os.getenv("KEEPFILES")
        if kf is None or not int(kf):
            shutil.rmtree(TestUtil.testdir)

    # -----------------------------------------------------------------------
    def test_chdir(self):
        """
        Test the Chdir() context manager
        """
        pre = os.getcwd()
        self.assertNotEqual(pre, self.testdir)
        with U.Chdir(self.testdir):
            inter = os.getcwd()
            self.assertEqual(inter, U.abspath(self.testdir))
        post = os.getcwd()
        self.assertNotEqual(post, self.testdir)
        self.assertEqual(post, pre)

    # -----------------------------------------------------------------------
    def test_contents_empty(self):
        """
        Calling contents on an empty file should return an empty list
        """
        with U.Chdir(self.testdir):
            U.touch("empty_file")
            z = U.contents("empty_file")
        self.assertEqual([], z)

    # -----------------------------------------------------------------------
    def test_contents_something(self):
        """
        Calling contents on a non-empty file should return a list of lines form
        the file
        """
        testdata = ["line 1", "line 2", "line 3"]
        with U.Chdir(self.testdir):
            th.write_file("something", content=testdata)
            z = U.contents("something")
        self.assertEqual(testdata, z)

    # -----------------------------------------------------------------------
    def test_expand(self):
        """
        Routine expand should expand env vars and ~ in a string
        """
        home = os.environ['HOME']
        logname = os.environ['LOGNAME']
        os.environ['UPATH'] = "~%s/prj/backscratcher" % logname

        self.assertEqual(U.expand('$HOME'), home)
        self.assertEqual(U.expand('~'), home)
        self.assertEqual(U.expand('~%s' % logname), home)
        self.assertEqual(U.expand('### $TERM ###'),
                         '### %s ###' % os.environ['TERM'])
        self.assertEqual(U.expand("$UPATH"),
                         "%s/prj/backscratcher" % home)

    # -----------------------------------------------------------------------
    def test_function_name(self):
        """
        Routine function_name() should return the name of its caller
        """
        self.assertEqual(U.function_name(), "test_function_name")

    # -----------------------------------------------------------------------
    def test_git_describe(self):
        """
        Test running git_describe and grabbing its output
        """
        if not U.in_bscr_repo():
            pytest.skip("not in backscratcher repo")

        got = U.git_describe()
        result = re.findall("\d{4}\.\d{4}\w*", got)
        self.assertTrue(0 < len(result),
                        "Expected something, got an empty list")

    # -----------------------------------------------------------------------
    def test_lquote(self):
        """
        Routine lquote() wraps its input in triple quotes with newlines
        """
        testdata = "The quick brown fox jumps over the lazy dog"
        self.assertEqual('"""\n%s\n"""' % testdata,
                         U.lquote(testdata))

    # -----------------------------------------------------------------------
    def test_touch_list(self):
        """
        Routine touch() should create the file if it does not exist and update
        its atime and mtime if it does. It takes a string or list.
        """
        with U.Chdir(self.testdir):
            now = int(time.time())
            flist = ["jabberwocky", "philodendron", "mcguffin"]
            U.touch(flist)
            for fn in flist:
                self.assertTrue(os.path.exists(fn))
                s = os.stat(fn)
                self.assertEqual(now, s[stat.ST_ATIME])
                self.assertEqual(now, s[stat.ST_MTIME])

    # -----------------------------------------------------------------------
    def test_touch_list_times(self):
        """
        Routine touch() should create the file if it does not exist and update
        its atime and mtime if it does. It takes a string or list. It also
        takes an optional second argument containing a tuple with the atime and
        mtime we want to set on the target file(s)
        """
        with U.Chdir(self.testdir):
            now = int(time.time())
            tt = (now+3, now-4)
            flist = ["jabberwocky", "philodendron", "mcguffin"]
            U.touch(flist, tt)
            for fn in flist:
                self.assertTrue(os.path.exists(fn))
                s = os.stat(fn)
                self.assertEqual(tt[0], s[stat.ST_ATIME])
                self.assertEqual(tt[1], s[stat.ST_MTIME])

    # -----------------------------------------------------------------------
    def test_touch_nlns(self):
        """
        Calling touch() with an argument that is not a list or a string should
        get an exception
        """
        with U.Chdir(self.testdir):
            self.assertRaisesMsg(bscr.Error,
                                 "argument must be list or string",
                                 U.touch,
                                 17)

    # -----------------------------------------------------------------------
    def test_touch_str(self):
        """
        Calling touch() with a string, setting the current time
        """
        with U.Chdir(self.testdir):
            now = int(time.time())
            filename = "pines"
            U.touch(filename)
            self.assertTrue(os.path.exists(filename))
            s = os.stat(filename)
            self.assertEqual(now, s[stat.ST_ATIME])
            self.assertEqual(now, s[stat.ST_MTIME])

    # -----------------------------------------------------------------------
    def test_touch_str_times(self):
        """
        Calling touch() with a string, setting some other time
        """
        with U.Chdir(self.testdir):
            now = int(time.time())
            tt = (now-17, now+42)
            filename = "pines"
            U.touch(filename, tt)
            self.assertTrue(os.path.exists(filename))
            s = os.stat(filename)
            self.assertEqual(tt[0], s[stat.ST_ATIME])
            self.assertEqual(tt[1], s[stat.ST_MTIME])

    # -----------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.util', __file__)

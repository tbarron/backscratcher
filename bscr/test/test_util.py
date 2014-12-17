import bscr
from bscr import testhelp as th
from bscr import util as U
import os
import pdb
import re
import shutil
import stat
import time


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
            now = int(time.time())
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

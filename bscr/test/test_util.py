from bscr import testhelp as th
from bscr import util as U
import os
import pdb
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
        if not os.path.exists(TestUtil.testdir):
            os.mkdir(TestUtil.testdir)

    # -----------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        kf = os.getenv("KEEPFILES")
        if kf is None or not int(kf):
            shutil.rmtree(TestUtil.testdir)

    # -----------------------------------------------------------------------
    def test_chdir(self):
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
        with U.Chdir(self.testdir):
            U.touch("empty_file")
            z = U.contents("empty_file")
        self.assertEqual([], z)

    # -----------------------------------------------------------------------
    def test_contents_something(self):
        testdata = ["line 1", "line 2", "line 3"]
        with U.Chdir(self.testdir):
            th.write_file("something", content=testdata)
            z = U.contents("something")
        self.assertEqual(testdata, z)

    # -----------------------------------------------------------------------
    def test_expand(self):
        home = os.environ['HOME']
        logname = os.environ['LOGNAME']
        U.pythonpath_bscrroot()
        os.environ['UPATH'] = "~%s/prj/backscratcher" % logname

        self.assertEqual(U.expand('$HOME'), home)
        self.assertEqual(U.expand('~'), home)
        self.assertEqual(U.expand('~%s' % logname), home)
        self.assertEqual(U.expand('### $PYTHONPATH ###'),
                         '### %s ###' % os.environ['PYTHONPATH'])
        self.assertEqual(U.expand("$UPATH"),
                         "%s/prj/backscratcher" % home)

    # -----------------------------------------------------------------------
    def test_function_name(self):
        self.assertEqual(U.function_name(), "test_function_name")

    # -----------------------------------------------------------------------
    def test_lquote(self):
        testdata = "The quick brown fox jumps over the lazy dog"
        self.assertEqual('"""\n%s\n"""' % testdata,
                         U.lquote(testdata))

    # -----------------------------------------------------------------------
    def test_touch_list(self):
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
        with U.Chdir(self.testdir):
            now = int(time.time())
            self.assertRaisesMsg(StandardError,
                                 "argument must be list or string",
                                 U.touch,
                                 17)

    # -----------------------------------------------------------------------
    def test_touch_str(self):
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

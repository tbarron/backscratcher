import bscr.xclean
from bscr import util as U
import os
import pexpect
import pytest
import re
import shutil
from bscr import testhelp as th


# -----------------------------------------------------------------------------
def test_cleanup_dr_np_nr(capsys, tmpdir, fx_cleanup):
    """
    Run cleanup with dryrun but no pattern or recursive flag. Afterwards, the
    target files should still exist. The dryrun message should show up in the
    output. Target files in the top directory should be named in the output.
    """
    pytest.debug_func()
    bscr.xclean.cleanup(str(tmpdir), dryrun=True)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        floc.exists()
        if all([floc.basename.endswith("~"),
                tmpdir.strpath == floc.dirname]):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_cleanup_dr_np_r(capsys, tmpdir, fx_cleanup):
    """
    xclean --dry-run --recursive
    """
    pytest.debug_func()
    bscr.xclean.cleanup(str(tmpdir), dryrun=True, recursive=True)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        floc.exists()
        if floc.basename.endswith("~"):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_cleanup_dr_p_nr(capsys, tmpdir, fx_cleanup):
    """
    xclean --dry-run --pattern 'no.*'
    """
    pytest.debug_func()
    rgx = "no.*"
    bscr.xclean.cleanup(str(tmpdir), dryrun=True, pattern=rgx)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        floc.exists()
        if all([tmpdir.strpath == floc.dirname,
                re.findall(rgx, floc.basename)]):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_cleanup_dr_p_r(capsys, tmpdir, fx_cleanup):
    """
    xclean --dry-run --pattern 'no.*' --recursive
    """
    pytest.debug_func()
    rgx = "no.*"
    bscr.xclean.cleanup(str(tmpdir), dryrun=True, pattern=rgx, recursive=True)
    result = "".join(capsys.readouterr())
    assert fx_cleanup["drmsg"] in result
    for floc in fx_cleanup["files"]:
        floc.exists()
        if re.findall(rgx, floc.basename):
            assert floc.basename in result
        else:
            assert floc.basename not in result


# -----------------------------------------------------------------------------
def test_standalone():
    """
    Make these tests stand-alone
    """
    pytest.fail("Make {} tests stand-alone".format(__file__))


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_cleanup(tmpdir):
    """
    Set up files for various tests
    """
    tmpdir.join('sub').ensure(dir=True)
    rval = {}
    rval['drmsg'] = "Without --dryrun, would remove"
    rval['files'] = [tmpdir.join(x).ensure() for x in ['xxx~',
                                                       'yyy~',
                                                       'sub/basement~',
                                                       'sub/.floor~',
                                                       'nomatch.txt',
                                                       'sub/nosuchfile',
                                                       ]]
    return rval


# -----------------------------------------------------------------------------
class TestXclean(th.HelpedTestCase):
    drmsg = 'Without --dryrun, would remove'
    testdir = "/tmp/test_xclean"
    tilde = [U.pj(testdir, 'xxx~'),
             U.pj(testdir, '.yyy~')]
    stilde = [U.pj(testdir, 'sub', 'basement~'),
              U.pj(testdir, 'sub', '.floor~')]
    ntilde = [U.pj(testdir, 'nomatch.txt')]
    nstilde = [U.pj(testdir, 'sub', 'nosuchfile')]
    testfiles = tilde + stilde + ntilde + nstilde

    # -------------------------------------------------------------------------
    def setUp(self):
        """
        Set up for each test in the suite.
        """
        if os.path.isdir(self.testdir):
            self.tearDown()
        os.makedirs(U.pj(self.testdir, 'sub'))
        for fp in self.testfiles:
            U.touch(fp)

    # -------------------------------------------------------------------------
    def tearDown(self):
        """
        Tear down after each test
        """
        shutil.rmtree(self.testdir)

    # -------------------------------------------------------------------------
    def test_cleanup_ndr_np_nr(self):
        """
        xclean
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir)
            result = getval()

        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [False, True, True, True])

        self.assertNotIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, False, False])

    # -------------------------------------------------------------------------
    def test_cleanup_ndr_np_r(self):
        """
        xclean --recursive
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir, recursive=True)
            result = getval()

        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [False, True, False, True])

        self.assertNotIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, True, False])

    # -------------------------------------------------------------------------
    def test_cleanup_ndr_p_nr(self):
        """
        xclean --pattern "no.*"
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir, pattern="no.*")
            result = getval()

        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [True, False, True, True])

        self.assertNotIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, False])

    # -------------------------------------------------------------------------
    def test_cleanup_ndr_p_r(self):
        """
        xclean --pattern "no.*" --recursive
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir, pattern="no.*", recursive=True)
            result = getval()

        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [True, False, True, False])

        self.assertNotIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, True])

    # -------------------------------------------------------------------------
    def test_find_files(self):
        """
        Finding files without recursion
        """
        fl = bscr.xclean.find_files(self.testdir)
        for fn in self.tilde:
            self.assertIn(fn, fl,
                          "Expected %s in %s" % (fn, fl))
        for fn in self.stilde:
            self.assertNotIn(fn, fl,
                             "Expected %s to not be in %s" % (fn, fl))
        for fn in self.ntilde:
            self.assertNotIn(fn, fl,
                             "Expected %s to not be in %s" % (fn, fl))
        for fn in self.nstilde:
            self.assertNotIn(fn, fl,
                             "Expected %s to not be in %s" % (fn, fl))

    # -------------------------------------------------------------------------
    def test_find_files_r(self):
        """
        find files with recursion
        """
        fl = bscr.xclean.find_files(self.testdir, recursive=True)
        for fn in self.tilde:
            self.assertIn(fn, fl,
                          "Expected %s in %s" % (fn, fl))
        for fn in self.stilde:
            self.assertIn(fn, fl,
                          "Expected %s in %s" % (fn, fl))
        for fn in self.ntilde:
            self.assertNotIn(fn, fl,
                             "Expected %s to not be in %s" % (fn, fl))
        for fn in self.nstilde:
            self.assertNotIn(fn, fl,
                             "Expected %s to not be in %s" % (fn, fl))

    # -------------------------------------------------------------------------
    def test_find_files_p(self):
        """
        find files that match a pattern
        """
        fl = bscr.xclean.find_files(self.testdir, pattern='no.*')
        for fn in self.tilde:
            self.assertNotIn(fn, fl,
                             "Expected %s to not be in %s" % (fn, fl))
        for fn in self.stilde:
            self.assertNotIn(fn, fl,
                             "Expected %s to not be in %s" % (fn, fl))
        for fn in self.ntilde:
            self.assertIn(fn, fl,
                          "Expected %s in %s" % (fn, fl))
        for fn in self.nstilde:
            self.assertNotIn(fn, fl,
                             "Expected %s to not be in %s" % (fn, fl))

    # -------------------------------------------------------------------------
    def test_find_files_p_r(self):
        """
        find files that match a pattern, recursively
        """
        fl = bscr.xclean.find_files(self.testdir, pattern='no.*',
                                    recursive=True)
        for fn in self.tilde:
            self.assertNotIn(fn, fl,
                             "Expected %s to not be in %s" % (fn, fl))
        for fn in self.stilde:
            self.assertNotIn(fn, fl,
                             "Expected %s to not be in %s" % (fn, fl))
        for fn in self.ntilde:
            self.assertIn(fn, fl,
                          "Expected %s in %s" % (fn, fl))
        for fn in self.nstilde:
            self.assertIn(fn, fl,
                          "Expected %s in %s" % (fn, fl))

    # -------------------------------------------------------------------------
    def test_main_dr_np_nr(self):
        """
        calling main: xclean --dry-run
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-n', self.testdir])
            result = getval()
        self.assertIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [True, True, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, False, False])

    # -------------------------------------------------------------------------
    def test_main_dr_p_nr(self):
        """
        calling main: xclean --dry-run --pattern "no.*"
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-n', '-p', 'no.*', self.testdir])
            result = getval()
        self.assertIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [True, True, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, False])

    # -------------------------------------------------------------------------
    def test_main_dr_np_r(self):
        """
        calling main: xclean --dry-run --recursive
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-n', '-r', self.testdir])
            result = getval()
        self.assertIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [True, True, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, True, False])

    # -------------------------------------------------------------------------
    def test_main_dr_p_r(self):
        """
        calling main: xclean --dry-run --pattern "no.*" --recursive
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-n', '-p', 'no.*',
                              '-r', self.testdir])
            result = getval()
        self.assertIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [True, True, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, True])

    # -------------------------------------------------------------------------
    def test_main_ndr_np_nr(self):
        """
        calling main: xclean
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', self.testdir])
            result = getval()
        self.assertNotIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [False, True, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, False, False])

    # -------------------------------------------------------------------------
    def test_main_ndr_np_r(self):
        """
        calling main: xclean --recursive
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-r', self.testdir])
            result = getval()
        self.assertNotIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [False, True, False, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, True, False])

    # -------------------------------------------------------------------------
    def test_main_ndr_p_nr(self):
        """
        calling main: xclean --pattern "no.*"
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-p', 'no.*', self.testdir])
            result = getval()
        self.assertNotIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [True, False, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, False])

    # -------------------------------------------------------------------------
    def test_main_ndr_p_r(self):
        """
        calling main: xclean --pattern "no.*" --recursive
        """
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-p', 'no.*', '-r', self.testdir])
            result = getval()
        self.assertNotIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde,
                            self.nstilde],
                           [True, False, True, False])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, True])

    # -------------------------------------------------------------------------
    def test_xclean_help(self):
        """
        Verify that 'xclean --help' does the right thing
        """
        exp = ["Usage:",
               "    xclean - remove files whose names match a regexp",
               "",
               "Options:",
               "  -h, --help            show this help message and exit",
               "  -d, --debug           run under the debugger",
               "  -n, --dry-run         just report",
               "  -p PATTERN, --pattern=PATTERN",
               "                        file matching regexp",
               "  -r, --recursive       whether to descend directories",
               ]
        cmd = U.script_location("xclean")
        actual = pexpect.run("%s --help" % cmd)
        for line in exp:
            self.assertTrue(line in actual,
                            "Expected '%s' in %s" %
                            (line, U.lquote(actual)))

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.xclean', __file__)

    # -------------------------------------------------------------------------
    def verify_exists(self, tv, rv):
        """
        tv is a list of file paths, rv is a list of truth values.
        If rv[i] is True, we expect tv[i] to be an existing file,
        otherwise not.
        """
        for fl, exp in zip(tv, rv):
            for fp in fl:
                self.assertEqual(exp, os.path.exists(fp),
                                 "expected '%s' to exist" % fp if exp else
                                 "expected '%s' to not exist" % fp)

    # -------------------------------------------------------------------------
    def verify_in(self, tv, text, rv):
        """
        tv is a list of strings, rv is a list of truth values. If r[i] is True,
        we expect that tv[i] will appear in text, otherwise not.
        """
        for fl, exp in zip(tv, rv):
            for fp in fl:
                if exp:
                    self.assertIn(fp, text,
                                  "expected '%s' in '%s'" % (fp, text))
                else:
                    self.assertNotIn(fp, text,
                                     "'%s' not expected in '%s'" % (fp, text))

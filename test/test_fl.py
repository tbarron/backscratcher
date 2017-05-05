#!/usr/bin/env python
from bscr import fl
from bscr import util
import os
import pexpect
import py
import pytest
import random
import re
import shutil
import stat
import tempfile
from bscr import testhelp as th
import time
from bscr import util as U


# -----------------------------------------------------------------------------
def test_amtime_atom_dir(tmpdir):
    """
    Test fl_set_atime_to_mtime()
    """
    pytest.debug_func()
    atime = int(time.time() - random.randint(1000, 2000))
    mtime = int(time.time() + random.randint(1000, 2000))
    atom = makefile(tmpdir, "atom", content="This is the test file",
                    atime=atime, mtime=mtime)
    fl.fl_set_atime_to_mtime(**{"FILE": [atom.strpath], "d": False})
    s = os.stat(atom.strpath)
    assert mtime == s[stat.ST_MTIME]
    assert mtime == s[stat.ST_ATIME]
    assert s[stat.ST_ATIME] == s[stat.ST_MTIME]


# -----------------------------------------------------------------------------
def test_amtime_atom_pxr(tmpdir):
    """
    Test fl_set_atime_to_mtime()
    """
    pytest.debug_func()
    atime = int(time.time() - random.randint(1000, 2000))
    mtime = int(time.time() + random.randint(1000, 2000))
    atom = makefile(tmpdir, "atom", content="This is the test file",
                    atime=atime, mtime=mtime)
    result = pexpect.run("fl set_atime_to_mtime {}".format(atom.strpath))
    assert result == ""
    s = os.stat(atom.strpath)
    assert mtime == s[stat.ST_MTIME]
    assert mtime == s[stat.ST_ATIME]
    assert s[stat.ST_ATIME] == s[stat.ST_MTIME]


# -----------------------------------------------------------------------------
def test_amtime_mtoa(tmpdir):
    """
    Test fl_set_mtime_to_atime()
    """
    atime = int(time.time() - random.randint(1000, 2000))
    mtime = int(time.time() + random.randint(1000, 2000))
    atom = makefile(tmpdir, "mtoa", content="This is the test file",
                    atime=atime, mtime=mtime)
    fl.fl_set_mtime_to_atime([atom.strpath])
    s = os.stat(atom.strpath)
    assert s[stat.ST_ATIME] == atime
    assert s[stat.ST_MTIME] == atime
    assert s[stat.ST_ATIME] == s[stat.ST_MTIME]


# -----------------------------------------------------------------------------
def test_command_line():
    """
    Running the command with no arguments should get help output
    """
    thisone = util.script_location("fl")

    result = pexpect.run(thisone)
    assert "Traceback" not in result
    assert "diff" in result
    assert "save" in result
    assert "times" in result


# -----------------------------------------------------------------------------
def test_diff_match_dir(tmpdir, capsys, fx_match):
    """
    Test fl.fl_diff(**{'d': False, 'FILE': filename}) when a prefix match
    exists
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        fl.fl_diff(**{"d": False, "n": False,
                      "FILE": [fx_match.mrpm1.basename]})
        got, _ = capsys.readouterr()
        assert fx_match.mrpm1_diff_exp == got.split("\n")

        fl.fl_diff(**{"d": False, "n": False, "FILE": ["mrpm2"]})
        got, _ = capsys.readouterr()
        assert "\n".join(fx_match.mrpm2_diff_exp) == got


# -----------------------------------------------------------------------------
def test_diff_match_pxr(tmpdir, fx_match):
    """
    Test 'fl diff FILENAME' when a prefix match exists
    """
    pytest.debug_func()
    with U.Chdir(tmpdir.strpath):
        cmd = "{} diff {}".format(U.script_location("fl"),
                                  fx_match.mrpm1.basename)
        got = pexpect.run(cmd).split("\n")
        assert fx_match.mrpm1_diff_exp == [_.rstrip() for _ in got]

        cmd = "{} diff {}".format(U.script_location("fl"),
                                  fx_match.mrpm2.basename)
        got = pexpect.run(cmd).split("\n")
        assert fx_match.mrpm2_diff_exp == [_.rstrip() for _ in got]


    with U.Chdir(tmpdir.strpath):
        expected = ["/Users/tbarron/prj/github/backscratcher/"
                    "bscr/util.py:210: "
                    "UserWarning: util.dispatch is deprecated "
                    "in favor of docopt_dispatch\r",
                    "  warnings.warn(\"util.dispatch is deprecated"
                    " in favor of docopt_dispatch\")\r",
                    'diff ./mrpm1.2009-10-01 mrpm1\r',
                    '1c1\r',
                    '< copy of test file\r',
                    '---\r',
                    '> this is a test file\r',
                    '']
        cmd = U.script_location("fl")
        got = pexpect.run("{} diff {}".format(cmd, mrpm1.basename)).split("\n")
        assert expected == got

        expected = ["/Users/tbarron/prj/github/backscratcher/"
                    "bscr/util.py:210: "
                    "UserWarning: util.dispatch is deprecated "
                    "in favor of docopt_dispatch\r",
                    "  warnings.warn(\"util.dispatch is deprecated"
                    " in favor of docopt_dispatch\")\r",
                    'diff ./old/mrpm2.2009-08-31 mrpm2\r',
                    '1c1\r',
                    '< copy of another test file\r',
                    '---\r',
                    '> this is another test file\r',
                    '']
        got = pexpect.run("%s diff mrpm2" % cmd).split("\n")
        assert expected == got


# ---------------------------------------------------------------------------
def setUpModule():
    """
    Run once before any of the tests in this module
    """
    if os.path.basename(os.getcwd()) == 'fl_tests':
        return

    if not os.path.exists('fl_tests'):
        os.mkdir('fl_tests')
        os.mkdir('fl_tests/old')


# ---------------------------------------------------------------------------
def tearDownModule():
    """
    Run once after all the tests in this module
    """
    kf = os.getenv('KEEPFILES')
    if not kf:
        shutil.rmtree('fl_tests')


# -----------------------------------------------------------------------------
class TestFL(th.HelpedTestCase):
    # tests needed:
    #   'fl help' -- test_fl_help
    #   'fl help help' -- test_fl_help_help
    #   'fl help rm_cr'
    #   'fl times'
    #   'fl nosuchcmd'

    # -------------------------------------------------------------------------
    def test_fl_help(self):
        """
        'fl help' should get help output
        """
        cmd = util.script_location("fl")
        result = pexpect.run('%s help' % cmd)
        self.assertFalse('Traceback' in result)
        for f in [x for x in dir(fl) if x.startswith('bscr_')]:
            subc = f.replace('bscr_', '')
            self.assertTrue('%s - ' % subc in result)

    # -------------------------------------------------------------------------
    def test_fl_help_help(self):
        """
        'fl help help' should get help for the help command
        """
        cmd = pexpect.which('fl')
        result = pexpect.run('%s help help' % cmd)
        self.assertFalse('Traceback' in result)
        for f in ['help - show a list of available commands',
                  'With no arguments, show a list of commands',
                  'With a command as argument, show help for that command',
                  ]:
            self.assertTrue(f in result)

    # -----------------------------------------------------------------------
    def test_most_recent_prefix_match(self):
        """
        Test the routine most_recent_prefix_match()
        """
        with util.Chdir("fl_tests"):
            util.writefile('mrpm1', ['this is a test file'])
            util.writefile('mrpm2', ['this is another test file'])
            os.system('cp mrpm1 mrpm1.2009-10-01')
            os.system('cp mrpm2 old/mrpm2.2009-08-31')

            a = fl.most_recent_prefix_match('.', 'mrpm1')
            self.assertEq('./mrpm1.2009-10-01', a)

            a = fl.most_recent_prefix_match('.', 'mrpm2')
            self.assertEq('./old/mrpm2.2009-08-31', a)

    # -----------------------------------------------------------------------
    def test_diff(self):
        """
        Test diff
        """
        with util.Chdir("fl_tests"):
            util.writefile('mrpm1', ['this is a test file\n'])
            util.writefile('mrpm2', ['this is another test file\n'])
            util.writefile('mrpm1.2009-10-01', ['copy of test file\n'])
            util.writefile('old/mrpm2.2009-08-31',
                           ['copy of another test file\n'])

            expected = ["/Users/tbarron/prj/github/backscratcher/"
                        "bscr/util.py:207: "
                        "UserWarning: util.dispatch is deprecated "
                        "in favor of docopt_dispatch\r",
                        "  warnings.warn(\"util.dispatch is deprecated"
                        " in favor of docopt_dispatch\")\r",
                        'diff ./mrpm1.2009-10-01 mrpm1\r',
                        '1c1\r',
                        '< copy of test file\r',
                        '---\r',
                        '> this is a test file\r',
                        '']
            cmd = util.script_location("fl")
            got = pexpect.run("%s diff mrpm1" % cmd).split("\n")
            self.assertEqual(expected, got)

            expected = ["/Users/tbarron/prj/github/backscratcher/"
                        "bscr/util.py:207: "
                        "UserWarning: util.dispatch is deprecated "
                        "in favor of docopt_dispatch\r",
                        "  warnings.warn(\"util.dispatch is deprecated"
                        " in favor of docopt_dispatch\")\r",
                        'diff ./old/mrpm2.2009-08-31 mrpm2\r',
                        '1c1\r',
                        '< copy of another test file\r',
                        '---\r',
                        '> this is another test file\r',
                        '']
            got = pexpect.run("%s diff mrpm2" % cmd).split("\n")
            self.assertEqual(expected, got)

    # -----------------------------------------------------------------------
    def test_revert(self):
        """
        Test revert
        """
        with util.Chdir("fl_tests"):
            util.writefile('mrpm1', ['this is a test file\n'])
            util.writefile('mrpm2', ['this is another test file\n'])
            util.writefile('mrpm1.2009-10-01', ['reverted\n'])
            util.writefile('old/mrpm2.2009-08-31',
                           ['REVERTED\n'])

            fl = util.script_location("fl")
            os.system('%s revert mrpm1' % fl)
            assert(os.path.exists('mrpm1.new'))
            assert(os.path.exists('mrpm1'))
            assert(not os.path.exists('mrpm1.2009-10-01'))
            assert(util.contents('mrpm1') == ['reverted'])

            os.system('%s revert mrpm2' % fl)
            assert(os.path.exists('mrpm2.new'))
            assert(os.path.exists('mrpm2'))
            assert(not os.path.exists('old/mrpm2.2009-08-31'))
            assert(util.contents('mrpm2') == ['REVERTED'])

    # -----------------------------------------------------------------------
    def test_mtoa(self):
        """
        Test set_mtime_to_atime
        """
        with util.Chdir("fl_tests"):
            filename = 'mtoa'
            open(filename, 'w').close()
            os.utime(filename, (time.time() - random.randint(1000, 2000),
                                time.time() + random.randint(1000, 2000)))
            s = os.stat(filename)
            assert(s[stat.ST_ATIME] != s[stat.ST_MTIME])
            fl.fl_set_mtime_to_atime([filename])
            s = os.stat(filename)
            assert(s[stat.ST_ATIME] == s[stat.ST_MTIME])

    # -------------------------------------------------------------------------
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.fl', __file__)


# -----------------------------------------------------------------------------
class TestFL_edit(th.HelpedTestCase):
    testdir = tempfile.mkdtemp(dir="/tmp")
    testdata = ["one foo two foo three\n",
                "foo four five foo\n",
                "six seven eight foo nine\n"]

    # -------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        """
        Clean up test directory
        """
        shutil.rmtree(cls.testdir)

    # -------------------------------------------------------------------------
    def test_editfile_nosuch(self):
        """
        fl.editfile('nosuchfile', 'foo', 'bar', None)
         => should throw an exception
        """
        self.assertRaisesMsg(IOError,
                             "No such file or directory: 'nosuchfile'",
                             fl.editfile,
                             'nosuchfile',
                             's',
                             'foo',
                             'bar',
                             None)

    # -------------------------------------------------------------------------
    def test_editfile_empty(self):
        """
        fl.editfile('emptyfile', 's', 'foo', 'bar', None)
         => rename emptyfile emptyfile.original, both empty
        """
        fpath = U.pj(self.testdir, 'emptyfile')
        forig = fpath + ".original"
        U.touch(fpath)

        fl.editfile(fpath, 's', 'foo', 'bar', None)

        self.assertEq(True, U.exists(fpath))
        self.assertEq(True, U.exists(forig))
        self.assertEq([], U.contents(fpath))
        self.assertEq([], U.contents(forig))

    # -------------------------------------------------------------------------
    def test_editfile_legit(self):
        """
        fl.editfile('legit', 's', 'foo', 'bar', None)
        """
        fp = U.pj(self.testdir, 'legit')
        forig = fp + ".original"
        tdata = ["foo bar",
                 "bar foo",
                 "barfoo",
                 "foobar foo",
                 "loofafool"]
        xdata = [z.replace('foo', 'bar') for z in tdata]
        U.writefile(fp, tdata, newlines=True)

        fl.editfile(fp, 's', 'foo', 'bar', None)

        self.assertEq(True, U.exists(fp))
        self.assertEq(True, U.exists(forig))
        self.assertEq(xdata, U.contents(fp))
        self.assertEq(tdata, U.contents(forig))

    # -------------------------------------------------------------------------
    def test_editfile_suffix(self):
        """
        fl.editfile('legit', 's', 'foo', 'bar', 'old')
        """
        fp = U.pj(self.testdir, U.function_name())
        forig = fp + ".old"
        tdata = ["foo bar",
                 "bar foo",
                 "barfoo",
                 "foobar foo",
                 "loofafool"]
        xdata = [z.replace('foo', 'bar') for z in tdata]
        U.writefile(fp, tdata, newlines=True)

        fl.editfile(fp, 's', 'foo', 'bar', 'old')

        self.assertEq(True, U.exists(fp))
        self.assertEq(True, U.exists(forig))
        self.assertEq(xdata, U.contents(fp))
        self.assertEq(tdata, U.contents(forig))

    # -------------------------------------------------------------------------
    def test_editfile_rgx(self):
        """
        fl.editfile('legit', 's', 'foo', 'bar', None)
        """
        fp = U.pj(self.testdir, U.function_name())
        forig = fp + ".original"
        tdata = ["foo bar",
                 "bar foo",
                 "barfoo",
                 "foobar foo",
                 "loofafool"]
        xdata = [re.sub('^foo', 'bar', z) for z in tdata]
        U.writefile(fp, tdata, newlines=True)

        fl.editfile(fp, 's', '^foo', 'bar', None)

        self.assertEq(True, U.exists(fp))
        self.assertEq(True, U.exists(forig))
        self.assertEq(xdata, U.contents(fp))
        self.assertEq(tdata, U.contents(forig))

    # -------------------------------------------------------------------------
    def test_editfile_delete(self):
        """
        fl.editfile('legit', 's', 'foo', '', None)
        """
        fp = U.pj(self.testdir, U.function_name())
        forig = fp + ".original"
        tdata = ["foo bar",
                 "bar foo",
                 "barfoo",
                 "foobar foo",
                 "loofafool"]
        xdata = [re.sub('^foo', '', z) for z in tdata]
        U.writefile(fp, tdata, newlines=True)

        fl.editfile(fp, 's', '^foo', '', None)

        self.assertEq(True, U.exists(fp))
        self.assertEq(True, U.exists(forig))
        self.assertEq(xdata, U.contents(fp))
        self.assertEq(tdata, U.contents(forig))

    # -------------------------------------------------------------------------
    def test_fl_edit_noarg(self):
        """
        fl edit                          => help msg
        """
        self.fl_edit_flawed("fl edit",
                            "usage: fl edit [-i <suffix>] -e <cmd> f1 f2 ...")

    # -------------------------------------------------------------------------
    def test_fl_edit_e_reqarg(self):
        """
        fl edit -e                       => -e requires argument
        check for
         - message that -e requires an argument
        """
        self.fl_edit_flawed("fl edit -e",
                            "-e option requires an argument")

    # -------------------------------------------------------------------------
    def test_fl_edit_i_reqarg(self):
        """
        fl edit -i                       => -i requires argument
        check for message that -i requires argument
        """
        self.fl_edit_flawed("fl edit -i",
                            "-i option requires an argument")

    # -------------------------------------------------------------------------
    def test_fl_edit_nofiles(self):
        """
        fl edit -e "s/foo/bar/"          => no files to edit
        check for message that there are no files to edit
        """
        self.fl_edit_flawed("fl edit -e 's/foo/bar/'",
                            "no files on command line to edit")

    # -------------------------------------------------------------------------
    def test_fl_edit_sub_mid(self):
        """
        fl edit -e "s/foo/bar/" f1 f2    => change "foo" to "bar" in f1, f2
        check for
         - f{1,2} edited correctly
         - f{1,2}.original exists with unchanged content
        """
        self.fl_edit_warn(eopt="s/foo/bar/",
                          files=2,
                          inp=self.testdata,
                          exp=["one bar two bar three",
                               "bar four five bar",
                               "six seven eight bar nine"],
                          warn=["/Users/tbarron/prj/github/backscratcher/bscr/"
                                "util.py:207: UserWarning: util.dispatch is "
                                "deprecated in favor of docopt_dispatch",
                                "  warnings.warn(\"util.dispatch is "
                                "deprecated in favor of docopt_dispatch\")"])

    # -------------------------------------------------------------------------
    def test_fl_edit_sub_bol(self):
        """
        fl edit -e "s/^foo/bar/" f1 f2   => edit at beginning of line
         - f1 edited correctly
         - f2 edited correctly
         - f{1,2}.original have unchanged content
        """
        self.fl_edit_warn(eopt="s/^foo/bar/",
                          files=2,
                          inp=self.testdata,
                          exp=["one foo two foo three",
                               "bar four five foo",
                               "six seven eight foo nine"],
                          warn=["/Users/tbarron/prj/github/backscratcher/bscr/"
                                "util.py:207: UserWarning: util.dispatch is "
                                "deprecated in favor of docopt_dispatch",
                                "  warnings.warn(\"util.dispatch is "
                                "deprecated in favor of docopt_dispatch\")"])

    # -------------------------------------------------------------------------
    def test_fl_edit_i_old(self):
        """
        fl edit -i old -e "s/x/y/" f1    => rename original to f1.old
         - f1 edited correctly
         - f1.old exists
         - f1.original does not exist
        """
        pytest.debug_func()
        self.fl_edit_warn(eopt="s/[rv]e/n/",
                          iopt="old",
                          files=1,
                          inp=self.testdata,
                          exp=["one foo two foo thne",
                               "foo four fin foo",
                               "six senn eight foo nine"],
                          warn=["/Users/tbarron/prj/github/backscratcher/bscr/"
                                "util.py:207: UserWarning: util.dispatch is "
                                "deprecated in favor of docopt_dispatch",
                                "  warnings.warn(\"util.dispatch is "
                                "deprecated in favor of docopt_dispatch\")"])

    # -------------------------------------------------------------------------
    def test_fl_edit_xlate_rot13(self):
        """
        fl edit -e "y/a-z/n-za-m/" f1 f2 => rot13
        check for
         - f{1,2} edited correctly
         - f{1,2}.original exist with correct content
        """
        prev = "abcdefghijklmnopqrstuvwxyz"
        post = "nopqrstuvwxyzabcdefghijklm"
        self.fl_edit_warn(eopt="y/%s/%s/" % (prev, post),
                          files=2,
                          inp=self.testdata,
                          exp=["bar sbb gjb sbb guerr",
                               "sbb sbhe svir sbb",
                               "fvk frira rvtug sbb avar"],
                          warn=["/Users/tbarron/prj/github/backscratcher/bscr/"
                                "util.py:207: UserWarning: util.dispatch is "
                                "deprecated in favor of docopt_dispatch",
                                "  warnings.warn(\"util.dispatch is "
                                "deprecated in favor of docopt_dispatch\")"])

    # -------------------------------------------------------------------------
    def test_fl_edit_xlate_ret(self):
        """
        fl edit -e "y/\r//" f1 f2        => remove \r characters
         - f{1,2} edited correctly
         - f{1,2}.original have correct original content
        """
        rdata = [x.rstrip() + "\r\n" for x in self.testdata]
        self.fl_edit_warn(eopt="y/\r//",
                          files=2,
                          inp=rdata,
                          exp=["one foo two foo three",
                               "foo four five foo",
                               "six seven eight foo nine"],
                          warn=["/Users/tbarron/prj/github/backscratcher/bscr/"
                                "util.py:207: UserWarning: util.dispatch is "
                                "deprecated in favor of docopt_dispatch",
                                "  warnings.warn(\"util.dispatch is "
                                "deprecated in favor of docopt_dispatch\")"])

    # -------------------------------------------------------------------------
    def fl_edit_flawed(self, cmd, exp):
        """
        Attempt to run an 'fl edit' command with something missing
        """
        result = pexpect.run(cmd)
        self.assertFalse("Traceback" in result,
                         "Traceback not expected in %s" % result)
        self.assertTrue(exp in result,
                        "\nExpected '%s' in \n%s" %
                        (exp, util.lquote(result)))

    # -------------------------------------------------------------------------
    def fl_edit_warn(self, eopt='', iopt='', files=0,
                     inp=None, exp=None, warn=None):
        """
        Common code for all the test_fl_edit_* routines
        """
        fl = []
        inp = inp or []
        exp = exp or []
        warn = warn or []
        for idx in range(files):
            (fd, fp) = tempfile.mkstemp(dir=self.testdir)
            os.close(fd)
            fl.append(fp)
            util.writefile(fp, inp)

        suffix = 'original'
        with util.Chdir(self.testdir):
            cmd = "fl edit "
            if eopt != '':
                cmd += '-e "%s" ' % eopt
            if iopt != '':
                cmd += '-i %s ' % iopt
                suffix = iopt
            if 0 < len(fl):
                cmd += " ".join(fl)
            result = pexpect.run(cmd)

            self.assertTrue(result == "\r\n".join(warn + [""]),
                            "Expected '%s' to contain '%s'"
                            % (result, "\r\n".join(warn + [""])))
            for fp in fl:
                forig = fp + "." + suffix
                self.assertTrue(util.exists(forig),
                                "Expected %s to exist" % forig)
                self.assertTrue("foo four five foo" in util.contents(forig),
                                "Contents of %s have changed" % forig)
                self.assertTrue(util.exists(fp),
                                "Expected %s to exist" % fp)
                self.assertEq(exp, util.contents(fp))

            for fp in fl:
                util.safe_unlink(fp)

    # -------------------------------------------------------------------------
    def fl_edit_ok(self, eopt='', iopt='', files=0, inp=[], exp=[]):
        """
        Common code for all the test_fl_edit_* routines
        """
        fl = []
        for idx in range(files):
            (fd, fp) = tempfile.mkstemp(dir=self.testdir)
            os.close(fd)
            fl.append(fp)
            util.writefile(fp, inp)

        suffix = 'original'
        with util.Chdir(self.testdir):
            cmd = "fl edit "
            if eopt != '':
                cmd += '-e "%s" ' % eopt
            if iopt != '':
                cmd += '-i %s ' % iopt
                suffix = iopt
            if 0 < len(fl):
                cmd += " ".join(fl)
            result = pexpect.run(cmd)

            self.assertTrue(result == "",
                            "Expected '%s' to be empty" % result)
            for fp in fl:
                forig = fp + "." + suffix
                self.assertTrue(util.exists(forig),
                                "Expected %s to exist" % forig)
                self.assertTrue("foo four five foo" in util.contents(forig),
                                "Contents of %s have changed" % forig)
                self.assertTrue(util.exists(fp),
                                "Expected %s to exist" % fp)
                self.assertEq(exp, util.contents(fp))

            for fp in fl:
                util.safe_unlink(fp)


# -----------------------------------------------------------------------------
def makefile(loc, basename, content=None, ensure=False, dir=False,
             copy=None, atime=0, mtime=0):
    """
    Return a py.path.local based on *loc*.join(*basename*). If *ensure*, touch
    it. If *dir*, make it a directory
    """
    rval = loc.join(basename)
    if copy:
        if dir:
            raise U.Error("*dir* must be false if *copy* is not None")
        if isinstance(copy, py.path.local):
            copy.copy(rval)
        elif isinstance(copy, str):
            copy = py.path.local(copy)
            copy.copy(rval)
        else:
            raise U.Error("*copy* must be a py.path.local or an str")
    elif content:
        if dir:
            raise U.Error("*dir* must be false if *content* is not None")
        if isinstance(content, str):
            rval.write(content)
        elif isinstance(content, list):
            rval.write("\n".join(content))
        else:
            rval.write(str(content))
    elif ensure:
        rval.ensure(dir=dir)

    if rval.exists():
        if atime != 0 or mtime != 0:
            atime = atime or time.time()
            mtime = mtime or time.time()
            os.utime(rval.strpath, (atime, mtime))

    return rval


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_match(tmpdir):
    """
    Set up some matching files for fl diff
    """
    this = fx_match
    this.mrpm1 = makefile(tmpdir, "mrpm1", content="this is a test file\n")
    this.mrpm2 = makefile(tmpdir, "mrpm2",
                          content="this is another test file\n")
    this.mprm1_dt = makefile(tmpdir, "mrpm1.2009-10-01",
                             content="copy of test file\n")
    this.olddir = makefile(tmpdir, "old", dir=True, ensure=True)
    this.mprm2_dt = makefile(this.olddir, "mrpm2.2009-08-31",
                             content="copy of another test file\n")

    this.mrpm1_diff_exp = [u'diff ./mrpm1.2009-10-01 mrpm1',
                           u'1c1',
                           u'< copy of test file',
                           u'---',
                           u'> this is a test file',
                           u'',
                           u'']

    this.mrpm2_diff_exp = [u'diff ./old/mrpm2.2009-08-31 mrpm2',
                           u'1c1',
                           u'< copy of another test file',
                           u'---',
                           u'> this is another test file',
                           u'',
                           u'']

    return this

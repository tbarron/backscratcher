import os
from bscr import align                                      # noqa: ignore=F401
import pexpect
import pytest
from bscr import testhelp as th
from bscr import util as U


# -------------------------------------------------------------------------
def test_align_help():
    """
    Verify that 'align --help' does the right thing
    """
    pytest.debug_func()
    cmd = pexpect.which("align")
    result = pexpect.run("%s --help" % cmd)
    nexp = "Traceback"
    assert nexp not in result
    exp = "Align columns from input"
    assert exp in result


# -------------------------------------------------------------------------
def test_digit_alignment(fx_data):
    """
    Words that contain valid numeric specifications should be right
    aligned. Words containing non-numeric values should be left aligned.
    """
    # script = U.script_location("align")
    script = pexpect.which("align")
    S = pexpect.spawn(script)
    S.setecho(False)
    for line in fx_data.tdata:
        S.sendline(line)
    S.send("\004")
    S.expect(pexpect.EOF)
    fx_data.result = th.rm_cov_warn(S.before)
    S.close()


# -------------------------------------------------------------------------
def test_named_input(fx_data):
    """
    Handle both input on stdin as well as input from a named file.
    """
    tfilename = 'testdata'
    f = open(tfilename, 'w')
    for line in fx_data.tdata:
        f.write(line + "\n")
    f.close()

    script = U.script_location("align")
    fx_data.result = th.rm_cov_warn(pexpect.run("%s %s" % (script, tfilename)))


# -----------------------------------------------------------------------------
def test_standalone():
    """
    Make these tests stand-alone
    """
    pytest.fail("Make align tests stand-alone")


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_data():
    """
    Test input and expected output for tests
    """
    fx_data.tdata = [" 1234  -12342 2342.9324 -1234.9238 "
                     "7.82734E+25 -2.2343E-17",
                     "abc  def ghi jkl mno qprs",
                     "foobard simplification denomination"
                     " vituperation spalshy"]
    fx_data.exp = ("   1234          -12342     2342.9324    -1234.9238  " +
                   "7.82734E+25  -2.2343E-17  \r\n" +
                   "abc      def             ghi           jkl           " +
                   "mno          qprs         \r\n" +
                   "foobard  simplification  denomination  vituperation" +
                   "  spalshy      \r\n")
    yield fx_data
    assert fx_data.exp == fx_data.result


# -----------------------------------------------------------------------------
def tearDownModule():
    """
    This one too
    """
    flist = ['testdata']
    if os.getenv('KEEPFILES') is not None:
        return
    for fname in flist:
        if os.path.exists(fname):
            os.unlink(fname)


# -----------------------------------------------------------------------------
class TestAlign(th.HelpedTestCase):
    """
    Test suite for align
    """
    tdata = [" 1234  -12342 2342.9324 -1234.9238 7.82734E+25 -2.2343E-17",
             "abc  def ghi jkl mno qprs",
             "foobard simplification denomination vituperation spalshy"]
    exp = ("   1234          -12342     2342.9324    -1234.9238  " +
           "7.82734E+25  -2.2343E-17  \r\n" +
           "abc      def             ghi           jkl           " +
           "mno          qprs         \r\n" +
           "foobard  simplification  denomination  vituperation" +
           "  spalshy      \r\n")

    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.align', __file__)

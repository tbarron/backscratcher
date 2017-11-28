import pexpect
import pytest
from bscr import calc                      # noqa: ignore=F401


# -------------------------------------------------------------------------
def test_example():
    """
    Example calc session
    """
    pytest.debug_func()
    cmd = pexpect.which("calc")
    S = pexpect.spawn(cmd)
    S.expect("> ")

    S.sendline("7 + 12")
    S.expect("> ")
    assert "19" in S.before

    S.sendline("7.988 + 28.576")
    S.expect("> ")
    assert "36.564000" in S.before

    S.sendline("\"zap\" * 2")
    S.expect("> ")
    assert "zapzap" in S.before

    S.sendline("exit()")
    S.expect(pexpect.EOF)
    S.close()


# -------------------------------------------------------------------------
def test_calc_help():
    """
    Verify that 'calc --help' does the right thing
    """
    pytest.debug_func()
    cmd = pexpect.which("calc")
    result = pexpect.run("%s --help" % cmd)
    nexp = "Traceback"
    assert nexp not in result
    exp = "Usage: calc [options]"
    assert exp in result

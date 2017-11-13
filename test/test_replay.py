"""
Tests for replay
"""
import pexpect
import pytest


# -----------------------------------------------------------------------------
def test_change():
    """
    'replay CMD' should display the output of CMD when it changes
    """
    pytest.debug_func()
    count = 3
    rcmd = "replay \"date '+%s xxx'\""
    S = pexpect.spawn(rcmd)
    last = None
    for idx in range(count):
        S.expect(["xxx", pexpect.EOF])
        cur = S.before
        assert last != cur
        last = cur
    S.close()


# -----------------------------------------------------------------------------
def test_filepath(tmpdir):
    """
    'replay -t FILENAME CMD' should run CMD when timetamp on FILENAME changes
    """
    pytest.debug_func()
    contents = ["one foo", "two foo", "three foo"]
    nib = tmpdir.join("nibble")
    count = 3
    rcmd = "replay -t {} \"cat {}\"".format(nib.strpath, nib.strpath)
    S = pexpect.spawn(rcmd)
    for idx in range(count):
        nib.write(contents[idx] + "\n")
        S.expect(["foo", pexpect.EOF])
        assert S.before.strip() in contents[idx]
    S.close()


    S = pexpect.spawn(rcmd)
    last = None
    for idx in range(count):
        S.expect(["xxx", pexpect.EOF])
        cur = int(S.before)
        if last:
            assert cur - last <= 2
        last = cur
    S.close()


# -----------------------------------------------------------------------------
def test_iterations():
    """
    'replay -i 7 CMD' should run CMD and show its output 7 times
    """
    pytest.debug_func()
    count = 3
    rcmd = "replay -i {} \"date '+%s xxx'\"".format(count)
    S = pexpect.spawn(rcmd)
    last = None
    for idx in range(count):
        S.expect(["xxx", pexpect.EOF])
        cur = int(S.before)
        if last:
            assert cur - last <= 2
        last = cur
    S.close()


# -----------------------------------------------------------------------------
def test_prompt():
    """
    'replay -p CMD' should run CMD and show its output when user hits ENTER
    """
    pytest.debug_func()
    S = pexpect.spawn("replay -p ls")
    S.expect("Hit ENTER...")
    assert "bscr" in S.before
    S.sendline("")
    S.expect("Hit ENTER...")
    S.close()


# -----------------------------------------------------------------------------
def test_replayNeedsTests():
    """
    Need tests for replay
    """
    pytest.fail("replay needs tests")

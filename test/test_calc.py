#!/usr/bin/env python
import pexpect
import unittest

# -----------------------------------------------------------------------------
class TestCalc(unittest.TestCase):
    def test_example(self):
        S = pexpect.spawn("bin/calc")
        # S.logfile = sys.stdout
        S.expect("> ")

        S.sendline("7 + 12")
        S.expect("> ")

        assert("19" in S.before)

        S.sendline("7.988 + 28.576")
        S.expect("> ")

        assert("36.564000" in S.before)

        S.sendline("\"zap\" * 2")
        S.expect("> ")

        assert("zapzap" in S.before)

        S.sendline("exit()")
        S.expect(pexpect.EOF)
        S.close()

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()


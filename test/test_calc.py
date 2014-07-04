#!/usr/bin/env python
import pexpect
import unittest

# -----------------------------------------------------------------------------
class TestCalc(unittest.TestCase):
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_calc_help(self):
        """
        Verify that 'calc --help' does the right thing
        """
        self.fail('construction')
    
    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.fail('construction')
        
    # -------------------------------------------------------------------------
    @unittest.skip("under construction")
    def test_which_script(self):
        """
        Verify that we're running the right script
        """
        self.fail('construction')
        
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()


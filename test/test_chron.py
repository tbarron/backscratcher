import chron
import unittest

# ---------------------------------------------------------------------------
class TestChron(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_hms_seconds(self):
        exp = 3923
        act = chron.hms_seconds("1:05:23")
        self.assertEqual(exp, act,
                         "Expected %d, got %d" % (exp, act))


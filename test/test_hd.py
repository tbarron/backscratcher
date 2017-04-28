#!/usr/bin/env python

from bscr import hd
from bscr import testhelp as th
from bscr import util as U
from StringIO import StringIO as sio


# -----------------------------------------------------------------------------
class TestHd(th.HelpedTestCase):

    # -------------------------------------------------------------------------
    def test_hexdump(self):
        """
        Routine hexdump() reads one file and hexdumps it to another.
        """
        exp = "\n".join([
            " 54 77 61 73  20 62 72 69  6c 6c 69 67  20 61 6e 64    " +
            "Twas bri llig and",
            " 20 74 68 65  20 73 6c 69  74 68 65 20  74 6f 76 65    " +
            " the sli the tove",
            " 73 0a 44 69  64 20 67 79  72 65 20 61  6e 64 20 67    "
            "s.Did gy re and g",
            " 69 6d 62 6c  65 20 72 6f  75 6e 64 20  74 68 65 20    "
            "imble ro und the ",
            " 77 61 62 65  0a 41 6c 6c  20 6d 69 6d  73 79 20 77    "
            "wabe.All  mimsy w",
            " 65 72 65 20  74 68 65 20  62 6f 72 6f  67 72 6f 76    "
            "ere the  borogrov",
            " 65 73 0a 41  6e 64 20 74  68 65 20 6d  6f 6d 65 20    "
            "es.And t he mome ",
            " 72 61 74 68  73 20 6f 75  74 67 72 61  62 65 0a       "
            "raths ou tgrabe. ",
            ""
            ])

        q = sio("\n".join(["Twas brillig and the slithe toves",
                           "Did gyre and gimble round the wabe",
                           "All mimsy were the borogroves",
                           "And the mome raths outgrabe\n"]))
        z = sio()
        hd.hexdump(q, z)
        result = z.getvalue()
        z.close()
        q.close()

        self.assertEqual(exp, result,
                         "%s != %s" % (U.lquote(repr(exp)),
                                       U.lquote(repr(result))))

    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_hd_help(self):
        """
        Verify that 'hd --help' does the right thing
        """
        self.assertOptionHelp("hd", "Hexdump stdin or a file")

    # -------------------------------------------------------------------------
    # @unittest.skip("under construction")
    def test_which_module(self):
        """
        Verify that we're importing the right align module
        """
        self.assertModule('bscr.hd', __file__)

#!/usr/bin/env python
import bscr.xclean
from bscr import util
import os
import shutil
import StringIO as sio
import sys
import testhelp as th
import unittest

# -----------------------------------------------------------------------------
class TestXclean(unittest.TestCase):
    drmsg = 'Without --dryrun, would remove'
    testdir = "/tmp/test_xclean"
    tilde = [util.pj(testdir, 'xxx~'),
             util.pj(testdir, '.yyy~')]
    stilde = [util.pj(testdir, 'sub', 'basement~'),
              util.pj(testdir, 'sub', '.floor~')]
    ntilde = [util.pj(testdir, 'nomatch.txt')]
    nstilde = [util.pj(testdir, 'sub', 'nosuchfile')]
    testfiles = tilde + stilde + ntilde + nstilde

    # -------------------------------------------------------------------------
    def setUp(self):
        """
        Set up for each test in the suite.
        """
        if os.path.isdir(self.testdir):
            self.tearDown()
        os.makedirs(util.pj(self.testdir, 'sub'))
        for fp in self.testfiles:
            util.touch(fp)

    # -------------------------------------------------------------------------
    def tearDown(self):
        shutil.rmtree(self.testdir)
        
    # -------------------------------------------------------------------------
    def test_cleanup_dr_np_nr(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir, dryrun=True)
            result = getval()
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, True, True, True])

        self.assertIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, False, False])

    # -------------------------------------------------------------------------
    def test_cleanup_dr_np_r(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir, dryrun=True, recursive=True)
            result = getval()
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, True, True, True])

        self.assertIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, True, False])
        
    # -------------------------------------------------------------------------
    def test_cleanup_dr_p_nr(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir, dryrun=True, pattern="no.*")
            result = getval()
        
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, True, True, True])

        self.assertIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, False])

    # -------------------------------------------------------------------------
    def test_cleanup_dr_p_r(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir, dryrun=True, pattern="no.*",
                                recursive=True)
            result = getval()

        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, True, True, True])

        self.assertIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, True])

    # -------------------------------------------------------------------------
    def test_cleanup_ndr_np_nr(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir)
            result = getval()

        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [False, True, True, True])

        self.assertNotIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, False, False])

    # -------------------------------------------------------------------------
    def test_cleanup_ndr_np_r(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir, recursive=True)
            result = getval()

        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [False, True, False, True])

        self.assertNotIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, True, False])
            
    # -------------------------------------------------------------------------
    def test_cleanup_ndr_p_nr(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir, pattern="no.*")
            result = getval()

        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, False, True, True])

        self.assertNotIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, False])

    # -------------------------------------------------------------------------
    def test_cleanup_ndr_p_r(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.cleanup(self.testdir, pattern="no.*", recursive=True)
            result = getval()

        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, False, True, False])

        self.assertNotIn(self.drmsg, result)

        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, True])


    # -------------------------------------------------------------------------
    def test_find_files(self):
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
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-n', self.testdir])
            result = getval()
        self.assertIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, True, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, False, False])

    # -------------------------------------------------------------------------
    def test_main_dr_p_nr(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-n', '-p', 'no.*', self.testdir])
            result = getval()
        self.assertIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, True, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, False])
    
    # -------------------------------------------------------------------------
    def test_main_dr_np_r(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-n', '-r', self.testdir])
            result = getval()
        self.assertIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, True, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, True, False])

    # -------------------------------------------------------------------------
    def test_main_dr_p_r(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-n', '-p', 'no.*',
                              '-r', self.testdir])
            result = getval()
        self.assertIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, True, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, True])
        
    # -------------------------------------------------------------------------
    def test_main_ndr_np_nr(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', self.testdir])
            result = getval()
        self.assertNotIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [False, True, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, False, False])

    # -------------------------------------------------------------------------
    def test_main_ndr_np_r(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-r', self.testdir])
            result = getval()
        self.assertNotIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [False, True, False, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [True, False, True, False])
        
    # -------------------------------------------------------------------------
    def test_main_ndr_p_nr(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-p', 'no.*', self.testdir])
            result = getval()
        self.assertNotIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, False, True, True])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, False])

    # -------------------------------------------------------------------------
    def test_main_ndr_p_r(self):
        with th.StdoutExcursion() as getval:
            bscr.xclean.main(['bin/xclean', '-p', 'no.*', '-r', self.testdir])
            result = getval()
        self.assertNotIn(self.drmsg, result)
        self.verify_exists([self.tilde, self.ntilde, self.stilde, self.nstilde],
                           [True, False, True, False])
        self.verify_in([self.tilde, self.ntilde, self.stilde, self.nstilde],
                       result,
                       [False, True, False, True])

    # -------------------------------------------------------------------------
    def verify_exists(self, tv, rv):
        for fl, exp in zip(tv, rv):
            for fp in fl:
                self.assertEqual(exp, os.path.exists(fp),
                                 "expected '%s' to exist" % fp if exp else
                                 "expected '%s' to not exist" % fp)
        
    # -------------------------------------------------------------------------
    def verify_in(self, tv, text, rv):
        for fl, exp in zip(tv, rv):
            for fp in fl:
                if exp:
                    self.assertIn(fp, text,
                                  "expected '%s' in '%s'" % (fp, text))
                else:
                    self.assertNotIn(fp, text,
                                     "'%s' not expected in '%s'" % (fp, text))
        
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
    

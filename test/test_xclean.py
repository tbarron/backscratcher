import bscr.xclean
import os
import shutil
import StringIO as sio
import sys
import unittest

# -----------------------------------------------------------------------------
def pj(*args):
    """
    pathjoin -- convenience wrapper for os.path.join()
    """
    return os.path.join(*args)

# -----------------------------------------------------------------------------
def touch(filepath, times=None):
    """
    touch -- ensure file exists and update its *times* (atime, mtime)
    """
    open(filepath, 'a').close()
    os.utime(filepath, times)

class StdoutExcursion(object):
    def __init__(self):
        self.stdout = sys.stdout

    def __enter__(self):
        sys.stdout = sio.StringIO()
        return sys.stdout.getvalue

    def __exit__(self, type, value, traceback):
        sys.stdout.close()
        sys.stdout = self.stdout

# -----------------------------------------------------------------------------
class TestClean(unittest.TestCase):
    testdir = "/tmp/test_xclean"
    tilde = [pj(testdir, 'xxx~'),
             pj(testdir, '.yyy~')]
    stilde = [pj(testdir, 'sub', 'basement~'),
              pj(testdir, 'sub', '.floor~')]
    ntilde = [pj(testdir, 'nomatch.txt')]
    nstilde = [pj(testdir, 'sub', 'nosuchfile')]
    testfiles = tilde + stilde + ntilde + nstilde

    # -------------------------------------------------------------------------
    def setUp(self):
        os.makedirs(pj(self.testdir, 'sub'))
        for fp in self.testfiles:
            touch(fp)

    # -------------------------------------------------------------------------
    def tearDown(self):
        shutil.rmtree(self.testdir)
        
    # -------------------------------------------------------------------------
    def test_main_dr_np_nr(self):
        with StdoutExcursion() as sio:
            bscr.xclean.main(['bin/xclean', '-n', self.testdir])
            result = sio()
        self.assertIn('Without --dryrun, would remove', result)
        for fn in self.tilde:
            self.assertIn(fn, result,
                          "Expected '%s' in '%s'" % (fn, result))
        for fn in self.ntilde:
            self.assertNotIn(fn, result,
                             "Expected '%s' to not be in '%s'" % (fn, result))
        for fn in self.stilde:
            self.assertNotIn(fn, result,
                             "Expected '%s' to not be in '%s'" % (fn, result))
        for fn in self.nstilde:
            self.assertNotIn(fn, result,
                             "Expected '%s' to not be in '%s'" % (fn, result))

    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_main_dr_p_nr(self):
        self.fail('construction')
    
    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_main_dryrun_nopat_r(self):
        self.fail('construction')

    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_main_dryrun_pat_r(self):
        self.fail('construction')
        
    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_main_nodr_nopat(self):
        self.fail('construction')

    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_main_nodr_pat(self):
        self.fail('construction')
        
    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_main_nodr_nopat_r(self):
        self.fail('construction')

    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_main_nodr_pat_r(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_cleanup_dr_np(self):
        pass
    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_cleanup_dr_p(self):
        pass
    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_cleanup_ndr_np(self):
        pass
    # -------------------------------------------------------------------------
    @unittest.skip('construction')
    def test_cleanup_ndr_p(self):
        pass
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

        
        

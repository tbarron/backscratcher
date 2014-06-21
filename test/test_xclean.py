import bscr.xclean
import os
import shutil
import unittest

def pj(*args):
    return os.path.join(*args)

def touch(filepath):
    open(filepath, 'a').close()
    os.utime(filepath, None)

class TestClean(unittest.TestCase):
    testdir = "/tmp/test_xclean"
    testfiles = [pj(testdir, 'xxx~'),
                 pj(testdir, '.yyy~'),
                 pj(testdir, 'sub', 'basement~'),
                 pj(testdir, 'sub', '.floor~')]
    def setUp(self):
        os.makedirs(pj(self.testdir, 'sub'))
        for fp in self.testfiles:
            touch(fp)

    def tearDown(self):
        shutil.rmtree(self.testdir)
        
    def test_find_files(self):
        fl = bscr.xclean.find_files(self.testdir)
        self.assertIn(self.testfiles[0], fl,
                      "Expected %s in %s" % (self.testfiles[0], fl))
        self.assertIn(self.testfiles[1], fl,
                      "Expected %s in %s" % (self.testfiles[0], fl))

        self.assertNotIn(self.testfiles[2], fl,
                         "Expected %s not in %s" % (self.testfiles[0], fl))
        self.assertNotIn(self.testfiles[3], fl,
                         "Expected %s not in %s" % (self.testfiles[0], fl))
        
    def test_recursive(self):
        self.fail('construction')
        
    def test_xclean_pattern_def(self):
        self.fail('construction')
        
    def test_xclean_pattern_env(self):
        self.fail('construction')
        

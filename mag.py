#!/usr/bin/python
'''
Report the magnitude of large numbers.

SYNOPSIS

   mag [-b] <number>

EXAMPLES
   $ mag 17
   17 = 17.00 b

   $ mag -b 72346
   72346 = 70.65 Kib

   $ mag 23482045
   23482045 = 23.48 Mb

   $ mag 2348291384 -b
   2348291384 = 2.19 Gib
'''

import sys
import unittest

from optparse import *

def main(argv = None):
    if argv == None:
        argv = sys.argv

    p = OptionParser()
    # define options here
    p.add_option('-b', '--binary',
                 action='store_true', default=False, dest='binary',
                 help='div=1024 rather than 1000')
    (o, a) = p.parse_args(argv)

    if o.binary:
        divisor = 1024
        units = ['b', 'Kib', 'Mib', 'Gib', 'Tib', 'Pib', 'Eib', 'Zib', 'Yib']
    else:
        divisor = 1000
        units = ['b', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb']

    units.reverse()

    if len(a) < 2:
        return usage()
    else:
        val = float(a[1])
        u = units.pop()
        while divisor <= val:
            val /= divisor
            u = units.pop()

        return("%s = %3.2f %s" % (a[1], val, u))

def usage():
    return '''
    mag [-b] <number>
    '''

class MagTest(unittest.TestCase):
    def test_usage(self):
        a = main(['./mag'])
        assert(a == usage())

    def test_bit(self):
        a = main(['./mag', '999'])
        self.magtest('999 = 999.00 b')

    def test_bbit(self):
        a = main(['./mag', '999', '-b'])
        self.magtest('999 = 999.00 b')

    def test_kilo(self):
        a = main(['./mag', '98765'])
        self.magtest('98765 = 98.77 Kb')

    def test_bkilo(self):
        a = main(['./mag', '-b', '98765'])
        self.magtest('98765 = 96.45 Kib')

    def test_mega(self):
        a = main(['./mag', '98765432'])
        self.magtest('98765432 = 98.77 Mb')

    def test_bmega(self):
        a = main(['./mag', '-b', '98765432'])
        self.magtest('98765432 = 94.19 Mib')

    def test_giga(self):
        a = main(['./mag', '12398765432'])
        self.magtest('12398765432 = 12.40 Gb')

    def test_bgiga(self):
        a = main(['./mag', '-b', '12398765432'])
        self.magtest('12398765432 = 11.55 Gib')

    def test_tera(self):
        a = main(['./mag', '12390008765432'])
        self.magtest('12390008765432 = 12.39 Tb')

    def test_btera(self):
        self.magtest('12398700065432 = 11.28 Tib')

    def test_peta(self):
        self.magtest('17239090087685432 = 17.24 Pb')

    def test_bpeta(self):
        self.magtest('71233986700065432 = 63.27 Pib')

    def test_exa(self):
        self.magtest('41873239090087685432 = 41.87 Eb')

    def test_bexa(self):
        self.magtest('87271233986700065432 = 75.70 Eib')

    def test_zetta(self):
        self.magtest('43541873239090087685432 = 43.54 Zb')

    def test_bzetta(self):
        self.magtest('23487271233986700065432 = 19.89 Zib')

    def test_yotta(self):
        self.magtest('75843541873239090087685432 = 75.84 Yb')

    def test_byotta(self):
        self.magtest('39423487271233986700065432 = 32.61 Yib')

    def magtest(self, string):
        d = string.split()
        v = d[0]
        if 'i' in d[3]:
            args = ['./mag', '-b', v]
        else:
            args = ['./mag', v]
            
        a = main(args)
        try:
            assert(a == string)
        except AssertionError:
            print "\nexpected: '%s'" % a
            print "result:   '%s'" % string
        
if __name__ == '__main__':
    unittest.main()

#!/usr/bin/python
'''
pytool - produce skeletons for python programs

Usage:
   pytool <function> <arguments>
   'pytool help' for details
'''

# import getopt
import os
import pexpect
import re
import sys
# import tpbtools
import testhelp
import time
import unittest

from optparse import *
from tpbtools import *

# ---------------------------------------------------------------------------
def main(args):
    op = args[1]
    cmd = "pt_%s(args[2:])" % op
    eval(cmd)

# ---------------------------------------------------------------------------
def pt_help(args):
    '''help - show this list

    usage: pytool help [function-name]

    If a function name is given, show the functions __doc__ member.
    Otherwise, show a list of functions based on the first line of
    each __doc__ member.
    '''
    global d

    if 0 < len(args) and 'pt_%s' % args[0] in d:
        dname = 'pt_%s.__doc__' % args[0]
        x = eval(dname)
        print '\n    ' + x
        return

    for o in d:
        if 'pt_' in o:
            dname = 'pt_%s.__doc__' % o
            x = eval('%s.__doc__' % o)
            f = x.split('\n')[0]
            print '   %s' % f

#     if 'noname' in A.keys() and 'pt_%s' % A['noname'][0] in d:
#         dname = 'pt_%s.__doc__' % A['noname'][0]
#         x = eval(dname)
#         print x
#         return

#     for o in d:
#         if 'pt_' in o:
#             # dname = 'pt_%s.__doc__' % o
#             x = eval('%s.__doc__' % o)
#             f = x.split('\n')[0]
#             print '   ' + f

# ---------------------------------------------------------------------------
def pt_newpy(args):
    '''newpy - Create a new python program

    usage: pytool newpy <program-name>

    Creates files <program-name> and <program-name>.py with skeletal
    contents and makes both executable.
    '''

    p = OptionParser()
    (o, a) = p.parse_args(args)

    if a == []:
        raise Exception('usage: pytool newpy <program-name>')
    else:
        pname = a[0]
        are_we_overwriting([pname, '%s.py' % pname])

        f = open(pname, 'w')
        f.writelines(['#!/usr/bin/python\n',
                      'import sys\n',
                      'import %s\n' % pname,
                      '%s.main(sys.argv)\n' % pname])
        f.close()

        f = open('%s.py' % pname, 'w')
        f.writelines(['#!/usr/bin/python\n',
                      "'''\n",
                      '%s - program description\n' % pname,
                      "'''\n",
                      '\n',
                      # 'import getopt\n',
                      'import sys\n',
                      'import unittest\n',
                      '\n',
                      'from optparse import *\n',
                      '\n',
                      'def main(argv = None):\n',
                      '    if argv == None:\n',
                      '        argv = sys.argv\n',
                      '\n',
                      '    p = OptionParser()\n',
                      '    # define options here\n',
                      "    # p.add_option('-s', '--long',\n",
                      "    #              action='', default='',\n",
                      "    #              dest='', type='',\n",
                      "    #              help='')\n",
                      '    (o, a) = p.parse_args(argv)\n',
                      '\n',
                      '    # process arguments\n',
                      '    for a in args:\n',
                      '        process(a)\n',
                      '\n',
                      'class %sTest(unittest.TestCase):\n' %
                          pname.capitalize(),
                      '    def test_example(self):\n',
                      '        pass\n',
                      '\n',
                      'if __name__ == \'__main__\':\n',
                      '    unittest.main()\n'])
        f.close()

        os.chmod(pname, 0755)
        os.chmod('%s.py' % pname, 0755)

#     if 'noname' not in A.keys():
#         fatal('usage: pytool newpy <program-name>')
#     else:
#         pname = A['noname'][0]
#         are_we_overwriting([pname, '%s.py' % pname])
                
#         p = open(pname, 'w')
#         p.write('#!/usr/bin/python\n')
#         p.write('import sys\n')
#         p.write('import %s\n' % pname)
#         p.write('%s.main(sys.argv)\n' % pname)
#         p.close()

#         p = open('%s.py' % pname, 'w')
#         p.writelines(['#!/usr/bin/python\n',
#                       "'''\n",
#                       '%s - program description\n' % pname,
#                       "'''\n",
#                       '\n',
#                       'import getopt\n',
#                       'import sys\n',
#                       'import unittest\n',
#                       '\n',
#                       'from optparse import *\n',
#                       '\n',
#                       'def main(argv = None):\n',
#                       '    if argv == None:\n',
#                       '        argv = sys.argv\n',
#                       '\n',
#                       '    p = OptionParser()\n',
#                       '    # define options here\n',
#                       "    # p.add_option('-s', '--long',\n",
#                       "    #              action='', default='',\n",
#                       "    #              dest='', type='',\n",
#                       "    #              help='')\n",
#                       '    (o, a) = p.parse_args(argv)\n',
#                       '\n',
#                       '    # process arguments\n',
#                       '    for a in args:\n',
#                       '        process(a)\n',
#                       '\n',
#                       'class %sTest(unittest.TestCase):\n' %
#                           pname.capitalize(),
#                       '    def test_example(self):\n',
#                       '        pass\n',
#                       '\n',
#                       'if __name__ == \'__main__\':\n',
#                       '    unittest.main()\n'])
#         p.close()

#         os.chmod(pname, 0755)
#         os.chmod('%s.py' % pname, 0755)
        
# ---------------------------------------------------------------------------
def pt_newtool(args):
    '''newtool - Create a new tool-style program

    usage: pytool newtool <program-name> <prefix>

    Creates files <program-name> and <program-name>.py with skeletal
    contents and makes both executable. The structure of the program
    is such that it is easy to add and describe new subfunctions.
    '''

    p = OptionParser()
    (o, a) = p.parse_args(args)

    if a == [] or len(a) != 2:
        raise Exception('usage: pytool newtool <program-name> <prefix>')
    else:
        pname = a[0]
        prefix = a[1]
        are_we_overwriting([pname, '%s.py' % pname])

        f = open(pname, 'w')
        f.writelines(['#!/usr/bin/python\n',
                      'import sys\n',
                      'import %s\n' % pname,
                      '%s.main(sys.argv)\n' % pname])
        f.close()

        f = open('%s.py' % pname, 'w')
        f.writelines(['#!/usr/bin/python\n',
                      "'''\n",
                      '%s - program description\n' % pname,
                      "'''\n",
                      '\n',
                      'import re\n',
                      'import sys\n',
                      'import unittest\n',
                      '\n',
                      'from optparse import *\n',
                      '\n',
                      '# -------------------------------------------------'
                          + '--------------------------\n',
                      'def main(args):\n',
                      '    op = args[1]\n',
                      '    cmd = "%s_%%s(args[2:])" %% op\n' % prefix,
                      '    eval(cmd)\n',
                      '\n',
                      '# -------------------------------------------------'
                          + '--------------------------\n',
                      'def %s_help(args):\n' % prefix,
                      "    '''help - show this list\n",
                      '\n',
                      '    usage: %s help [function-name]\n' % pname,
                      '\n',
                      '    If a function name is given, show the'
                         + ' __doc__ member of the function.\n',
                      '    Otherwise, show a list of functions based on'
                         + ' the first line of\n',
                      '    each __doc__ member.\n',
                      "    '''\n",
                      '    global d\n',
                      '\n',
                      '    p = OptionParser()\n',
                      "    # p = add_option('-e', '--exec',\n",
                      "    #                action='store_true',"
                         + " default=False, dest='xable',\n",
                      "    #                help='otherwise dryrun')\n",
                      '    (o, a) = p.parse_args(args)',
                      '\n',
                      "    if 0 < len(a) and '%s_%%s' %% a[0] in d:\n"
                          % prefix,
                      "        x = eval('%s_%%s.__doc__' %% a[0])\n"
                          % (prefix),
                      "        print '\\n    ' + x\n",
                      '        return\n',
                      '\n',
                      '    for fcn in d:\n',
                      "        if '%s_' in fcn:\n" % prefix,
                      "            x = eval('%%s.__doc__' % fcn)\n",
                      "            f = x.split('\\n')[0]\n",
                      "            print '   %%s' % f\n"
                      ])
        f.close()

        for fname in [pname, '%s.py' % pname]:
            os.chmod(fname, 0755)

#     if 'noname' not in A.keys():
#         fatal('usage: pytool newtool <program-name> <prefix>')
#     elif len(A['noname']) != 2:
#         fatal('usage: pytool newtool <program-name> <prefix>')
#     else:
#         pname = A['noname'][0]
#         prefix = A['noname'][1]
#         are_we_overwriting([pname, '%s.py' % pname])

#         p = open(pname, 'w')
#         p.write('#!/usr/bin/python\n')
#         p.write('import sys\n')
#         p.write('import %s\n' % pname)
#         p.write('%s.main(sys.argv)\n' % pname)
#         p.close()

#         p = open('%s.py' % pname, 'w')
#         p.write('#!/usr/bin/python\n')
#         p.write("'''\n")
#         p.write('%s - program description\n' % pname)
#         p.write("'''\n")
#         p.write('\n')
#         p.write('import getopt\n')
#         p.write('import re\n')
#         p.write('import sys\n')
#         p.write('import unittest\n')
#         p.write('\n')
#         p.write("# ----------------------------------------------------"
#                 + "-----------------------\n")
#         p.write('def main(args):\n')
#         p.write('    A = ahash(args[2:])\n')
#         p.write('    try:\n')
#         p.write('        eval("%s_%%s(A)" %% args[1])\n' % prefix)
#         p.write('    except IndexError:\n')
#         p.write('        adm_help({})\n')
#         p.write('\n')
#         p.write("# ----------------------------------------------------"
#                 + "-----------------------\n")
#         p.write('def %s_help(A):\n' % prefix)
#         p.write("    '''help - show this list\n")
#         p.write("\n")
#         p.write("    usage: %s help [function-name]\n" % pname)
#         p.write("\n")
#         p.write("    If a function name is given, show the"
#                 + " functions __doc__ member.\n")
#         p.write("    Otherwise, show a list of functions based on"
#                 + " the first line of\n")
#         p.write("    each __doc__ member.\n")
#         p.write("    '''\n")
#         p.write("    global d\n")
#         p.write("\n")
#         p.write("    if 0 < len(A)"
#                 + " and '%s_%%s' %% A[0] in d:\n" % prefix)
#         p.write("        dname = '%s_%%s.__doc__' %% A[0]\n"
#                 % prefix)
#         p.write("        x = eval(dname)\n")
#         p.write("        print '\\n    ' + x\n")
#         p.write("        return\n")
#         p.write("\n")
#         p.write("    for o in d:\n")
#         p.write("        if '%s_' in o:\n" % (prefix))
#         p.write("            x = eval('%s.__doc__' % o)\n")
#         p.write("            f = x.split('\\n')[0]\n")
#         p.write("            print '    ' + f\n")
#         p.write('\n')
#         p.write("# ----------------------------------------------------"
#                 + "-----------------------\n")
#         p.write("def ahash(arglist):\n")
#         p.write("    mylist = []\n")
#         p.write("    mylist.extend(arglist)\n")
#         p.write("\n")
#         p.write("    rval = {}\n")
#         p.write("    for i in range(0,len(mylist)):\n")
#         p.write("        item = mylist[i]\n")
#         p.write("        if re.search(r'^!', item):\n")
#         p.write("            pass\n")
#         p.write("        elif re.search(r'^-', item):\n")
#         p.write("            k = item.strip('-')\n")
#         p.write("            if i < len(mylist)-1:\n")
#         p.write("                v = mylist[i+1]\n")
#         p.write("                if not re.search(r'^-', v):\n")
#         p.write("                    mylist[i+1] = '!' + mylist[i+1]\n")
#         p.write("                    rval[k] = v\n")
#         p.write("                else:\n")
#         p.write("                    rval[k] = True\n")
#         p.write("            else:\n")
#         p.write("                rval[k] = True\n")
#         p.write("        else:\n")
#         p.write("            try:\n")
#         p.write("                rval['noname'].append(item)\n")
#         p.write("            except KeyError:\n")
#         p.write("                rval['noname'] = [item]\n")
#         p.write("\n")
#         p.write("    return rval\n")
#         p.write("                    \n")
#         p.write("# ----------------------------------------------------"
#                 + "-----------------------\n")
#         p.write('class %sTest(unittest.TestCase):\n' % pname)
#         p.write('    def test_example(self):\n')
#         p.write('        pass\n')
#         p.write('\n')
#         p.write("# ----------------------------------------------------"
#                 + "-----------------------\n")
#         p.write("global d\n")
#         p.write("d = dir()\n")
#         p.write('if __name__ == \'__main__\':\n')
#         p.write('    unittest.main()\n')
#         p.close()

#         os.chmod(pname, 0755)
#         os.chmod('%s.py' % pname, 0755)
        
# ---------------------------------------------------------------------------
# def ahash(arglist):
#     mylist = []
#     mylist.extend(arglist)

#     rval = {}
#     for i in range(0,len(mylist)):
#         item = mylist[i]
#         if re.search(r'^!', item):
#             pass
#         elif re.search(r'^-', item):
#             k = item.strip('-')
#             if i < len(mylist)-1:
#                 v = mylist[i+1]
#                 if not re.search(r'^-', v):
#                     mylist[i+1] = '!' + mylist[i+1]
#                     rval[k] = v
#                 else:
#                     rval[k] = True
#             else:
#                 rval[k] = True
#         else:
#             try:
#                 rval['noname'].append(item)
#             except KeyError:
#                 rval['noname'] = [item]

#     return rval
                    
# ---------------------------------------------------------------------------
def are_we_overwriting(flist):
    already = []
    for f in flist:
        if os.path.exists(f):
            already.append(f)

    if len(already) < 1:
        return
    elif len(already) < 2:
        report = '%s already exists' % already[0]
    elif len(already) < 3:
        report = '%s and %s already exist' % (already[0], already[1])
    else:
        report = ', '.join(already)

        sep = ', and '
        for a in already:
            report = sep + a + report
            sep = ', '
        report = report[2:]
        
    answer = raw_input('%s. Are you sure? > ' % report)

    if not re.search(r'^\s*[Yy]', answer):
        sys.exit(1)
                           
# ---------------------------------------------------------------------------
class PytoolTest(unittest.TestCase):
    # -----------------------------------------------------------------------
    def test_newpy_x(self):
        '''
        Run "pytool newpy xyzzy". Verify that xyzzy and xyzzy.py are created
        and have the right contents.
        '''
        prepare_tests()
        safe_unlink(['xyzzy', 'xyzzy.py'])
        S = pexpect.spawn('../pytool newpy xyzzy')
        try:
            S.expect(pexpect.EOF)
        except pexpect.TIMEOUT:
            fail('pytool should not prompt in this case')
        assert(os.path.exists('xyzzy'))
        assert(os.path.exists('xyzzy.py'))
        
        got = contents('xyzzy')
        expected = expected_xyzzy()
        testhelp.expectVSgot(expected, got)

        got = contents('xyzzy.py')
        expected = expected_xyzzy_py()
        testhelp.expectVSgot(expected, got)

    # -----------------------------------------------------------------------
    def test_newpy_overwriting_no(self):
        '''
        Run "pytool newpy xyzzy" when xyzzy already exists. Verify
        that confirmation is requested. Answer "no" and verify that
        the existing file is not overwritten.
        '''
        prepare_tests()
        safe_unlink(['xyzzy', 'xyzzy.py'])
        writefile('xyzzy', ['original xyzzy\n'])
        writefile('xyzzy.py', ['original xyzzy.py\n'])
        S = pexpect.spawn('../pytool newpy xyzzy')
        which = S.expect([r'you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')
        else:
            self.fail('should have asked about overwriting xyzzy')
            
        expected = ['original xyzzy\n']
        got = contents('xyzzy')
        assert(expected == got)

        expected = ['original xyzzy.py\n']
        got = contents('xyzzy.py')
        assert(expected == got)

    # -----------------------------------------------------------------------
    def test_newpy_overwriting_yes(self):
        '''
        Run "pytool newpy xyzzy" when xyzzy, xyzzy.py already exist.
        Verify that confirmation is requested. Answer "yes" and verify
        that the existing file IS overwritten.
        '''
        prepare_tests()
        safe_unlink(['xyzzy', 'xyzzy.py'])
        writefile('xyzzy', ['original xyzzy\n'])
        S = pexpect.spawn('../pytool newpy xyzzy')
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('yes')
            S.expect(pexpect.EOF)
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')
        else:
            self.fail('should have asked about overwriting xyzzy')
            
        expected = expected_xyzzy()
        got = contents('xyzzy')
        testhelp.expectVSgot(expected, got)

        expected = expected_xyzzy_py()
        got = contents('xyzzy.py')
        testhelp.expectVSgot(expected, got)

    # -----------------------------------------------------------------------
    def test_newtool(self):
        '''
        Run "pytool newtool testtool tt". Verify that testtool and testtool.py
        are created and have the right contents.
        '''
        prepare_tests()
        safe_unlink(['testtool', 'testtool.py'])
        S = pexpect.spawn('../pytool newtool testtool tt')
        S.logfile = sys.stdout
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
            self.fail('should not have asked about overwriting')
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')
            
        expected = expected_testtool()
        got = contents('testtool')
        testhelp.expectVSgot(expected, got)

        expected = expected_testtool_py()
        got = contents('testtool.py')
        testhelp.expectVSgot(expected, got)

    # -----------------------------------------------------------------------
    def test_help(self):
        '''
        Run "pytool help". Verify that the output is correct
        '''
        prepare_tests()
        outputs = ['testtool', 'testtool.py', 'xyzzy', 'xyzzy.py']
        safe_unlink(outputs)
        S = pexpect.spawn('../pytool help')
        # S.logfile = sys.stdout
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
            self.fail('should not have asked about overwriting')
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')
            
        # !@! check that none of the outputs exist
        for file in outputs:
            assert(not os.path.exists(file))
            
    # -----------------------------------------------------------------------
    def test_help_newpy(self):
        '''
        Run "pytool help newpy". Verify that the output is correct.
        '''
        prepare_tests()
        S = pexpect.spawn('../pytool help newpy')
        # S.logfile = sys.stdout
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
            self.fail('should not have asked about overwriting')
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')

        got = S.before.split('\r\n')
        expected = ['',
                    '    newpy - Create a new python program',
                    '',
                    '    usage: pytool newpy <program-name>',
                    '',
                    '    Creates files <program-name> and <program-name>.py'
                       + ' with skeletal',
                    '    contents and makes both executable.',
                    '    ',
                    '']
        testhelp.expectVSgot(expected, got)
        
    # -----------------------------------------------------------------------
    def test_help_newtool(self):
        '''
        Run "pytool help newtool". Verify that the output is correct.
        '''
        prepare_tests()
        S = pexpect.spawn('../pytool help newtool')
        # S.logfile = sys.stdout
        which = S.expect([r'Are you sure\? >',
                          'Error:',
                          pexpect.EOF])
        if which == 0:
            S.sendline('no')
            S.expect(pexpect.EOF)
            self.fail('should not have asked about overwriting')
        elif which == 1:
            print S.before + S.after
            self.fail('unexpected exception')

        got = S.before.split('\r\n')
        expected = ['',
                    '    newtool - Create a new tool-style program',
                    '',
                    '    usage: pytool newtool <program-name> <prefix>',
                    '',
                    '    Creates files <program-name> and <program-name>.py'
                        + ' with skeletal',
                    '    contents and makes both executable. The structure'
                        + ' of the program',
                    '    is such that it is easy to add and describe'
                        + ' new subfunctions.',
                    '    ',
                    '']
        testhelp.expectVSgot(expected, got)
        
# ---------------------------------------------------------------------------
def cleanup():
    global intestdir
    print "intestdir = %s" % intestdir
    try:
        if intestdir:
            print os.getcwd()
            os.chdir('..')
            print os.getcwd()
            rmrf('./pytool_test')
    except NameError:
        print("cleanup_tests: Nothing to clean up")

# ---------------------------------------------------------------------------
def expected_testtool():
    expected = ['#!/usr/bin/python\n',
                'import sys\n',
                'import testtool\n',
                'testtool.main(sys.argv)\n']
    return expected

# ---------------------------------------------------------------------------
def expected_testtool_py():
    expected = ['#!/usr/bin/python\n',
                "'''\n",
                'testtool - program description\n',
                "'''\n",
                '\n',
                'import re\n',
                'import sys\n',
                'import unittest\n',
                '\n',
                'from optparse import *\n',
                '\n',
                '# ----------------------------------------------------'
                    + '-----------------------\n',
                'def main(args):\n',
                '    op = args[1]\n',
                '    cmd = "tt_%s(args[2:])" % op\n',
                '    eval(cmd)\n',
                '\n',
                '# ----------------------------------------------------'
                    + '-----------------------\n',
                'def tt_help(args):\n',
                "    '''help - show this list\n",
                '\n',
                '    usage: testtool help [function-name]\n',
                '\n',
                '    If a function name is given, show the __doc__'
                    + ' member of the function.\n',
                '    Otherwise, show a list of functions based on the'
                    + ' first line of\n',
                '    each __doc__ member.\n',
                "    '''\n",
                '    global d\n',
                '\n',
                '    p = OptionParser()\n',
                "    # p = add_option('-e', '--exec',\n",
                "    #                action='store_true', default=False, dest='xable',\n",
                "    #                help='otherwise dryrun')\n",
                '    (o, a) = p.parse_args(args)\n',
                "    if 0 < len(a) and 'tt_%s' % a[0] in d:\n",
                "        x = eval('tt_%s.__doc__' % a[0])\n",
                "        print '\\n    ' + x\n",
                '        return\n',
                '\n',
                '    for fcn in d:\n',
                "        if 'tt_' in fcn:\n",
                "            x = eval('%%s.__doc__' % fcn)\n",
                "            f = x.split('\\n')[0]\n",
                "            print '   %%s' % f\n"]
    return expected

# ---------------------------------------------------------------------------
def expected_xyzzy():
    expected = ['#!/usr/bin/python\n',
                'import sys\n',
                'import xyzzy\n',
                'xyzzy.main(sys.argv)\n']
    return expected

# ---------------------------------------------------------------------------
def expected_xyzzy_py():
    expected = ['#!/usr/bin/python\n',
                "'''\n",
                'xyzzy - program description\n',
                "'''\n",
                '\n',
                # 'import getopt\n',
                'import sys\n',
                'import unittest\n',
                '\n',
                'from optparse import *\n',
                '\n',
                'def main(argv = None):\n',
                '    if argv == None:\n',
                '        argv = sys.argv\n',
                '\n',
                '    p = OptionParser()\n',
                '    # define options here\n',
                "    # p.add_option('-s', '--long',\n",
                "    #              action='', default='',\n",
                "    #              dest='', type='',\n",
                "    #              help='')\n",
                '    (o, a) = p.parse_args(argv)\n',
                '\n',
                '    # process arguments\n',
                '    for a in args:\n',
                '        process(a)\n',
                '\n',
                'class XyzzyTest(unittest.TestCase):\n',
                '    def test_example(self):\n',
                '        pass\n',
                '\n',
                "if __name__ == '__main__':\n",
                '    unittest.main()\n',]
    return expected

# ---------------------------------------------------------------------------
def prepare_tests():
    global intestdir
    try:
        if intestdir:
            # print "prepare_tests(1): %s" % os.getcwd()
            return
    except NameError:
        intestdir = False

    if os.path.basename(os.getcwd()) == 'pytool_test':
        intestdir = True
        # print "prepare_tests(2): %s" % os.getcwd()
        return
    
    if not os.path.exists('./pytool_test'):
        os.mkdir('./pytool_test')

    os.chdir('./pytool_test')
    intestdir = True
        
    # print "prepare_tests(3): %s" % os.getcwd()

# ---------------------------------------------------------------------------
global d
d = dir()
if __name__ == '__main__':
    if not testhelp.main(sys.argv, 'PytoolTest'):
        cleanup()

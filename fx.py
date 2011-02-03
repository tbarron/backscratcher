#!/usr/bin/python
"""
commnd effects

The simplest use is to apply a command to a sequence of files. For example,

  fx -c "echo %" file1 file2 file3

will expand to

  echo file1
  echo file2
  echo file3

USAGE

 fx [-n] [-q] -c <command> {file1 file2 ... filen | -i low:high}
 fx [-n] [-q] -x -c <command>
 fx [-n] [-q] -e s/foo/bar/ file1 file2 ... filen

If -i is used to specify a range of numbers instead of a list of
files, the numbers will be substituted for the '%' in the command. If
-x is used, strings from stdin will be collected into bundles and the
bundles will be substituted for '%' in the command.

If the -e option is used, the s/// operation is applied to each
filename in the list and the files are renamed.

If -n is used, the commands generated are displayed but not run.

If -q is used, the commands are run without being displayed first.

OPTIONS

 -c <command>  

Specify the command to be run.

 -e s/<old>/<new>/

Specify a substitute operation to be applied to a list of filenames.

 -i <low>:<high>

Specify a list of numbers to be substituted for '%' in a command string.

 -n

Just do a dryrun.

 -q

Be quiet -- don't echo commands before running them.

 -x

Bundle strings from stdin into groups that won't overrun the shell
command buffer and substitute the bundles for '%' in the command. This
is like xargs, except it facilitates putting the list from stdin in
the middle of the command rather than only being able to put it at the
end.

LICENSE

Copyright (C) 1995 - <the end of time>  Tom Barron
  tom.barron@comcast.net
  177 Crossroads Blvd
  Oak Ridge, TN  37830

This software is licensed under the CC-GNU GPL. For the full text of
the license, see http://creativecommons.org/licenses/GPL/2.0/

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import glob
import os
import pdb
import re
import sys
import StringIO
import textwrap
import unittest

from optparse import *

# ---------------------------------------------------------------------------
def main(argv = None):
    """
    Select the function to apply based on the command line options.
    """
    if argv == None:
        argv = sys.argv

    p = OptionParser()
    p.add_option('-c', '--command',
                 action='store', default='', dest='cmd', type='string',
                 help='command to apply to all arguments')
    p.add_option('-d', '--debug',
                 action='store_true', default = False, dest='debug',
                 help='run under the debugger')
    p.add_option('-e', '--edit',
                 action='store', default='', dest='edit', type='string',
                 help='file rename expression applied to all arguments')
    p.add_option('-i', '--integer',
                 action='store', default='', dest='irange', type='string',
                 help='low:high -- generate range of numbers')
    p.add_option('-n', '--dryrun',
                 action='store_true', default=False, dest='dryrun',
                 help='dryrun or execute')
    p.add_option('-q', '--quiet',
                 action='store_true', default=False, dest='quiet',
                 help="don't echo commands, just run them")
    p.add_option('-x', '--xargs',
                 action='store_true', default=False, dest='xargs',
                 help='batch input from stdin into command lines like xargs')
    (o, a) = p.parse_args(argv)

    if o.debug:
        pdb.set_trace()

    Home = os.getenv('HOME')

    if o.edit != '':
        SubstRename(o, a[1:])
    elif o.irange != '':
        IterateCommand(o, a[1:])
    elif o.xargs:
        BatchCommand(o, a[1:])
    elif o.cmd != '':
        SubstCommand(o, a[1:])
    else:
        Usage()

# ---------------------------------------------------------------------------
def expand(cmd):
    """
    Expand environment variables and user notation in a command string.
    """
    return os.path.expandvars(os.path.expanduser(cmd))

# ---------------------------------------------------------------------------
def BatchCommand(options, arglist):
    """
    Bundle arguments into command lines similarly to xargs.

    Unlink xargs, this version allows for static values following the
    list of arguments on each command line.
    """
    for cmd in xargs_wrap(options.cmd, sys.stdin):
        psys(cmd, options)

# ---------------------------------------------------------------------------
def IterateCommand(options, arglist):
    """
    Run a command once for each of a sequence of numbers.

    Possible enhancements would be to handle low/high/step tuples, and
    to handle an arbitrary comma delimited list of values.
    """
    (low, high) = options.irange.split(':')
    for idx in range(int(low), int(high)):
        cmd = expand(re.sub('%', str(idx), options.cmd))
        psys(cmd, options)

# ---------------------------------------------------------------------------
def psys(cmd, options):
    """
    Handle a command subject to the dryrun and quiet members of options.

    !dryrun & !quiet: Display the command, then run it
    !dryrun & quiet: Run the command without running it
    dryrun & !quiet: Display the command without running it
    dryrun & quiet: Display the command without running it
    """
    # print("psys: cmd = '%s', dryrun = %s, quiet = %s"
    #       % (cmd, options.dryrun, options.quiet))
    if options.dryrun:
        print("would do '%s'" % cmd)
    elif options.quiet:
        # os.system(cmd)
        f = os.popen(cmd, 'r')
        sys.stdout.write(f.read())
        f.close()
    else:
        print(cmd)
        # os.system(cmd)
        f = os.popen(cmd, 'r')
        sys.stdout.write(f.read())
        f.close()
        
# ---------------------------------------------------------------------------
def SubstCommand(options, arglist):
    """
    Run the command for each filename in arglist.
    """
    for filename in arglist:
        cmd = expand(re.sub('%', filename, options.cmd))
        psys(cmd, options)
        
# ---------------------------------------------------------------------------
def SubstRename(options, arglist):
    """
    Create and run a rename command based on a s/old/new/ expression.
    """
    p = options.edit
    s = p.split(p[1])
    for filename in arglist:
        newname = re.sub(s[1], s[2], filename)
        print("rename %s %s" % (filename, newname))
        if not options.dryrun:
            os.rename(filename, newname)
        
# ---------------------------------------------------------------------------
def Usage():
    """
    Report program usage.
    """
    print
    print('  fx [-n] -c <command> <files> (% in the command becomes filename)')
    print('          -e s/old/new/ <files> (rename file old to new name)')
    print('          -i low:high <command> (% ranges from low to high-1)')
    print
    
# ---------------------------------------------------------------------------
def xargs_wrap(cmd, input):
    """
    Do xargs wrapping to cmd, distributing args from file input across
    command lines.
    """
    tcmd = cmd
    rval = []
    for line in input:
        l = line.strip()
        for item in l.split(" "):
            tcmd = expand(re.sub('%', item + ' %', tcmd))
            pending = True

            if 240 < len(tcmd):
                tcmd = re.sub(r'\s*%\s*', '', tcmd)
                rval.append(tcmd)
                pending = False
                tcmd = cmd
    if pending:
        tcmd = re.sub(r'\s*%\s*', '', tcmd)
        rval.append(tcmd)
    return(rval)

# ---------------------------------------------------------------------------
class FxTest(unittest.TestCase):
    """
    Tests for code in fx.py.
    """
    # -----------------------------------------------------------------------
    def test_usage(self):
        """
        Test the Usage routine.
        """
        self.redirect()
        Usage()
        exp = '\n'
        exp += '  fx [-n] -c <command> <files> (% in the command becomes'
        exp += ' filename)\n'
        exp += '          -e s/old/new/ <files> (rename file old to new'
        exp += ' name)\n'
        exp += '          -i low:high <command> (% ranges from low to'
        exp += ' high-1)\n'
        exp += '\n'
        actual = self.undirect()
        assert(actual == exp)
  
    # -----------------------------------------------------------------------
    def test_expand(self):
        """
        Test the expand routine.
        """
        home = os.environ['HOME']
        input = '~/$PWD'
        expected = '%s/%s' % (home, os.environ['PWD'])
        actual = expand(input)
        assert(expected == actual)

    # -----------------------------------------------------------------------
    def test_psys_neither(self):
        """
        Test routine psys with dryrun False and quiet False.
        """
        self.redirect()
        v = Values({'dryrun': False, 'quiet': False})
        psys('ls -d ../fx.py', v)
        actual = self.undirect()
        expected = "ls -d ../fx.py\n../fx.py\n"
        assert(expected == actual)

    # -----------------------------------------------------------------------
    def test_psys_dryrun(self):
        """
        Test routine psys with dryrun True and quiet False.
        """
        self.redirect()
        v = Values({'dryrun': True, 'quiet': False})
        psys('ls -d nosuchfile', v)
        actual = self.undirect()
        expected = "would do 'ls -d nosuchfile'\n"
        assert(expected == actual)
    
    # -----------------------------------------------------------------------
    def test_psys_quiet(self):
        """
        Test routine psys with dryrun False and quiet True.
        """
        self.redirect()
        v = Values({'dryrun': False, 'quiet': True})
        psys('ls -d ../fx.py', v)
        actual = self.undirect()
        expected = "../fx.py\n"
        self.check_result(expected == actual, expected, actual)

    # -----------------------------------------------------------------------
    def test_psys_both(self):
        """
        Test routine psys with dryrun True and quiet True.
        """
        self.redirect()
        v = Values({'dryrun': True, 'quiet': True})
        psys('ls -d fx.py', v)
        actual = self.undirect()
        expected = "would do 'ls -d fx.py'\n"
        assert(expected == actual)

    # -----------------------------------------------------------------------
    def test_BatchCommand_neither(self):
        """
        Test BatchCommand with dryrun and quiet both False.
        """
        self.into_testdir()
        inlist = range(1, 250)
        f = open('tmpfile', 'w')
        for x in inlist:
            f.write(str(x) + '\n')
        f.close()
        
        v = Values({'dryrun': False, 'quiet': False, 'xargs': True,
                    'cmd': 'echo %'})

        x = StringIO.StringIO(" ".join([str(z) for z in range(1, 250)]))
        q = xargs_wrap("echo %", x)
        exp = ''
        for chunk in q:
            exp += chunk + '\n'
            exp += re.sub('^echo ', '', chunk) + '\n'

        self.indirect('tmpfile')
        self.redirect()
        BatchCommand(v, [])
        actual = self.undirect()

        self.check_result(exp == actual, exp, actual)
        
    # -----------------------------------------------------------------------
    def test_BatchCommand_quiet(self):
        """
        Test BatchCommand with dryrun False and quiet True.
        """
        self.into_testdir()
        inlist = range(1, 250)
        f = open('tmpfile', 'w')
        for x in inlist:
            f.write(str(x) + '\n')
        f.close()
        
        v = Values({'dryrun': False, 'quiet': True, 'xargs': True,
                    'cmd': 'echo %'})

        x = StringIO.StringIO(" ".join([str(z) for z in range(1, 250)]))
        q = xargs_wrap("echo %", x)
        exp = ''
        for chunk in q:
            # exp += chunk + '\n'
            exp += re.sub('^echo ', '', chunk) + '\n'

        self.indirect('tmpfile')
        self.redirect()
        BatchCommand(v, [])
        actual = self.undirect()

        self.check_result(exp == actual, exp, actual)
        
    # -----------------------------------------------------------------------
    def test_BatchCommand_dryrun(self):
        """
        Test BatchCommand with dryrun True and quiet False.
        """
        self.into_testdir()
        inlist = range(1, 250)
        f = open('tmpfile', 'w')
        for x in inlist:
            f.write(str(x) + '\n')
        f.close()
        
        v = Values({'dryrun': True, 'quiet': False, 'xargs': True,
                    'cmd': 'echo %'})

        x = StringIO.StringIO(" ".join([str(z) for z in range(1, 250)]))
        q = xargs_wrap("echo %", x)
        exp = ''
        for chunk in q:
            exp += re.sub('^echo ', "would do 'echo ", chunk) + "'\n"

        self.indirect('tmpfile')
        self.redirect()
        BatchCommand(v, [])
        actual = self.undirect()

        self.check_result(exp == actual, exp, actual)
        
    # -----------------------------------------------------------------------
    def test_BatchCommand_both(self):
        """
        Test BatchCommand with dryrun True and quiet True.
        """
        self.into_testdir()
        inlist = range(1, 250)
        f = open('tmpfile', 'w')
        for x in inlist:
            f.write(str(x) + '\n')
        f.close()
        
        v = Values({'dryrun': True, 'quiet': False, 'xargs': True,
                    'cmd': 'echo %'})

        x = StringIO.StringIO(" ".join([str(z) for z in range(1, 250)]))
        q = xargs_wrap("echo %", x)
        exp = ''
        for chunk in q:
            exp += re.sub('^echo ', "would do 'echo ", chunk) + "'\n"

        self.indirect('tmpfile')
        self.redirect()
        BatchCommand(v, [])
        actual = self.undirect()

        self.check_result(exp == actual, exp, actual)
        
    # -----------------------------------------------------------------------
    def test_IterateCommand_neither(self):
        """
        Test IterateCommand() with dryrun False and quiet False.
        """
        self.into_testdir()
        v = Values({'dryrun': False, 'quiet': False,
                    'cmd': 'echo %',
                    'irange': '5:10'})
        exp = "".join(["echo %d\n%d\n" % (i, i) for i in range(5, 10)])

        self.redirect()
        IterateCommand(v, [])
        actual = self.undirect()
        self.check_result(exp == actual, exp, actual)
    
    # -----------------------------------------------------------------------
    def test_IterateCommand_quiet(self):
        """
        Test IterateCommand() with dryrun False and quiet True.
        """
        # pdb.set_trace()
        self.into_testdir()
        v = Values({'dryrun': False, 'quiet': True,
                    'cmd': 'echo %',
                    'irange': '5:10'})
        exp = "".join(["%d\n" % i for i in range(5, 10)])

        self.redirect()
        IterateCommand(v, [])
        actual = self.undirect()
        self.check_result(exp == actual, exp, actual)
    
    # -----------------------------------------------------------------------
    def test_IterateCommand_dryrun(self):
        """
        Test IterateCommand() with dryrun True and quiet False.
        """
        self.into_testdir()
        v = Values({'dryrun': True, 'quiet': False,
                    'cmd': 'echo %',
                    'irange': '5:10'})
        exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

        self.redirect()
        IterateCommand(v, [])
        actual = self.undirect()

        self.check_result(exp == actual, exp, actual)
    
    # -----------------------------------------------------------------------
    def test_IterateCommand_both(self):
        """
        Test IterateCommand() with dryrun True and quiet True.
        """
        self.into_testdir()
        v = Values({'dryrun': True, 'quiet': True,
                    'cmd': 'echo %',
                    'irange': '5:10'})
        exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

        self.redirect()
        IterateCommand(v, [])
        actual = self.undirect()

        self.check_result(exp == actual, exp, actual)
        
    # -----------------------------------------------------------------------
    def test_SubstCommand_neither(self):
        """
        Test SubstCommand() with dryrun False and quiet False.
        """
        self.into_testdir()
        v = Values({'dryrun': False, 'quiet': False, 'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(['ls %s\n%s\n' % (x, x) for x in a])
        self.touch(a)
        
        self.redirect()
        SubstCommand(v, a)
        actual = self.undirect()

        self.check_result(exp == actual, exp, actual)
        
    # -----------------------------------------------------------------------
    def test_SubstCommand_dryrun(self):
        """
        Test SubstCommand() with dryrun True and quiet False.
        """
        self.into_testdir()
        v = Values({'dryrun': True, 'quiet': False, 'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(["would do 'ls %s'\n" % x for x in a])
        self.unlink(a)

        self.redirect()
        SubstCommand(v, a)
        actual = self.undirect()

        self.check_result(exp == actual, exp, actual)
    
    # -----------------------------------------------------------------------
    def test_SubstCommand_quiet(self):
        """
        Test SubstCommand() with dryrun False and quiet True.
        """
        self.into_testdir()
        v = Values({'dryrun': False, 'quiet': True, 'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(['%s\n' % x for x in a])
        self.touch(a)
        
        self.redirect()
        SubstCommand(v, a)
        actual = self.undirect()

        self.check_result(exp == actual, exp, actual)
    
    # -----------------------------------------------------------------------
    def test_SubstCommand_both(self):
        """
        Test SubstCommand() with dryrun True and quiet True.
        """
        self.into_testdir()
        v = Values({'dryrun': True, 'quiet': True, 'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(["would do 'ls %s'\n" % x for x in a])
        self.unlink(a)
        
        self.redirect()
        SubstCommand(v, a)
        actual = self.undirect()

        self.check_result(exp == actual, exp, actual)
        
    # -----------------------------------------------------------------------
    def test_SubstRename_neither(self):
        """
        Test SubstRename() with dryrun False and quiet False.
        """
        self.into_testdir()
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            self.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = Values({'dryrun': False, 'quiet': False, 'edit': 's/.pl/.xyzzy'})

        self.redirect()
        SubstRename(v, arglist)
        actual = self.undirect()

        self.check_result(expected == actual, expected, actual)

        q = glob.glob('*.xyzzy')
        q.sort()
        self.check_result(q == exp, exp, q)
        
    # -----------------------------------------------------------------------
    def test_SubstRename_dryrun(self):
        """
        Test SubstRename() with dryrun True and quiet False.
        """
        self.into_testdir()
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            self.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = Values({'dryrun': True, 'quiet': False, 'edit': 's/.pl/.xyzzy'})

        self.redirect()
        SubstRename(v, arglist)
        actual = self.undirect()

        self.check_result(expected == actual, expected, actual)
            
        q = glob.glob('*.pl')
        q.sort()
        self.check_result(q == arglist, arglist, q)
        
    # -----------------------------------------------------------------------
    def test_SubstRename_quiet(self):
        """
        Test SubstRename() with dryrun False and quiet True.
        """
        self.into_testdir()
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            self.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = Values({'dryrun': False, 'quiet': True, 'edit': 's/.pl/.xyzzy'})

        self.redirect()
        SubstRename(v, arglist)
        actual = self.undirect()

        self.check_result(expected == actual, expected, actual)
        
        q = glob.glob('*.pl')
        q.sort()
        self.check_result(q == [], [], q)
        
        q = glob.glob('*.xyzzy')
        q.sort()
        self.check_result(q == exp, exp, q)
        
    # -----------------------------------------------------------------------
    def test_SubstRename_both(self):
        """
        Test SubstRename() with dryrun True and quiet True.
        """
        self.into_testdir()
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            self.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = Values({'dryrun': True, 'quiet': True, 'edit': 's/.pl/.xyzzy'})

        self.redirect()
        SubstRename(v, arglist)
        actual = self.undirect()

        self.check_result(expected == actual, expected, actual)
            
        q = glob.glob('*.pl')
        q.sort()
        self.check_result(q == arglist, arglist, q)
        
    # -----------------------------------------------------------------------
    def check_result(self, expr, expected, actual):
        """
        Calling this is similar to saying 'assert(expected == actual)'.

        If it fails, we report expected and actual. Otherwise, just return.
        """
        if not expr:
            raise AssertionError("'''\n%s\n''' != '''\n%s\n'''"
                                 % (expected, actual))

    # -----------------------------------------------------------------------
    def into_testdir(self):
        """
        Make sure we're in the test directory.

        Create it if necessary, then step down into it unless we're
        already there.
        """
        x = os.getcwd()
        if os.path.basename(x) != 'fx_test':
            if not os.path.exists('fx_test'):
                os.mkdir('fx_test')
            os.chdir('fx_test')
            
    # -----------------------------------------------------------------------
    def indirect(self, filename):
        """
        Arrange stdin to read from filename.
        """
        self.stdin = sys.stdin
        sys.stdin = open(filename, 'r')
        
    # -----------------------------------------------------------------------
    def redirect(self):
        """
        Aim stdout at a memory string so we can capture a function's output.
        """
        self.stdout = sys.stdout
        sys.stdout = StringIO.StringIO()

    # -----------------------------------------------------------------------
    def touch(self, touchables):
        """
        Touch the file or files named in touchables (string or list).
        """
        if type(touchables) == list:
            for f in touchables:
                open(f, 'a').close()
        elif type(touchables) == str:
            open(touchables, 'a').close()
        else:
            raise StandardError('argument must be list or string')
        
    # -----------------------------------------------------------------------
    def undirect(self):
        """
        Reset stdout (and stdin if needed) back to the terminal.
        """
        rval = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = self.stdout
        if not os.isatty(sys.stdin.fileno()) \
               and os.isatty(self.stdin.fileno()):
            sys.stdin = self.stdin
        return rval
    
    # -----------------------------------------------------------------------
    def unlink(self, args):
        """
        Unlink the file or files named in args (may be string or list).
        """
        if type(args) == list:
            for f in args:
                if os.path.exists(f):
                    os.unlink(f)
        elif type(args) == str:
            if os.path.exists(args):
                os.unlink(args)
        else:
            raise StandardError('argument must be list or string')
        
# ---------------------------------------------------------------------------
sname = sys.argv[0]
if sname.endswith('.py') and '-L' in sys.argv:
    pname = re.sub('.py$', '', sname)
    print("creating symlink: %s -> %s" % (pname, sname))
    os.symlink(sname, pname)
elif sname.endswith('.py') and __name__ == '__main__':
    unittest.main()
elif not sname.endswith('.py'):
    main(sys.argv)

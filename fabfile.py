"""
local fab control file

During dry runs, the functions list what they would do.

During actual execution, functions are quiet unless -v/--verbose is used.
"""
import difflib
import fnmatch
import glob
import os
import pdb

from optparse import OptionParser
from tpbtools import *

# ---------------------------------------------------------------------------
def fab_clean(args):
    """clean - remove generated files

    usage: fab clean [-e] [-v]

    Remove generated files from the current directory. Without
    -e/--exec on the command line, just do a dry run, reporting what
    would happen. During execution, function is silent unless
    -v/--verbose is specified.
    """
    p = OptionParser()
    p.add_option('-e', '--exec',
                 default=False, action='store_true', dest='xable',
                 help='without this option, just do a dryrun')
    p.add_option('-v', '--verbose',
                 default=False, action='store_true', dest='verbose',
                 help='more output')
    (o, a) = p.parse_args(args)

    cleanables = ["*~", "*.pyc", 'fl_tests']
    for c in cleanables:
        for f in glob.glob(c):
            if o.xable:
                if os.path.isdir(f):
                    if o.verbose:
                        print('rmrf(%s)' % f)
                    rmrf(f)
                else:
                    if o.verbose:
                        print('os.unlink(%s)' % f)
                    os.unlink(f)
            else:
                if os.path.isdir(f):
                    print('would rmrf %s' % f)
                else:
                    print('would unlink %s' % f)

# ---------------------------------------------------------------------------
def fab_dist(args):
    """dist - tar up this package for distribution

    usage: fab dist [-e] [=t filename]

    The files in the current package are packaged into a tar file. Without
    -e or --exec on the command line, does a dry run.
    """
    p = OptionParser()
    p.add_option('-e', '--exec',
                 default=False, action='store_true', dest='xable',
                 help='without this option, just do a dryrun')
    p.add_option('-t', '--tarball',
                 default='/tmp/backscratcher.tar.gz', action='store',
                 dest='tarball', help='path to output tarball')
    (o, a) = p.parse_args(args)

    fl = files()
    f = fl.keys()
    fstring = ' '.join(f)
    run('tar zcvf %s %s' % (o.tarball, fstring), o.xable)
        
# ---------------------------------------------------------------------------
def fab_install(args):
    """install - put stuff from this package where they belong

    usage: fab install [-e/--exec] [-v/--verbose]

    Copy files from the package to where they live. Without -e/--exec
    on the command line, does a dry run, reporting what it would do.
    During execution, the function is silent unless -v/--verbose is
    specified.

    During a dry run, 'D' will be appended to the copy command if the
    file exists in its installed location, but is different from the
    package version. If 'N' is appended to the copy command, the file
    does not exist in the installed location.
    """
    p = OptionParser()
    p.add_option('-e', '--exec',
                 default=False, action='store_true', dest='xable',
                 help='without this option, just do a dryrun')
    p.add_option('-v', '--verbose',
                 default=False, action='store_true', dest='verbose',
                 help='more output')
    (o, a) = p.parse_args(args)

    fl = files()
    fk = fl.keys()
    fk.sort()
    for f in fk:
        copy_it = ' '
        fpath = '%s/%s' % (os.path.expandvars(fl[f]), f)
        if not os.path.exists(f):
            raise Exception('File %s not found in the package' % f)

        if os.path.exists(fpath):
            diff = list(difflib.unified_diff(contents(fpath), contents(f)))
            if diff != []:
                copy_it = 'D'
            elif o.verbose:
                if o.xable:
                    print '%s already installed' % f
                else:
                    print "would report '%s already installed'" % f
        else:
            copy_it = 'N'

        if copy_it != ' ' and fl[f] != '/dev/null':
            cmd = 'cp %s %s # %s' % (f, fpath, copy_it)
            run(cmd, o.xable, o.verbose)
            
# ---------------------------------------------------------------------------
def fab_status(args):
    """status - report the status of the files in the current directory

    usage: fab status

    For each file in the current directory, report whether it is
      - not in the list of files defined herein (?),
      - installed (I),
      - installed but needs update (U),
      - not installed (F)
    """
    p = OptionParser()
    p.add_option('-a', '--attention',
                 default=False, action='store_true', dest='attention',
                 help='report only files needing attention (-f -u)')
    p.add_option('-d', '--debug',
                 default=False, action='store_true', dest='debug',
                 help='start the debugger')
    p.add_option('-i', '--installed',
                 default=False, action='store_true', dest='installed',
                 help='show installed files')
    p.add_option('-f', '--needed',
                 default=False, action='store_true', dest='needed',
                 help='show files not yet installed')
    p.add_option('-u', '--updates',
                 default=False, action='store_true', dest='updates',
                 help='show files needing update')
    p.add_option('-v', '--verbose',
                 default=False, action='store_true', dest='verbose',
                 help='more output')
    (o, a) = p.parse_args(args)

    if o.debug:   pdb.set_trace()
    
    fl = files()
    if len(a) <= 0:
        ll = glob.glob('*')
        ll.sort()
    else:
        ll = a

    if o.verbose:
        print('?: not in file list')
        print('F: in the file list, not installed')
        print('I: installed')
        print('U: installed, needs update')
    for filename in ll:
        if ignorable(filename):
            continue
        flag = '?'
        if filename in fl.keys():
            flag = 'F'
            ipath = '%s/%s' % (os.path.expandvars(fl[filename]), filename)
            if os.path.exists(ipath):
                flag = 'I'
                diff = list(difflib.unified_diff(contents(ipath),
                                                 contents(filename)))
                if diff != []:
                    flag += 'U'

        if (o.updates or o.attention) and 'U' in flag:
            print(" %s %s" % (flag, filename))
        elif o.installed and 'I' in flag:
            print(" %s %s" % (flag, filename))
        elif (o.needed or o.attention) and 'F' in flag:
            print(" %s %s" % (flag, filename))
        elif not o.updates and not o.needed \
                 and not o.installed and not o.attention:
            print(" %s %s" % (flag, filename))
        
# ---------------------------------------------------------------------------
def fab_uninstall(args):
    """uninstall - remove files installed from this package

    usage: fab uninstall [-e/--exec] [-v/--verbose]

    Remove files installed by this package. Function does a dry run
    and reports what it would do unless -e/--exec is specified. During
    execution, function is silent unless -v/--verbose is specified.
    """
    p = OptionParser()
    p.add_option('-e', '--exec',
                 default=False, action='store_true', dest='xable',
                 help='without this option, just do a dryrun')
    p.add_option('-v', '--verbose',
                 default=False, action='store_true', dest='verbose',
                 help='more output')
    (o, a) = p.parse_args(args)

    fl = files()
    fk = fl.keys()
    fk.sort()
    for f in fk:
        fpath = '%s/%s' % (os.path.expandvars(fl[f]), f)
        if os.path.exists(fpath):
            run('rm %s' % fpath, o.xable, o.verbose)

# ---------------------------------------------------------------------------
def files():
    """
    List of files to be maintained/distributed and where they should live.

    The entry for fabfile.py is needed so it will be distributed by the
    tarball routine, even though it should not be copied out during
    installation.
    """
    flist = {'align'         : '$HOME/bin',
             'align.py'      : '$HOME/bin',
             'ascii'         : '$HOME/bin',
             'ascii.py'      : '$HOME/bin',
             'calc'          : '$HOME/bin',
             'calc.py'       : '$HOME/bin',
             'chron'         : '$HOME/bin',
             'chron.py'      : '$HOME/bin',
             'dt'            : '$HOME/bin',
             'dt.py'         : '$HOME/bin',
             'errno'         : '$HOME/bin',
             'fab'           : '$HOME/bin',
             'fab.py'        : '$HOME/bin',
             'fabfile.py'    : '/dev/null',
             'filter.py'     : '$HOME/lib/python',
             'fl'            : '$HOME/bin',
             'fl.py'         : '$HOME/bin',
             'fx'            : '$HOME/bin',
             'fx.py'         : '$HOME/bin',
             'hd'            : '$HOME/bin',
             'hd.py'         : '$HOME/bin',
             'list.py'       : '$HOME/bin',
             'magnitude'     : '$HOME/bin',
             'mag.py'        : '$HOME/bin',
             'mag'           : '$HOME/bin',
             'odx'           : '$HOME/bin',
             'plwhich'       : '$HOME/bin',
             'ptidy'         : '$HOME/bin',
             'pytool'        : '$HOME/bin',
             'pytool.py'     : '$HOME/bin',
             'replay'        : '$HOME/bin',
             'rxlab'         : '$HOME/bin',
             'scanpath'      : '$HOME/bin',
             'summarize'     : '$HOME/bin',
             'testhelp.py'   : '$HOME/lib/python',
             'toolframe.py'  : '$HOME/lib/python',
             'tpbtools.py'   : '$HOME/bin',
             'tps'           : '$HOME/bin',
             'truth_table'   : '$HOME/bin',
             'vipath'        : '$HOME/bin',
             'wcal'          : '$HOME/bin',
             'workrpt'       : '$HOME/bin',
             'workrpt.py'    : '$HOME/bin',
             'wxfr'          : '$HOME/bin'}
    return flist

# ---------------------------------------------------------------------------
def ignorable(filename):
    """
    Return True or False indicating whether to ignore filename.
    """
    for pat in ignore():
        if fnmatch.fnmatchcase(filename, pat):
            return True
    return False

# ---------------------------------------------------------------------------
def ignore():
    """
    List of files to be ignored.
    """
    rval = ["DODO",
            "README",
            "*.pyc"]
    return rval

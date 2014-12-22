import glob
import optparse
import os
try:
    import pager
except ImportError:
    pass
import pdb
import pexpect
import re
from pkg_resources import resource_string
import shutil
import StringIO
import subprocess as subp
import sys
import util
from version import __version__


# -----------------------------------------------------------------------------
def main(args=None):
    """
    Command line entry point
    """
    if args is None:
        args = sys.argv
    util.dispatch('bscr.bscr', 'bscr', args)


# -----------------------------------------------------------------------------
def bscr_help_commands(args):
    """help_commands - list the commands that are part of backscratcher
    """

    cl = ["align       - use spaces to spread input lines so that " +
          "columns line up",
          "ascii       - display the ASCII collating sequence",
          "bscr        - help and management for the backscratcher suite",
          "calc        - simple python expression evaluator",
          "chron       - stopwatch and timer",
          "dt          - date and time manipulations",
          "fl          - retrieve and report information about files",
          "gtx         - git helper extensions",
          "fx          - command line special effects",
          "hd          - hexdump",
          "jcal        - generate various kinds of calendars",
          "list        - minus, union, or intersect two lists",
          "mag         - report the magnitude of a large number",
          "nvtool      - environment manipulation tool",
          "odx         - display value in octal, decimal, and hex format",
          "perrno      - report errno values",
          "plwhich     - report location of a perl module",
          "pstrack     - report whether current process stack contains root",
          "pytool      - start python scripts",
          "pywhich     - report location of python modules",
          "replay      - run a command repetitively",
          "rxlab       - play with regexps",
          "tps         - look up processes by fragments of ps line",
          "truth_table - generate a truth table",
          "wcal        - show a wide calendar of three months",
          "whych       - find python, perl, and bash modules",
          "workrpt     - time reports",
          "xclean      - remove files by pattern, optionally walking trees",
          ]

    ldir = os.path.dirname(sys.argv[0])
    for line in cl:
        cmd = line.split()[0]
        if os.path.exists("%s/%s" % (ldir, cmd)):
            print("   %s" % line)
        else:
            print(" * %s" % line)


# -----------------------------------------------------------------------------
def bscr_readme(args):
    """readme - display the package README file

    usage: bscr readme
    """
    try:
        readme = resource_string(__name__, "README")
    except:
        raise bscr.Error("Can't find the README file")

    try:
        pager.page(StringIO.StringIO(readme))
    except NameError:
        print(readme)
        print("(*** 'pip install pager' to get internal paging ***)")


# -----------------------------------------------------------------------------
def bscr_roots(args):
    """roots - display bscr root and git repo location

    usage: bscr roots
    """
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under the debugger')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    print("bscr root: %s" % util.bscr_root())
    print(" git root: %s" % util.git_root())
    print("in_bscr_repo: %s" % util.in_bscr_repo())


# -----------------------------------------------------------------------------
def bscr_test(args):
    """test - run tests

    usage: bscr test [-t py.test|green|nosetests|unittest] [-n] [-d]

    Without -t, we use the first available of py.test, green, nosetests, or
    unittest. With -t, we attempt to run the tests with the specified test
    runner.

    The tests are optimized for py.test. They may not work well under green
    or nose.
    """
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under the debugger')
    p.add_option('-n', '--dry-run',
                 action='store_true', default=False, dest='dryrun',
                 help='select a tester')
    p.add_option('-t', '--tester',
                 action='store', default='', dest='tester',
                 help='select a tester')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    with util.Chdir(util.dirname(__file__)):
        target = util.pj(os.path.dirname(__file__), 'test')
        print("Running tests in %s" % target)
        if o.tester == '':
            if which('py.test'):
                util.run('py.test %s' % target, not o.dryrun)
            elif which('green'):
                util.run('green -v %s' % target, not o.dryrun)
            elif which('nosetests') and importable('nose_ignoredoc'):
                tl = glob.glob(util.pj(target, 'test_*.py'))
                util.run('nosetests -v -c nose.cfg %s' % " ".join(tl),
                         not o.dryrun)
            else:
                tl = glob.glob(util.pj(target, 'test_*.py'))
                for t in tl:
                    util.run("%s -v" % t, not o.dryrun)
                    # p = subp.Popen([t, '-v'])
                    # p.wait()
        elif o.tester == 'py.test':
            util.run('py.test %s' % target, not o.dryrun)
        elif o.tester == 'green':
            util.run('green -v %s' % target, not o.dryrun)
        elif o.tester == 'nose':
            tl = glob.glob(util.pj(target, 'test_*.py'))
            util.run('nosetests -v -c nose.cfg %s' % " ".join(tl),
                     not o.dryrun)
        elif o.tester == 'unittest':
            tl = glob.glob(util.pj(target, 'test_*.py'))
            for t in tl:
                util.run("%s -v" % t, not o.dryrun)
        else:
            raise SystemExit("unrecognized tester: '%s'" % o.tester)


# -----------------------------------------------------------------------------
def bscr_uninstall(args):
    """uninstall - remove bscr from your system

    If you installed with pip, you can also uninstall with pip:

        pip uninstall bscr

    However, if you used easy_install, or if you just downloaded the tarball
    and ran 'python setup.py install', uninstalling can be a pain. bscr
    provides an easier way:

        bscr uninstall

    will remove bscr from your system.
    """
    bscrpkg = os.path.dirname(__file__)
    sitepkg = os.path.dirname(bscrpkg)
    if os.path.isdir(util.pj(sitepkg, '.git')):
        print("Cowardly refusing to uninstall from a .git repo")
    else:
        eggl = glob.glob(util.pj(sitepkg, 'backscratcher*egg*'))
        egg = eggl[0]
        iflist = util.contents(util.pj(egg, 'installed-files.txt'))
        print("Preparing to uninstall:")
        with util.Chdir(egg):
            afpl = [os.path.abspath(rfp.strip()) for rfp in iflist]
        for afp in afpl:
            print("   " + afp)
        print("   rmdir " + bscrpkg)
        answer = raw_input("Proceed? > ")
        if re.match("yes", answer):
            for afp in afpl:
                if os.path.isdir(afp):
                    shutil.rmtree(afp)
                elif os.path.exists(afp):
                    os.unlink(afp)
            shutil.rmtree(bscrpkg)

    return None


# -----------------------------------------------------------------------------
def bscr_version(args):
    """version - report the version of this backscratcher instance

    usage: bscr version
    """
    ap = util.cmdline([{'a': ['-v', '--verbose'],
                        'k': {'action': 'store_true',
                              'default': False,
                              'dest': 'verbose',
                              'help': 'show more info'
                              }}
                       ])
    (o, a) = ap.parse(args)

    print("Backscratcher version %s" % __version__)


# -----------------------------------------------------------------------------
def importable(module_name):
    """
    Module *module_name* is importable? True or False
    """
    try:
        m = __import__(module_name)
        if sys.getrefcount(module_name) <= 3:
            del sys.modules[module_name]
            del m
    except ImportError:
        return False
    return True


# -----------------------------------------------------------------------------
def which(program):
    """
    Figure out where program is. !@!DERPRECATED in favor of pexpect.which()
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

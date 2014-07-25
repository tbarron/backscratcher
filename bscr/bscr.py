import glob
import os
import pdb
import pexpect
import re
import shutil
import subprocess as subp
import sys
import util


# -----------------------------------------------------------------------------
def main(args=None):
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
    filename = "README"
    groot = util.git_root()
    broot = util.bscr_root()
    if groot:
        readme = util.pj(groot, filename)
    elif broot:
        readme = util.pj(broot, filename)
    else:
        raise StandardError("Can't find the README file")

    w, h = util.terminal_size()
    if sys.stdout.isatty():
        p = pexpect.spawn("less -z %d %s" % (h, readme))
        p.interact()
    else:
        shutil.copyfileobj(open(readme, 'r'), sys.stdout)


# -----------------------------------------------------------------------------
def bscr_test(args):
    """test - run tests

    If green is available, we use it. Otherwise, if nosetests is available, we
    use it. Otherwise, just call unittest.main for each test file.
    """
    with util.Chdir("/tmp"):
        target = util.pj(os.path.dirname(__file__), 'test')
        print("Running tests in %s" % target)
        if which('green'):
            p = subp.Popen(['green', '-v', target])
            p.wait()
        elif which('nosetests') and importable('nose_ignoredoc'):
            tl = glob.glob(util.pj(target, 'test_*.py'))
            p = subp.Popen(['nosetests', '-v', '-c', 'nose.cfg'] + tl)
            p.wait()
        else:
            tl = glob.glob(util.pj(target, 'test_*.py'))
            for t in tl:
                p = subp.Popen([t, '-v'])
                p.wait()


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
    filename = ".bscr_version"
    groot = util.git_root()
    broot = util.bscr_root()
    if groot:
        vpath = util.pj(groot, filename)
    elif broot:
        vpath = util.pj(broot, filename)
    else:
        raise StandardError("Can't find the version file")
    version = util.contents(vpath)
    print("Backscratcher version %s" % version[0])


# -----------------------------------------------------------------------------
def importable(module_name):
    pdb.set_trace()
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

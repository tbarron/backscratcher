"""
Backscratcher help and management

Usage:   bscr [-d] help [COMMAND]
         bscr [-d] help_commands
         bscr [-d] roots
         bscr [-d] uninstall
         bscr [-d] version
"""
from docopt_dispatch import dispatch
import os
import pdb
import sys

import util
from version import __version__


# -----------------------------------------------------------------------------
def main():
    """
    Command line entry point
    """
    dispatch(__doc__)


# -----------------------------------------------------------------------------
@dispatch.on('help_commands')
def bscr_help_commands(**kwa):
    """
    help_commands - list the commands that are part of backscratcher
    """
    cmdl = ["align       - use spaces to spread input lines so that " +
            "columns line up",
            "ascii       - display the ASCII collating sequence",
            "bscr        - help and management for the backscratcher suite",
            "calc        - simple python expression evaluator",
            "chron       - stopwatch and timer",
            "dt          - date and time manipulations",
            "filter      - report interesting items",
            "fl          - retrieve and report information about files",
            "fx          - command line special effects",
            "gtx         - git helper extensions",
            "hd          - hexdump",
            "jcal        - generate various kinds of calendars",
            "list        - minus, union, or intersect two lists",
            "mag         - report the magnitude of a large number",
            "mcal        - generate calendars with weeks starting Monday",
            "nvtool      - environment manipulation tool",
            "odx         - display value in octal, decimal, and hex format",
            "perrno      - report errno values",
            "pfind       - simple find(1) replacement",
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
            "xclean      - remove files by pattern, optionally walking trees"]

    ldir = os.path.dirname(sys.argv[0])
    for line in cmdl:
        cmd = line.split()[0]
        if os.path.exists("%s/%s" % (ldir, cmd)):
            print("   %s" % line)
        else:
            print(" * %s" % line)


# -----------------------------------------------------------------------------
@dispatch.on('help')
def bscr_help(**kwa):
    """
    Describe the functions provided by bscr

    'bscr help' provides a list of available functions

    'bscr help FUNCTION' provides a description of FUNCTION
    """
    if kwa['d']:
        pdb.set_trace()
    if kwa["COMMAND"]:
        fname = "bscr_" + kwa["COMMAND"]
        fobj = globals()[fname]
        print(fobj.__doc__)
    else:
        print(__doc__)


# -----------------------------------------------------------------------------
@dispatch.on('roots')
def bscr_roots(**kwa):
    """roots - display bscr root and git repo location

    usage: bscr roots
    """
    if kwa["d"]:
        pdb.set_trace()
    print("bscr root: %s" % util.bscr_root())
    print(" git root: %s" % util.git_root())
    print("in_bscr_repo: %s" % util.in_bscr_repo())


# -----------------------------------------------------------------------------
# needs test
# def bscr_uninstall(args):
#     """uninstall - remove bscr from your system
#
#     If you installed with pip, you can also uninstall with pip:
#
#         pip uninstall bscr
#
#     However, if you used easy_install, or if you just downloaded the tarball
#     and ran 'python setup.py install', uninstalling can be a pain. bscr
#     provides an easier way:
#
#         bscr uninstall
#
#     will remove bscr from your system.
#     """
#     bscrpkg = os.path.dirname(__file__)
#     sitepkg = os.path.dirname(bscrpkg)
#     if os.path.isdir(util.pj(sitepkg, '.git')):
#         print("Cowardly refusing to uninstall from a .git repo")
#     else:
#         eggl = glob.glob(util.pj(sitepkg, 'backscratcher*egg*'))
#         egg = eggl[0]
#         iflist = util.contents(util.pj(egg, 'installed-files.txt'))
#         print("Preparing to uninstall:")
#         with util.Chdir(egg):
#             afpl = [os.path.abspath(rfp.strip()) for rfp in iflist]
#         for afp in afpl:
#             print("   " + afp)
#         print("   rmdir " + bscrpkg)
#         answer = raw_input("Proceed? > ")
#         if re.match("yes", answer):
#             for afp in afpl:
#                 if os.path.isdir(afp):
#                     shutil.rmtree(afp)
#                 elif os.path.exists(afp):
#                     os.unlink(afp)
#             shutil.rmtree(bscrpkg)
#
#     return None


# -----------------------------------------------------------------------------
@dispatch.on('version')
def bscr_version(**kwa):
    """version - report the version of this backscratcher instance

    usage: bscr version
    """
    print("Backscratcher version %s" % __version__)


# -----------------------------------------------------------------------------
def importable(module_name):
    """
    Module *module_name* is importable? True or False
    """
    try:
        __import__(module_name)
        if sys.getrefcount(module_name) <= 3:
            del sys.modules[module_name]
            del mod
    except ImportError:
        return False
    return True


# -----------------------------------------------------------------------------
def which(program):
    """
    Figure out where program is. !@!DERPRECATED in favor of pexpect.which()
    """
    def is_exe(fpath):
        """
        True if *fpath* is executable, else False
        """
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
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

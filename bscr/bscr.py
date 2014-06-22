import glob
import os
import pdb
import re
import shutil
import subprocess as subp
import util

# -----------------------------------------------------------------------------
def dispatch(args):
    called_as = args.pop(0)
    try:
        func_name = args.pop(0)
    except IndexError:
        func_name = 'help'
    func = globals()['bscr_' + func_name]
    return func(args)

# -----------------------------------------------------------------------------
def bscr_help(args):
    """help - things bscr can do for you

    With no arguments, 'bscr help' provides a list of bscr subcommands.

    'bscr help <subcommand>' will provide a description of the indicated
    subcommand.
    """
    if 0 == len(args):
        for x in globals():
            if x.startswith('bscr_'):
                f = globals()[x]
                print f.__doc__.strip().split(os.linesep)[0]
    else:
        for fname in args:
            f = globals()['bscr_' + fname]
            print os.linesep + f.__doc__

# -----------------------------------------------------------------------------
def bscr_test(args):
    """test - run tests

    If green is available, we use it. Otherwise, if nosetests is available, we
    use it. Otherwise, just call unittest.main for each test file.
    """
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

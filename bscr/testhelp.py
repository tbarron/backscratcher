#!/usr/bin/python

import logging
import logging.handlers
import optparse
import os
import pdb
import pexpect
import pprint as pp
import re
import socket
import sys
import pytest
import unittest
import StringIO
import util as U
bscr = U.package_module(__name__)
tlogger = None


# -----------------------------------------------------------------------------
def main(args=None, filter=None, logfile=None):
    """
    This could be used as our own test runner, although I don't think it ever
    is. We could probably get rid of this routine.
    """
    if args is None:
        args = sys.argv
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='debug')
    p.add_option('-k', '--keep',
                 action='store_true', default=False, dest='keep',
                 help='keep test files')
    p.add_option('-l', '--list',
                 action='store_true', default=False, dest='list',
                 help='list tests')
    p.add_option('-q', '--quiet',
                 action='store_true', default=False, dest='quiet',
                 help='quieter')
    p.add_option('-t', '--to',
                 action='store', default='', dest='final',
                 help='run all tests up to this one')
    p.add_option('-v', '--verbose',
                 action='store_true', default=False, dest='verbose',
                 help='louder')
    (o, a) = p.parse_args(args)

    debug_flag(o.debug)

    if o.verbose:
        volume = 2
    elif o.quiet:
        volume = 0
    else:
        volume = 1

    # print sys.modules.keys()
    # print sys.modules['__main__']

    testlist = all_tests('__main__', filter)
    if o.list:
        list_tests(a, o.final, testlist)
        o.keep = True
    else:
        run_tests(a, o.final, testlist, volume, logfile)

    return o.keep


# ---------------------------------------------------------------------------
def all_tests(name, filter=None):
    '''
    Return a list of tests in the module <name>.
    Limit the list to those which contain the string <filter>.
    '''
    # print("all_tests(%s, %s)" % (name, filter))
    testclasses = []
    cases = []
    if filter is None:
        filter = 'Test'
    # print("all_tests(%s, %s)" % (name, filter))
    # print dir(sys.modules[name])
    for item in dir(sys.modules[name]):
        iobj = getattr(sys.modules[name], item)
        for iobjmember in dir(iobj):
            if iobjmember.startswith('test_') and filter in item:
                testclasses.append(item)
                break

    for c in testclasses:
        cobj = getattr(sys.modules[name], c)
        for case in unittest.TestLoader().getTestCaseNames(cobj):
            skip = case.replace('test_', 'skip_', 1)
            sfunc = getattr(sys.modules[name], skip, None)
            if sfunc is None:
                cases.append(['%s.%s' % (c, case), None])
            else:
                cases.append(['%s.%s' % (c, case), skip])

    return cases


# ---------------------------------------------------------------------------
def debug_flag(value=None):
    """
    Used in main() to decide whether --debug occurred on command line. This
    could go away with main().
    """
    global dval

    if value is not None:
        dval = value

    try:
        rval = dval
    except NameError:
        dval = False
        rval = dval

    return rval


# ---------------------------------------------------------------------------
def get_logger():
    """
    Get the singleton test logger
    """
    global tlogger
    return tlogger


# ---------------------------------------------------------------------------
def into_test_dir():
    """
    Create the test dir if needed, then cd into it. Deprecated in favor of
    setUp* plus 'with Chdir()'
    """
    tdname = '_test.%d' % os.getpid()
    bname = os.path.basename(os.getcwd())
    if bname != tdname:
        os.mkdir(tdname)
        os.chdir(tdname)
    return tdname


# ---------------------------------------------------------------------------
def keepfiles(value=None):
    """
    Return value of global value kf_flag. Optionally set it if value
    is specified. If it is not set, the default return value is False.
    """
    global kf_flag
    try:
        rval = kf_flag
    except:
        kf_flag = False
        rval = kf_flag

    if value is not None:
        kf_flag = value

    return rval


# ---------------------------------------------------------------------------
def list_tests(a, final, testlist):
    """
    This goes away with main(). If called through the main() test runner, this
    will list the tests available without running them.
    """
    # pdb.set_trace()
    if len(a) <= 1:
        for c in testlist:
            print c[0]
            if final != '' and final in c[0]:
                break
    else:
        for arg in a[1:]:
            for c in testlist:
                if arg in c[0]:
                    print c[0]
                if final != '' and final in c[0]:
                    break


# ---------------------------------------------------------------------------
def name_of(obj=None):
    """
    Return the caller's function name (with an optional class prefix).
    Is this used anywhere? Can we get rid of it?
    """
    return str(obj).split()[0]


# ---------------------------------------------------------------------------
def rm_cov_warn(string):
    """
    Return the input string with the coverage warning removed if it was
    present.
    """
    rval = string
    covwarn = "Coverage.py.warning:.No.data.was collected.\r?\n?"
    if re.findall(covwarn, string):
        rval = re.sub(covwarn, "", string)
    return rval


# ---------------------------------------------------------------------------
def run_tests(a, final, testlist, volume, logfile=None):
    """
    This goes with the main() test runner. Probably not needed.
    """
    mainmod = sys.modules['__main__']
    if len(a) <= 1:
        suite = LoggingTestSuite(logfile=logfile)
        for (case, skip) in testlist:
            if skip_check(skip):
                continue
            s = unittest.TestLoader().loadTestsFromName(case, mainmod)
            suite.addTests(s)
            if final != '' and final in case:
                break
    else:
        suite = LoggingTestSuite(logfile=logfile)
        for arg in a[1:]:
            for (case, skip) in testlist:
                if skip_check(skip):
                    continue
                if arg in case:
                    s = unittest.TestLoader().loadTestsFromName(case, mainmod)
                    suite.addTests(s)
                if final != '' and final in case:
                    break

    result = unittest.TextTestRunner(verbosity=volume).run(suite)


# -----------------------------------------------------------------------------
class HelpedTestCase(unittest.TestCase):
    # -------------------------------------------------------------------------
    def expgot(self, exp, actual):
        """
        *exp* and *actual* should be equal. If they are not, report an
         assertion failure.
        """
        self.assertEqual(exp, actual,
                         "Expected '%s', got '%s'" % (exp, actual))

    # -------------------------------------------------------------------------
    def expected(self, exp, actual):
        """
        *exp* and *actual* should be equal. If they are not, report an
         assertion failure.
        """
        self.assertEqual(exp, actual,
                         "Expected '%s', got '%s'" % (exp, actual))

    # -------------------------------------------------------------------------
    def exp_in_got(self, exp, actual):
        """
        *exp* is expected to be in *actual*. If it is not, report an assertion
         failure.
        """
        self.assertIn(exp, actual,
                      "Expected '%s' in '%s'" % (exp, actual))

    # -----------------------------------------------------------------------
    def assertEq(self, expected, actual):
        """
        Calling this is similar to saying 'assert(expected == actual)'.

        If it fails, we report expected and actual. Otherwise, just return.
        """
        self.assertEqual(expected, actual,
                         self._generate_msg(expected, actual))

    # -------------------------------------------------------------------------
    def _generate_msg(self, exp, act):
        """
        Generate a message to report how *exp* and *act* differ
        """
        rval = "\n"
        if type(exp) == list:
            if 5 < len(exp):
                for i in range(0, len(exp)):
                    try:
                        if exp[i] != act[i]:
                            rval += "EXPECTED: '%s'\n" % exp[i]
                            rval += "     GOT: '%s'\n" % act[i]
                    except IndexError:
                        rval += "EXPECTED: '%s'\n" % exp[i]
                        rval += "     GOT: None\n"
            else:
                rval += "EXPECTED '%s'\n" % exp
                rval += "     GOT '%s'\n" % act
        elif type(exp) == str:
            rval += "EXPECTED: '%s'\n" % exp
            rval += "     GOT: '%s'\n" % act
        else:
            rval += "EXPECTED: %s\n" % repr(exp)
            rval += "     GOT: %s\n" % repr(act)

        return rval

    # -------------------------------------------------------------------------
    def assertIn(self, member, container, msg=None):
        """
        Report an assertion failure if *member* is not in *container*.
        """
        if member not in container:
            fmsg = "%s not found in %s" % (pp.saferepr(member),
                                           pp.saferepr(container))
            self.fail(msg or fmsg)

    # -------------------------------------------------------------------------
    def assertModule(self, module_name, filename):
        """
        The root directory for the module and the associated test file should
        be the same. If not, report an assertion failure.
        """
        mroot = U.bscr_root(sys.modules[module_name].__file__)
        troot = U.bscr_root()
        self.assertEqual(troot, mroot,
                         "Expected '%s', got '%s'" % (troot, mroot))

    # -------------------------------------------------------------------------
    def assertNotIn(self, member, container, msg=None):
        """
        Report an assertion failure if *member* IS in *container*.
        """
        if member in container:
            fmsg = "%s unexpectedly found in %s" % (pp.saferepr(member),
                                                    pp.saferepr(container))
            self.fail(msg or fmsg)

    # -------------------------------------------------------------------------
    def assertOptionHelp(self, script, explist):
        """
        Test '*script* --help', comparing the result against *explist*.
        """
        cmd = U.script_location(script)
        result = pexpect.run("%s --help" % cmd)
        if type(explist) == str:
            self.assertTrue(explist in result,
                            "Expected '%s' in %s" %
                            (explist, U.lquote(result)))
        elif type(explist) == list:
            for exp in explist:
                self.assertTrue(exp in result,
                                "Expected '%s' in %s" %
                                (exp, U.lquote(result)))
        else:
            self.fail("Expected string or list, got %s" % type(explist))

    # -------------------------------------------------------------------------
    def assertRaisesMsg(self, exctype, excstr, func, *args, **kwargs):
        """
        The call *func*(* *args*, ** *kwargs*) should raise an exception of
        *exctype* containing the message *excstr*. If not, we report the
        assertion failure.
        """
        try:
            func(*args, **kwargs)
        except exctype, e:
            if excstr not in str(e):
                fmsg = ("Expected '%s' in the exception, got '%s'"
                        % (excstr, str(e)))
                self.fail(fmsg)
        except Exception, e:
            self.fail("Expected an exception of type %s, got %s" %
                      (exctype, type(e)))

    # -------------------------------------------------------------------------
    def setUp(self):
        """
        """
        dbgopt = pytest.config.getoption("dbg")
        if any(["all" in x.lower() for x in dbgopt] +
               [self._testMethodName in dbgopt]):
            self.dbgfunc = pdb.set_trace
        else:
            self.dbgfunc = lambda: None


# -----------------------------------------------------------------------------
class LoggingTestSuite(unittest.TestSuite):
    def __init__(self, tests=(), logfile=None):
        """
        This initializes my version of the TestSuite class that does test
        logging. I think this can be deprecated in favor of a scheme where we
        override unittest.TestResult.stopTest() and do the logging there.
        """
        super(LoggingTestSuite, self).__init__(tests)
        self._logger = None
        if None != logfile:
            self.setup_logging(logfile)

    def setup_logging(self, logfile):
        """
        Initialize test logging.
        """
        self._logger = logging.getLogger('TestSuite')
        self._logger.setLevel(logging.INFO)
        host = socket.gethostname().split('.')[0]
        fh = logging.handlers.RotatingFileHandler(logfile,
                                                  maxBytes=10*1024*1024,
                                                  backupCount=5)
        strfmt = "%" + "(asctime)s [%s] " % host + "%" + "(message)s"
        fmt = logging.Formatter(strfmt, datefmt="%Y.%m%d %H:%M:%S")
        fh.setFormatter(fmt)

        self._logger.addHandler(fh)
        self._logger.info('-' * (55 - len(host)))

    def run(self, result):
        """
        Run the tests in the suite.
        """
        errs = 0
        fails = 0
        for test in self._tests:
            if result.shouldStop:
                break
            if None != self._logger:
                test(result)
                if fails < len(result.failures):
                    self._logger.info('%-30s >>> FAILED' % name_of(test))
                    fails = len(result.failures)
                elif errs < len(result.errors):
                    self._logger.info('%-30s >>> ERROR' % name_of(test))
                    errs = len(result.errors)
                else:
                    self._logger.info('%-25s PASSED' % name_of(test))
            else:
                test(result)
        return result


# -----------------------------------------------------------------------------
class StdoutExcursion(object):
    """
    This class allows us to run something that writes to stdout and capture the
    output in a StringIO.

        with StdoutExcursion() as sio:
            do something that writes to stdout
            result = sio()
        self.assertEqual(result, ...)

    This is useful in a different way than
        result = pexpect.run(something that writes stdout)
    since pexpect.run() expects a command line but in a StdoutExcursion, we can
    call a python function.
    """
    def __init__(self):
        self.stdout = sys.stdout

    def __enter__(self):
        sys.stdout = StringIO.StringIO()
        return sys.stdout.getvalue

    def __exit__(self, type, value, traceback):
        sys.stdout.close()
        sys.stdout = self.stdout


# ---------------------------------------------------------------------------
def show_stdout(value=None):
    """
    Return value of global value show_stdout. Optionally set it if
    value is specified. If it is not set, the default return value is False.
    """
    global show_output
    try:
        rval = show_output
    except:
        show_output = False
        rval = show_output

    if value is not None:
        show_output = value

    return rval


# ---------------------------------------------------------------------------
def skip_check(skipfunc):
    """
    My attempt at implementing skipping. Superceded by the options offered in
    py.test, nosetests, etc.
    """
    if skipfunc is None:
        return False
    func = getattr(sys.modules['__main__'], skipfunc)
    rval = func()
    if rval:
        print "skipping %s" % skipfunc.replace('skip_', 'test_')
    return rval


# ---------------------------------------------------------------------------
def testlog(mname):
    """
    Get a test log file name.
    """
    return "%s/test.log" % os.path.dirname(sys.modules[mname].__file__)


# ---------------------------------------------------------------------------
def touch(pathname):
    """
    Do the same sort of thing as touch(1), except that this does not actually
    update the file time if it already exists. It just creates *pathname* if it
    does not exist.
    """
    open(pathname, 'a').close()


# ---------------------------------------------------------------------------
def write_file(filename, mode=0644, content=None):
    """
    Write *content* to *filename* and set the file's mode to *mode*. This looks
    to be the same as util.writefile().
    """
    f = open(filename, 'w')
    if type(content) == str:
        f.write(content)
    elif type(content) == list:
        f.writelines([x.rstrip() + '\n' for x in content])
    else:
        raise bscr.Error("content is not of a suitable type (%s)"
                         % type(content))
    f.close()
    os.chmod(filename, mode)


# -----------------------------------------------------------------------------
class UnderConstructionError(Exception):
    # -------------------------------------------------------------------------
    def __init__(self, value=""):
        """
        Deprecated in favor of 'self.fail('construction')'
        """
        if value == '':
            self.value = 'under construction'
        else:
            self.value = value

    # -------------------------------------------------------------------------
    def __str__(self):
        """
        Deprecated in favor of 'self.fail('construction')'
        """
        return repr(self.value)

# -----------------------------------------------------------------------------
global d
d = dir()
if __name__ == '__main__':
    main(sys.argv)

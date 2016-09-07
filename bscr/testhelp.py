#!/usr/bin/python
"""
Stuff to help with testing
"""
import logging
import logging.handlers
import os
import pdb
import pprint as pp
import re
import socket
import sys
import unittest
import StringIO

import pytest

import pexpect
import util as U

BSCR = U.package_module(__name__)


# ---------------------------------------------------------------------------
def all_tests(name, fltr=None):
    """
    Return a list of tests in the module *name*.
    Limit the list to those which contain the string *fltr*.
    """
    testclasses = []
    cases = []
    if fltr is None:
        fltr = 'Test'
    for item in dir(sys.modules[name]):
        iobj = getattr(sys.modules[name], item)
        for iobjmember in dir(iobj):
            if iobjmember.startswith('test_') and fltr in item:
                testclasses.append(item)
                break

    for cls in testclasses:
        cobj = getattr(sys.modules[name], cls)
        for case in unittest.TestLoader().getTestCaseNames(cobj):
            skip = case.replace('test_', 'skip_', 1)
            sfunc = getattr(sys.modules[name], skip, None)
            if sfunc is None:
                cases.append(['%s.%s' % (cls, case), None])
            else:
                cases.append(['%s.%s' % (cls, case), skip])

    return cases


# ---------------------------------------------------------------------------
def debug_flag(value=None):
    """
    Used in main() to decide whether --debug occurred on command line. This
    could go away with main().
    """
    try:
        rval = debug_flag.dval
    except AttributeError:
        rval = debug_flag.dval = False

    if value is not None:
        rval = debug_flag.dval = value

    return rval


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
    try:
        rval = keepfiles.kf_flag
    except AttributeError:
        keepfiles.kf_flag = False
        rval = keepfiles.kf_flag

    if value is not None:
        keepfiles.kf_flag = value

    return rval


# ---------------------------------------------------------------------------
def list_tests(argl, final, testlist):
    """
    This goes away with main(). If called through the main() test runner, this
    will list the tests available without running them.
    """
    # pdb.set_trace()
    if len(argl) <= 1:
        for candy in testlist:
            print candy[0]
            if final != '' and final in candy[0]:
                break
    else:
        for arg in argl[1:]:
            for candy in testlist:
                if arg in candy[0]:
                    print candy[0]
                if final != '' and final in candy[0]:
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
def run_tests(argl, final, testlist, volume, logfile=None):
    """
    This goes with the main() test runner. Probably not needed.
    """
    mainmod = sys.modules['__main__']
    if len(argl) <= 1:
        suite = LoggingTestSuite(logfile=logfile)
        for (case, skip) in testlist:
            if skip_check(skip):
                continue
            slst = unittest.TestLoader().loadTestsFromName(case, mainmod)
            suite.addTests(slst)
            if final != '' and final in case:
                break
    else:
        suite = LoggingTestSuite(logfile=logfile)
        for arg in argl[1:]:
            for (case, skip) in testlist:
                if skip_check(skip):
                    continue
                if arg in case:
                    slst = unittest.TestLoader().loadTestsFromName(case,
                                                                   mainmod)
                    suite.addTests(slst)
                if final != '' and final in case:
                    break

    unittest.TextTestRunner(verbosity=volume).run(suite)


# -----------------------------------------------------------------------------
class HelpedTestCase(unittest.TestCase):
    """
    This class inherits from unittest.TestCase so we can hang extra attributes
    on it
    """
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
        if isinstance(actual, str):
            covmsg = "Coverage.py.warning:.No.data.was collected.\r?\n?"
            if re.findall(covmsg, actual):
                actual = re.sub(covmsg, "", actual)
        self.assertEqual(expected, actual,
                         self._generate_msg(expected, actual))

    # -------------------------------------------------------------------------
    def _generate_msg(self, exp, act):
        """
        Generate a message to report how *exp* and *act* differ
        """
        rval = "\n"
        if isinstance(exp, list):
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
        elif isinstance(exp, str):
            rval += "EXPECTED: '%s'\n" % exp.replace(' ', '.')
            rval += "     GOT: '%s'\n" % act.replace(' ', '.')
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
    def assertModule(self, module_name, filename=None):
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
        if isinstance(explist, str):
            self.assertTrue(explist in result,
                            "Expected '%s' in %s" %
                            (explist, U.lquote(result)))
        elif isinstance(explist, list):
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
        What it sounds like -- prepare for a test
        """
        dbgopt = pytest.config.getoption("dbg")
        if any(["all" in x.lower() for x in dbgopt] +
               [self._testMethodName in dbgopt]):
            self.dbgfunc = pdb.set_trace
        else:
            self.dbgfunc = lambda: None


# -----------------------------------------------------------------------------
class LoggingTestSuite(unittest.TestSuite):
    """
    Inherit from unittest.TestSuite so we can add attributes useful for logging
    """
    def __init__(self, tests=(), logfile=None):
        """
        This initializes my version of the TestSuite class that does test
        logging. I think this can be deprecated in favor of a scheme where we
        override unittest.TestResult.stopTest() and do the logging there.
        """
        super(LoggingTestSuite, self).__init__(tests)
        self._logger = None
        if logfile is not None:
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
            if self._logger is not None:
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

    DEPRECATED in favor of py.test's capsys facility
    """
    def __init__(self):
        self.stdout = sys.stdout

    def __enter__(self):
        sys.stdout = StringIO.StringIO()
        return sys.stdout.getvalue

    def __exit__(self, tb_type, value, traceback):
        sys.stdout.close()
        sys.stdout = self.stdout


# ---------------------------------------------------------------------------
def show_stdout(value=None):
    """
    Return value of global value show_stdout. Optionally set it if
    value is specified. If it is not set, the default return value is False.
    """
    try:
        rval = show_stdout.flag
    except AttributeError:
        show_stdout.flag = False
        rval = show_stdout.flag

    if value is not None:
        show_stdout.flag = value

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
    if isinstance(content, str):
        f.write(content)
    elif isinstance(content, list):
        f.writelines([x.rstrip() + '\n' for x in content])
    else:
        raise BSCR.Error("content is not of a suitable type (%s)"
                         % type(content))
    f.close()
    os.chmod(filename, mode)


# -----------------------------------------------------------------------------
class UnderConstructionError(Exception):
    """
    Deprecated in favor of 'pytest.fail('construction')'
    """
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

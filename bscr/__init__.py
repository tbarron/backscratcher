import glob
import pdb
import pexpect
import sys
import testhelp as th
import util as U


# -----------------------------------------------------------------------------
class Error(Exception):
    def __init__(self, value):
        """
        input
        """
        self.value = value

    def __str__(self):
        """
        output
        """
        return repr(self.value)


# -----------------------------------------------------------------------------
def whych():
    """
    Find stuff
    """
    c = U.cmdline([{'name': 'namespace',
                    'default': '',
                    'help': 'python (default), perl, or bash'}])
    (o, a) = c.parse(sys.argv)

    if o.namespace in ['', 'python']:
        for item in a[1:]:
            print(python_which(item))
    elif o.namespace == 'perl':
        for item in a[1:]:
            print(perl_which(item))
    elif o.namespace == 'bash':
        for item in a[1:]:
            print(bash_which(item))
    else:
        raise SystemExit("--namespace argument must be 'python', " +
                         "'perl', or 'bash'")


# -----------------------------------------------------------------------------
def python_which(module_name):
    """
    Look up *module_name* in sys.path and return it if found
    """
    rval = ''
    mname = module_name.replace('.', '/')
    for path in sys.path:
        dname = U.pj(path, mname)
        pname = dname + ".py"
        cname = dname + ".pyc"
        if U.exists(dname):
            rval = dname
            break
        elif U.exists(cname):
            rval = cname
            break
        elif U.exists(pname):
            rval = pname
            break
    return rval


# -----------------------------------------------------------------------------
def perl_which(module_name):
    """
    Look for and return the path of the perl module
    """
    # pdb.set_trace()
    rval = ""
    result = th.rm_cov_warn(pexpect.run("perl -E \"say for @INC\""))
    z = result.strip().split("\r\n")
    m = module_name.replace("::", "/") + ".pm"
    # print("-----")
    for x in z:
        cpath = U.pj(x, m)
        # print cpath
        if U.exists("%s" % cpath):
            rval += cpath + "\n"
    return rval.strip()


# -----------------------------------------------------------------------------
def bash_which(xname):
    """
    Return the location of xname based on $PATH
    """
    return pexpect.which(xname)

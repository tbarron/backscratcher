from bscr import list
# from bscr import testhelp as th
from bscr import util as U
import pexpect
# import pprint
import pytest


# -----------------------------------------------------------------------------
def test_generate_list(tmpdir):
    """
    Generate a list from the output of a command
    """
    pytest.debug_func()
    flist = ["abc", "def", "ghi"]
    for fname in flist:
        tmpdir.join(fname).ensure()
    with U.Chdir(tmpdir.strpath):
        a = list.generate_list("ls")
        for fname in flist:
            assert fname in a
    assert sorted(flist) == sorted(a)


# -------------------------------------------------------------------------
def test_list_help():
    """
    Verify that 'list --help' does the right thing
    """
    result = pexpect.run("list --help")
    exp = "usage: list {minus|union|intersect} <list-1> <list-2>"
    assert exp in result


# -----------------------------------------------------------------------
def test_list_intersect():
    """
    Test the intersect operation
    """
    a_list = ['one', 'two', 'three', 'four', 'five']
    b_list = ['two', 'four', 'six', 'eight', 'ten']
    isect = list.list_intersect(a_list, b_list)
    assert sorted(isect) == ['four', 'two']


# -----------------------------------------------------------------------
def test_list_minus():
    """
    Test the minus operation
    """
    a = list.list_minus(['one', 'two', 'three', 'four', 'five'],
                        ['two', 'four', 'six', 'eight'])
    assert a == ['one', 'three', 'five']


# -----------------------------------------------------------------------
def test_list_union():
    """
    Test the union operation
    """
    a_list = ['one', 'three', 'five']
    b_list = ['two', 'four', 'five', 'six', 'two']
    union = list.list_union(a_list, b_list)
    union.sort()
    assert(union == ['five', 'four', 'one', 'six', 'three', 'two'])

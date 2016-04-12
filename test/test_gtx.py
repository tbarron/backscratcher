import os
import pdb
import pexpect
import pytest
import py
from bscr import testhelp
from bscr import util as U


# -----------------------------------------------------------------------------
def assertLink(hook, link):
    """
    Assert that 1) *hook* exists, 2) *link* exists, 3) *link* is a symlink
    pointing at *hook*
    """
    assert(os.path.exists(hook))
    assert(os.path.exists(link))
    nhook = U.normalize_path(hook)
    nlink = U.normalize_path(os.readlink(link))
    assert(nlink == nhook)


# -----------------------------------------------------------------------------
def assertNoLink(hook, link):
    """
    Assert that *hook* exists but that *link* does not
    """
    assert(os.path.exists(hook))
    assert(not os.path.exists(link))


# -----------------------------------------------------------------------------
def gtxtest_setup_hldirs(tmpdir, hooks=[], mklinks=[]):
    """
    Create the hook and link directories and maybe set up some links
    """
    if isinstance(tmpdir, py._path.local.LocalPath):
        tdname = tmpdir.strpath
    else:
        tdname = tmpdir
    bn_d = {}
    bn_d['hookdir'] = os.path.join(tdname, "hookdir")
    os.mkdir(bn_d['hookdir'])
    bn_d['linkdir'] = os.path.join(tdname, "linkdir")
    os.mkdir(bn_d['linkdir'])
    for hook in hooks:
        bn_d[hook] = {}
        bn_d[hook]['hook'] = os.path.join(bn_d['hookdir'], hook)
        bn_d[hook]['link'] = os.path.join(bn_d['linkdir'], hook)
        U.touch(bn_d[hook]['hook'])
        if hook in mklinks:
            os.symlink(bn_d[hook]['hook'], bn_d[hook]['link'])
    return bn_d


# -----------------------------------------------------------------------------
def test_gtx_hooks_create_all_already(tmpdir):
    """
    Ask to create all links, some already exist
    """
    pytest.debug_func()
    hooklist = ['first', 'second', 'third']
    bn_d = gtxtest_setup_hldirs(tmpdir.strpath,
                                hooks=hooklist,
                                mklinks=['second'])

    assertLink(bn_d['second']['hook'], bn_d['second']['link'])

    hookdir = bn_d['hookdir']
    linkdir = bn_d['linkdir']
    S = pexpect.spawn("gtx hooks -C -H %s -l %s" % (hookdir, linkdir))

    while True:
        which = S.expect(["does not appear to have a link",
                          "already has link",
                          pexpect.EOF,
                          pexpect.TIMEOUT])
        if 0 == which:
            S.expect(r"Shall I add one\? >")
            S.sendline("y")
        elif 1 == which:
            pass
        else:
            break

    assert(" <-- " in S.before)

    for hook in hooklist:
        assertLink(bn_d[hook]['hook'], bn_d[hook]['link'])


# -------------------------------------------------------------------------
def test_gtx_hooks_create_all_nothing(tmpdir):
    """
    Create all links, nothing in place
    """
    pytest.debug_func()
    hooklist = ['one', 'two', 'three']
    hl_d = gtxtest_setup_hldirs(tmpdir.strpath, hooks=hooklist)

    hookdir = hl_d['hookdir']
    linkdir = hl_d['linkdir']
    S = pexpect.spawn("gtx hooks -C -H %s -l %s" % (hookdir, linkdir))
    while True:
        which = S.expect(["does not appear to have a link",
                          "already has link",
                          pexpect.EOF,
                          pexpect.TIMEOUT])
        if 0 == which:
            S.expect(r"Shall I add one\? >")
            S.sendline("y")
        elif 1 == which:
            self.unexpected_in("already has link", S.before)
        else:
            break

    S.expect(pexpect.EOF)

    for hook in hooklist:
        hpath = os.path.join(hl_d['hookdir'], hook)
        lpath = os.path.join(hl_d['linkdir'], hook)
        assert(os.path.exists(hpath))
        assert(os.path.exists(lpath))


# -------------------------------------------------------------------------
def test_gtx_hooks_create_name_already(tmpdir):
    """
    Create by name, some already there
    """
    pytest.debug_func()
    hooklist = ['one', 'two', 'three']
    hl_d = gtxtest_setup_hldirs(tmpdir.strpath,
                                hooks=hooklist,
                                mklinks=['two'])

    hookdir = hl_d['hookdir']
    linkdir = hl_d['linkdir']

    assertLink(hl_d['two']['hook'], hl_d['two']['link'])

    S = pexpect.spawn("gtx hooks -C -H %s -l %s three" % (hookdir, linkdir))
    while True:
        which = S.expect(["does not appear to have a link",
                          "already has link",
                          pexpect.EOF,
                          pexpect.TIMEOUT])
        if 0 == which:
            S.expect(r"Shall I add one\? >")
            S.sendline("y")
        elif 1 == which:
            pass
        else:
            break

    S.expect(pexpect.EOF)

    assertNoLink(hl_d['one']['hook'], hl_d['one']['link'])
    assertLink(hl_d['two']['hook'], hl_d['two']['link'])
    assertLink(hl_d['three']['hook'], hl_d['three']['link'])


# -----------------------------------------------------------------------------
def test_gtx_hooks_create_name_nomatch(tmpdir):
    """
    Create by name no match, some already there
    """
    pytest.debug_func()
    hooklist = ['one', 'two', 'three']
    hl_d = gtxtest_setup_hldirs(tmpdir.strpath,
                                hooks=hooklist,
                                mklinks=['two'])

    hookdir = hl_d['hookdir']
    linkdir = hl_d['linkdir']

    assertLink(hl_d['two']['hook'], hl_d['two']['link'])

    S = pexpect.spawn("gtx hooks -C -H %s -l %s seven" % (hookdir, linkdir))
    S.expect(pexpect.EOF)

    assertNoLink(hl_d['one']['hook'], hl_d['one']['link'])
    assertLink(hl_d['two']['hook'], hl_d['two']['link'])
    assertNoLink(hl_d['three']['hook'], hl_d['three']['link'])


# -------------------------------------------------------------------------
def test_gtx_hooks_create_name_nothing(tmpdir):
    """
    Create by name, nothing in place
    """
    pytest.debug_func()
    hooklist = ['one', 'two', 'three']
    hl_d = gtxtest_setup_hldirs(tmpdir.strpath,
                                hooks=hooklist,
                                mklinks=[])

    hookdir = hl_d['hookdir']
    linkdir = hl_d['linkdir']

    S = pexpect.spawn("gtx hooks -C -H %s -l %s one" % (hookdir, linkdir))
    S.expect(pexpect.EOF)

    assertLink(hl_d['one']['hook'], hl_d['one']['link'])
    assertNoLink(hl_d['two']['hook'], hl_d['two']['link'])
    assertNoLink(hl_d['three']['hook'], hl_d['three']['link'])


# -----------------------------------------------------------------------------
def test_gtx_hooks_delall_ntd(tmpdir):
    """
    Delete all links, but there aren't any there to delete
    """
    pytest.debug_func()
    hooklist = ['one', 'two', 'three']
    hl_d = gtxtest_setup_hldirs(tmpdir.strpath, hooks=hooklist)

    hookdir = hl_d['hookdir']
    linkdir = hl_d['linkdir']
    S = pexpect.spawn("gtx hooks -D -H %s -l %s" % (hookdir, linkdir))
    S.expect(pexpect.EOF)

    assert("There are no links to delete" in S.before)
    for hook in hooklist:
        assertNoLink(hl_d[hook]['hook'], hl_d[hook]['link'])


# -------------------------------------------------------------------------
def test_gtx_hooks_delall_std(tmpdir):
    """
    Delete all links, something is there to delete
    """
    pytest.debug_func()
    hooklist = ['one', 'two', 'three']
    hl_d = gtxtest_setup_hldirs(tmpdir.strpath, hooks=hooklist,
                                mklinks=['two', 'three'])

    hookdir = hl_d['hookdir']
    linkdir = hl_d['linkdir']
    S = pexpect.spawn("gtx hooks -D -H %s -l %s" % (hookdir, linkdir))
    S.expect(pexpect.EOF)

    assert("There are no links to delete" not in S.before)
    for hook in hooklist:
        assertNoLink(hl_d[hook]['hook'], hl_d[hook]['link'])


# -------------------------------------------------------------------------
def test_gtx_hooks_delname_nomatch(tmpdir):
    """
    Delete by non-matching name, nothing is there to delete
    """
    pytest.debug_func()
    hooklist = ['one', 'two', 'three']
    hl_d = gtxtest_setup_hldirs(tmpdir.strpath, hooks=hooklist,
                                mklinks=[])

    hookdir = hl_d['hookdir']
    linkdir = hl_d['linkdir']
    S = pexpect.spawn("gtx hooks -D -H %s -l %s seven" % (hookdir, linkdir))
    S.expect(pexpect.EOF)

    assert("There is no link to seven to delete" in S.before)
    for hook in hooklist:
        assertNoLink(hl_d[hook]['hook'], hl_d[hook]['link'])


# -------------------------------------------------------------------------
def test_gtx_hooks_delname_ntd(tmpdir):
    """
    Delete by matching name, nothing is there to delete
    """
    pytest.debug_func()
    hooklist = ['one', 'two', 'three']
    hl_d = gtxtest_setup_hldirs(tmpdir.strpath, hooks=hooklist,
                                mklinks=[])

    hookdir = hl_d['hookdir']
    linkdir = hl_d['linkdir']
    S = pexpect.spawn("gtx hooks -D -H %s -l %s two" % (hookdir, linkdir))
    S.expect(pexpect.EOF)

    assert("There is no link to two to delete" in S.before)
    for hook in hooklist:
        assertNoLink(hl_d[hook]['hook'], hl_d[hook]['link'])


# -------------------------------------------------------------------------
def test_gtx_hooks_delname_std(tmpdir):
    """
    Delete by name, something is there to delete
    """
    pytest.debug_func()
    hooklist = ['one', 'two', 'three']
    hl_d = gtxtest_setup_hldirs(tmpdir.strpath, hooks=hooklist,
                                mklinks=['two'])

    hookdir = hl_d['hookdir']
    linkdir = hl_d['linkdir']
    S = pexpect.spawn("gtx hooks -D -H %s -l %s two" % (hookdir, linkdir))
    S.expect(pexpect.EOF)

    assert("There is no link to two to delete" not in S.before)
    for hook in hooklist:
        assertNoLink(hl_d[hook]['hook'], hl_d[hook]['link'])

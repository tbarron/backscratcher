#!/bin/env python

import fnmatch
import glob
import sys
sys.path.append("/ccs/home/tpb/lib/python")
import optparse
import os
import pdb
import pexpect
import re
import shlex
import subprocess
import time
# import xtoolframe
import traceback
import unittest
import util


# ---------------------------------------------------------------------------
def main(args=None):
    """
    Command line entry point
    """
    if args is None:
        args = sys.argv
    util.dispatch("bscr.gtx", "gtx", args)


# -----------------------------------------------------------------------------
def gtx_addem(args):
    """addem - add pending files to git index for commit
    """
    p = optparse.OptionParser()
    p.add_option('-a',  '--add',
                 action='append', default=[], dest='add',
                 help='which statuses to add')
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    p.add_option('-f',  '--force',
                 action='store_true', default=False, dest='force',
                 help='add -f to the git add command')
    p.add_option('-i',  '--ignore',
                 action='append', default=[], dest='ignore',
                 help='which statuses to ignore')
    p.add_option('-n',  '--dryrun',
                 action='store_true', default=False, dest='dryrun',
                 help='show what would happen')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    fl = []
    r = pexpect.run("git status --porcelain")
    ignlist = ["??", "R"]
    addlist = ["UU", "AA", "AU", "UA", "M"]

    for st in o.add:
        if st in ignlist:
            ignlist.remove(st)
        if st not in addlist:
            addlist.append(st)
    for st in o.ignore:
        if st in addlist:
            addlist.remove(st)
        if st not in ignlist:
            ignlist.append(st)

    for line in r.strip().split("\r\n"):
        if line.strip() == '':
            continue
        (status, filename) = line.strip().split(None, 1)
        if status in ignlist:
            continue
        if status in addlist:
            fl.append(filename)

    if fl == []:
        msg = ["Nothing to add. 'git status --porcelain' to see status flags.",
               "Use 'gtx addem -a/--add ST -i/--ignore ST' to select statuses",
               "to add or ignore.",
               "Defaults:"
               "   ignore '??', 'M', 'R'",
               "   add    'UU', 'AA', 'AU', 'UA'",
               ]
        for line in msg:
            print line
        raise SystemExit
    cmd = "git add "
    if o.force:
        cmd += "-f "
    cmd += " ".join(fl)
    if o.dryrun:
        print("would do: '%s'" % cmd)
    else:
        print cmd
        r = pexpect.run(cmd)
        print r


# -----------------------------------------------------------------------------
def gtx_cleanup(args):
    """cleanup - remove .orig files
    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    p.add_option('-n',  '--dryrun',
                 action='store_true', default=False, dest='dryrun',
                 help='show what would happen')
    p.add_option('-s',  '--suffix',
                 action='store', default='', dest='suffix',
                 help='suffix to remove')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    if o.suffix == '':
        suffix = '.orig'
    else:
        suffix = o.suffix

    for r, d, f in os.walk("."):
        for filename in f:
            if filename.endswith(suffix):
                print("os.unlink(%s)" % os.path.join(r, filename))
                os.unlink(os.path.join(r, filename))


# -----------------------------------------------------------------------------
def gtx_gerrit_issues(args):
    """gerrit_issues - report commits that we expect gerrit to complain about
    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    p.add_option('-n',  '--dryrun',
                 action='store_true', default=False, dest='dryrun',
                 help='show what would happen')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    depth = 0
    r = pexpect.run("git --no-pager log")
    for c in r.split("\r\n\x1b[33mcommit"):
        issue = []
        if "Change-Id:" not in c:
            issue.append("Change-Id: not present")
        z = c.split("\r\n")
        if 65 < len(z[4].strip()):
            issue.append("Summary line too long")
        if 0 < len(z[5].strip()):
            issue.append("First paragraph too long")
        if issue != []:
            # d = c.replace("\x1b[m", "")
            d = re.sub("\x1b\[\d*m", "", c)
            if not d.startswith("commit"):
                d = "commit" + d
            print "===> Depth: %d" % depth
            for i in issue:
                print "===> %s" % i
            print d
            print("")
        depth += 1


# -----------------------------------------------------------------------------
def gtx_hooks(args):
    """hooks - check hooks and offer to add any missing links
    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    p.add_option('-C',  '--create',
                 action='store_true', default=False, dest='create',
                 help='create hooks')
    p.add_option('-D',  '--delete',
                 action='store_true', default=False, dest='delete',
                 help='delete hooks')
    p.add_option('-H',  '--hookdir',
                 action='store', default='', dest='hookdir',
                 help='hook scripts under git control')
    p.add_option('-n',  '--dryrun',
                 action='store_true', default=False, dest='dryrun',
                 help='show what would happen')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    srcdir = o.hookdir
    if srcdir == '':
        srcdir = 'githooks'

    lnkdir = ".git/hooks"

    if o.delete:
        hooks_delete(a, lnkdir)

    if o.create:
        hooks_create(srcdir, lnkdir, a)

    hooks_list(srcdir, lnkdir)


# -----------------------------------------------------------------------------
def hooks_list(srcdir, lnkdir):
    D = {}
    scr_l = [x for x in glob.glob("%s/*" % srcdir)]
    for scr in scr_l:
        key = os.path.abspath(scr)
        D[key] = {}
        D[key]['abs'] = os.path.abspath(scr)
        D[key]['short'] = scr

    lnk_l = [x for x in glob.glob("%s/*" % lnkdir) if os.path.islink(x)]
    for link in lnk_l:
        target = os.readlink(link)
        if target in D:
            D[target]['link'] = link
        else:
            D[target] = {}
            D[target]['link'] = link

    for key in D:
        if 'short' in D[key] and 'link' in D[key]:
            print("   %-25s  <-- %s" % (D[key]['short'], D[key]['link']))
        elif 'short' in D[key] and 'link' not in D[key]:
            print("   %-25s      NO LINK" % (D[key]['short']))
        elif 'short' not in D[key] and 'link' in D[key]:
            print("   %-25s <-- %s" % ('-' * 10, D[key]['link']))


# -----------------------------------------------------------------------------
def hooks_delete(names, lnkdir):
    """
    Delete links from .git/hooks by name or all of them
    """
    links = [x for x in glob.glob("%s/*" % lnkdir) if os.path.islink(x)]
    if names == []:
        if links:
            for path in links:
                os.unlink(path)
        else:
            print("There are no links to delete")
    else:
        for name in names:
            tmp = [x for x in links if name in x]
            if tmp:
                os.unlink(tmp[0])
            else:
                print("There is no link to %s to delete" % name)


# -----------------------------------------------------------------------------
def hooks_create(srcdir, lnkdir, names):
    """
    Offer to create hook links if they are missing
    """
    script_l = [os.path.abspath(x) for x in glob.glob("%s/*" % srcdir)]
    link_l = [x for x in glob.glob("%s/*" % lnkdir) if os.path.islink(x)]
    linked = {}
    for l in link_l:
        target = os.path.abspath(os.readlink(l))
        if target in script_l:
            linked[target] = l

    if names == []:
        for h in script_l:
            if h not in linked:
                print("%s does not appear to have a link in .git/hooks" %
                      os.path.basename(h))
                answer = raw_input("Shall I add one? > ")
                if answer.strip().lower().startswith('y'):
                    os.symlink(h, "%s/%s" % (lnkdir, os.path.basename(h)))
            else:
                print("%s already has link %s" % (os.path.basename(h),
                                                  linked[h]))
    else:
        for name in names:
            tmp = [x for x in script_l if x.endswith(name)]
            if tmp == []:
                print("I don't see a hook script named %s to link" % name)
                continue

            for spath in tmp:
                if spath in linked:
                    print("It looks like link %s already points at %s" %
                          (linked[spath], os.path.basename(spath)))
                else:
                    os.symlink(spath,
                               "%s/%s" % (lnkdir, os.path.basename(spath)))


# -----------------------------------------------------------------------------
def gtx_depth(args):
    """depth - report depth and age of a commit
    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    p.add_option('-n',  '--dryrun',
                 action='store_true', default=False, dest='dryrun',
                 help='show what would happen')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    depth = 0
    found = False
    r = pexpect.run("git --no-pager log")
    for c in r.split("\r\n\x1b[33mcommit"):
        chash_l = re.findall("(commit)?\s+([0-9a-f]+)", c)
        chash = chash_l[0][1]
        date_l = re.findall("Date:\s+([^\r\n]+)", c)
        date = date_l[0]

        for needle in a:
            if needle in c:
                found = True
                print("commit %s" % c.replace("\x1b[m", ""))
                print("===> Depth: %d" % depth)
                break

        depth += 1

    if not found:
        print("No commit found matching '%s'" % a)


# -----------------------------------------------------------------------------
def gtx_flix(args):
    """flix - show '<<<<< HEAD' lines from current conflicts

    With the -e option, you can make flix throw you into an editor on each file
    that contains a conflict.

    any() is True if any of the listed conditions are True. Basically, it ORs
    all the conditions in the list passed to it.
    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    p.add_option('-e',  '--edit',
                 action='store_true', default=False, dest='edit',
                 help='run an editor on each file with conflicts')
    p.add_option('-g', '--glob',
                 action='store', default='*', dest='globstr',
                 help='only report on files matching the glob string')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    fl = []
    r = pexpect.run("git status --porcelain")
    for line in r.split("\n"):
        if any([line.startswith("?? "),
                line.startswith("D  "),
                line.startswith("R  "),
                line.strip() == '',
                ]):
            continue
        fl.append(line.strip()[3:])
    for fn in [x for x in fl if fnmatch.fnmatch(x, o.globstr)]:
        edit_this_one = False
        lnum = 0
        z = open(fn, 'r')
        for line in z:
            if '<<<<<<<' in line:
                print("%s[%d]: %s" % (fn, lnum, line.strip()))
                edit_this_one = True
            lnum += 1
        if edit_this_one and o.edit:
            call_editor(fn)


# -----------------------------------------------------------------------------
def gtx_fl(args):
    """fl - list files needing attention (eg, during a rebase)
    """
    r = pexpect.run("git status --porcelain")
    for line in r.split("\n"):
        if "??" in line or line.strip() == '':
            continue
        print line.split()[1]
        # print line.strip()[3:]


# -----------------------------------------------------------------------------
def gtx_progress(args):
    """progress - show rebase progress 

    usage: gtx progress refdir rebasedir


    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    ref = a[0]
    rebase = a[1]

    os.chdir(rebase)
    r = pexpect.run("git --no-pager log --no-color -1")
    commit = re.findall("commit\s+(\w+)", r)
    x = r.split("\r\n")
    needle = x[4].strip()
    pass

    os.chdir(os.path.join("..", ref))
    r = pexpect.run("gtx depth %s" % commit[0])
    if "No commit found" in r:
        r = pexpect.run("gtx depth -- \"%s\"" % needle)
    print r
    pass

# -----------------------------------------------------------------------------
def gtx_recover(args):
    """recover - recover file content from HEAD into a missing 'added by them'

    This is for when we're rebasing and files git says are in conflict and need
    to be added to the index don't exist in the tree. This will recover such
    files from the previous commit and copy the content into the right place
    where git expects them.
    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    agenda = {}
    status = pexpect.run("git status --porc").strip().split("\r\n")

    # For each file to be handled, we expect a "D" record from where the file
    # was deleted and a "UA" record for where the file should be.
    for substr in a:
        z = [x for x in status if substr in x]
        agenda[substr] = {}
        for entry in z:
            (stat, path) = entry.split(None, 1)
            if stat == "D":
                agenda[substr]["src"] = path
            elif stat == "UA":
                agenda[substr]["dst"] = path
            else:
                print("Ignoring '%s'" % entry)

    for substr in agenda:
        if "src" not in agenda[substr]:
            print("No source for %s" % substr)
        elif "dst" not in agenda[substr]:
            print("No destination for %s" % substr)
        elif os.path.exists(agenda[substr]["dst"]):
            print("%s already exists, not rewriting" % agenda[substr]["dst"])
        else:
            cmd = "git --no-pager show HEAD:%s" % (agenda[substr]["src"])
            print cmd + " > " + agenda[substr]["dst"]
            result = pexpect.run(cmd)
            with open(agenda[substr]["dst"], 'w') as out:
                out.write(result)


# -----------------------------------------------------------------------------
def gtx_resolve(args):
    """resolve - resolve conflicts either for or against HEAD
    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    p.add_option('-H', '--head',
                 action='store_true', default=False, dest='head',
                 help='resolve in favor of HEAD')
    p.add_option('-c', '--commit',
                 action='store_true', default=False, dest='commit',
                 help='resolve in favor of commit')
    p.add_option('-s', '--suffix',
                 action='store', default='.orig', dest='suffix',
                 help='suffix to append to original file(s)')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    if o.head and o.commit:
        raise SystemExit("-H and -c are mutually exclusive")
    elif o.head:
        resolve = 'head'
    elif o.commit:
        resolve = 'commit'
    else:
        raise SystemExit("One of -H or -c are required")

    r = pexpect.run("git status --porcelain")
    for line in r.rstrip().split("\r\n"):
        (status, filename) = line.split(None, 1)
        if status in ["AA", "UU"]:
            resolve_file(resolve, filename, o.suffix)


# -----------------------------------------------------------------------------
def resolve_file(which, filename, suffix):
    """
    Resolve one file
    """
    nname = filename + ".new"
    o = open(nname, 'w')
    write = True
    with open(filename, 'r') as i:
        for line in i.readlines():
            if line.startswith("<<<<<<< HEAD") :
                write = (which == 'head')
                continue
            elif line.startswith("======="):
                write = (which == 'commit')
                continue
            elif line.startswith(">>>>>>>"):
                write = True
                continue
            elif write:
                o.write(line)
    o.close()

    if suffix != '':
        os.rename(filename, filename + suffix)
    os.rename(nname, filename)


# -----------------------------------------------------------------------------
def gtx_nochid(args):
    """nochid - report log entries that don't have a Change-Id
    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    try:
        result = pexpect.run("git --no-pager log")
        current = ''
        for line in result.split("\n"):
            if line.startswith("\x1b[33mcommit "):
                line = re.sub("\x1b\[3*m", "", line)
                if current and "Change-Id:" not in current:
                    print("-----")
                    print current
                    print("===> subsequent %s" % line)
                current = line
            else:
                current += "\n" + line
        if "Change-Id:" not in current:
            print current
    except IOError,e:
        if "Broken pipe" not in str(e):
            raise


# -----------------------------------------------------------------------------
def gtx_nodoc(args):
    """nodoc - report functions in the current tree with no doc string
    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    for r, d, f in os.walk("."):
        for path in [os.path.join(r, fname) for fname in f
                     if fname.endswith(".py")]:
            s = contents(path)
            for idx in range(len(s)):
                if re.findall("^\s*def\s+", s[idx]):
                    if all([x not in s[idx+1] for x in ['"""', "'''"]]):
                        print("%s: %s" % (path, s[idx].rstrip()))


# -----------------------------------------------------------------------------
def gtx_rm_untrack(args):
    """rm_untrack - remove untracked files
    """
    p = optparse.OptionParser()
    p.add_option('-d',  '--debug',
                 action='store_true', default=False, dest='debug',
                 help='start the debugger')
    p.add_option('-n',  '--dry-run',
                 action='store_true', default=False, dest='dryrun',
                 help='show what would happen')
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    r = [z.split()
         for z in pexpect.run("git status --porcelain").strip().split("\r\n")]
    for x in r:
        if x[0] == '??':
            print("os.unlink(%s)" % x[1])
            if not o.dryrun:
                os.unlink(x[1])


# -----------------------------------------------------------------------------
def contents(path):
    with open(path, 'r') as f:
        rval = f.readlines()
    return rval


# -----------------------------------------------------------------------------
def call_editor(filename):
    editor = os.getenv("EDITOR")
    if editor is None:
        editor = pexpect.which("vim")
    if editor is None:
        editor = pexpect.which("vi")
    if editor is None:
        raise StandardError("Can't find an editor")
    os.system("%s %s" % (editor, filename))


# -----------------------------------------------------------------------------
# def exc_handler(t, v, tb):
#     pdb.set_trace()
#     with open("/tmp/traceback.log", 'a') as f:
#         f.write(">>> %s <<<\n" % (time.strftime("%Y.%m%d %H:%M:%S")))
#         f.write("".join(traceback.format_tb(tb)))
#         f.write("%s: %s\n" % (t.__name__, str(v)))
# 
#     print(str(v))
# sys.excepthook = exc_handler

# -----------------------------------------------------------------------------
class GtxTest(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_gtx_hooks_delall_ntd(self):
        """
        Delete all links, but there aren't any there to delete
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_gtx_hooks_delall_std(self):
        """
        Delete all links, something is there to delete
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_gtx_hooks_delname_std(self):
        """
        Delete by name, something is there to delete
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_gtx_hooks_delname_ntd(self):
        """
        Delete by matching name, nothing is there to delete
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_gtx_hooks_delname_nomatch(self):
        """
        Delete by non-matching name, nothing is there to delete
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_gtx_hooks_create_all_nothing(self):
        """
        Create all links, nothing in place
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_gtx_hooks_create_all_already(self):
        """
        Create all links, some already there
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_gtx_hooks_create_name_nothing(self):
        """
        Create by name, nothing in place
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_gtx_hooks_create_name_already(self):
        """
        Create all links, some already there
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_gtx_hooks_create_name_nomatch(self):
        """
        Create all links, some already there
        """
        self.fail('construction')

# -----------------------------------------------------------------------------
# xtoolframe.tf_launch('gtx')

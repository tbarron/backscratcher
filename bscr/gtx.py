#!/bin/env python
"""
Git extensions
"""
import fnmatch
import glob
import sys
import optparse
import os
import pdb
import re

import pexpect
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
    prs = optparse.OptionParser()
    prs.add_option('-a', '--add',
                   action='append', default=[], dest='add',
                   help='which statuses to add')
    prs.add_option('-d', '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    prs.add_option('-f', '--force',
                   action='store_true', default=False, dest='force',
                   help='add -f to the git add command')
    prs.add_option('-i', '--ignore',
                   action='append', default=[], dest='ignore',
                   help='which statuses to ignore')
    prs.add_option('-n', '--dryrun',
                   action='store_true', default=False, dest='dryrun',
                   help='show what would happen')
    (opts, _) = prs.parse_args(args)

    if opts.debug:
        pdb.set_trace()

    flist = []
    result = pexpect.run("git status --porcelain")
    ignlist = ["??", "R"]
    addlist = ["UU", "AA", "AU", "UA", "M"]

    # remove from ignlist anything in opts.add
    ignlist = [_ for _ in ignlist if _ not in opts.add]  # noqa: ignore=F812
    # add to addlist anything in opts.add
    addlist.extend([_ for _ in opts.add if _ not in addlist])

    # remove from addlist anything in opts.ignore
    addlist = [_ for _ in addlist if _ not in opts.ignore]
    # add to ignlist anything in opts.ignore
    ignlist.extend([_ for _ in opts.ignore if _ not in ignlist])

    for line in result.strip().split("\r\n"):
        if line.strip() == '':
            continue
        (status, filename) = line.strip().split(None, 1)
        if status in ignlist:
            continue
        if status in addlist:
            flist.append(filename)

    if flist == []:
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
    if opts.force:
        cmd += "-f "
    cmd += " ".join(flist)
    if opts.dryrun:
        print("would do: '%s'" % cmd)
    else:
        print cmd
        result = pexpect.run(cmd)
        print result


# -----------------------------------------------------------------------------
def gtx_cleanup(args):
    """cleanup - remove .orig files
    """
    prs = optparse.OptionParser()
    prs.add_option('-d',  '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    prs.add_option('-n',  '--dryrun',
                   action='store_true', default=False, dest='dryrun',
                   help='show what would happen')
    prs.add_option('-s',  '--suffix',
                   action='store', default='', dest='suffix',
                   help='suffix to remove')
    (opts, _) = prs.parse_args(args)

    if opts.debug:
        pdb.set_trace()

    suffix = opts.suffix or '.orig'

    for root, _, files in os.walk("."):
        for filename in files:
            if filename.endswith(suffix):
                print("os.unlink(%s)" % os.path.join(root, filename))
                os.unlink(os.path.join(root, filename))


# -----------------------------------------------------------------------------
def gtx_gerrit_issues(args):
    """gerrit_issues - report commits that we expect gerrit to complain about

    TODO: gtx_gerrit_issues() needs test? No, not using gerrit anymore
    """
    prs = optparse.OptionParser()
    prs.add_option('-d',  '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    prs.add_option('-n',  '--dryrun',
                   action='store_true', default=False, dest='dryrun',
                   help='show what would happen')
    (opts, _) = prs.parse_args(args)

    if opts.debug:
        pdb.set_trace()

    depth = 0
    result = pexpect.run("git --no-pager log")
    for commit in result.split("\r\n\x1b[33mcommit"):
        issue = []
        if "Change-Id:" not in commit:
            issue.append("Change-Id: not present")
        lines = commit.split("\r\n")
        if 65 < len(lines[4].strip()):
            issue.append("Summary line too long")
        if 0 < len(lines[5].strip()):
            issue.append("First paragraph too long")
        if issue != []:
            # d = c.replace("\x1b[m", "")
            clean = re.sub(r"\x1b\[\d*m", "", commit)
            if not clean.startswith("commit"):
                clean = "commit" + clean
            print "===> Depth: %d" % depth
            for i in issue:
                print "===> %s" % i
            print clean
            print("")
        depth += 1


# -----------------------------------------------------------------------------
def gtx_hooks(args):
    """hooks - check hooks and offer to add any missing links

    usage: gtx hooks [-d] [-n] [-C|-D] [-H dir]

    """
    prs = optparse.OptionParser()
    prs.add_option('-d',  '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    prs.add_option('-C',  '--create',
                   action='store_true', default=False, dest='create',
                   help='create hooks')
    prs.add_option('-D',  '--delete',
                   action='store_true', default=False, dest='delete',
                   help='delete hooks')
    prs.add_option('-H',  '--hookdir',
                   action='store', default='', dest='hookdir',
                   help='where to look for hook scripts')
    prs.add_option('-l',  '--linkdir',
                   action='store', default='', dest='linkdir',
                   help='link dir for testing')
    prs.add_option('-n',  '--dryrun',
                   action='store_true', default=False, dest='dryrun',
                   help='show what would happen')
    (opts, args) = prs.parse_args(args)

    if opts.debug:
        pdb.set_trace()

    srcdir = opts.hookdir
    if srcdir == '':
        srcdir = 'githooks'

    lnkdir = opts.linkdir
    if lnkdir == '':
        lnkdir = ".git/hooks"

    if opts.delete:
        hooks_delete(args, lnkdir)

    if opts.create:
        hooks_create(srcdir, lnkdir, args)

    hooks_list(srcdir, lnkdir)


# -----------------------------------------------------------------------------
def hooks_list(srcdir, lnkdir):
    """
    Report the hooks set up in a git repository
    """
    dat = {}
    scr_l = [x for x in glob.glob("%s/*" % srcdir)]
    for scr in scr_l:
        key = os.path.abspath(scr)
        dat[key] = {}
        dat[key]['abs'] = os.path.abspath(scr)
        dat[key]['short'] = scr

    lnk_l = [x for x in glob.glob("%s/*" % lnkdir) if os.path.islink(x)]
    for link in lnk_l:
        target = os.readlink(link)
        if target in dat:
            dat[target]['link'] = link
        else:
            dat[target] = {}
            dat[target]['link'] = link

    for key in dat:
        if 'short' in dat[key] and 'link' in dat[key]:
            print("   %-25s  <-- %s" % (dat[key]['short'], dat[key]['link']))
        elif 'short' in dat[key] and 'link' not in dat[key]:
            print("   %-25s      NO LINK" % (dat[key]['short']))
        elif 'short' not in dat[key] and 'link' in dat[key]:
            print("   %-25s <-- %s" % ('-' * 10, dat[key]['link']))


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
def hook_exists(path, linkdir):
    """
    Return True if a link in linkdir points at path, else False.

    We assume linkdir is already normalized.
    """
    rval = ''
    for link in [_ for _ in glob.glob(os.path.join(linkdir, "*"))
                 if os.path.islink(_)]:
        targ = util.normalize_path(os.readlink(link))
        if targ == path:
            rval = link
            break
    return rval


# -----------------------------------------------------------------------------
def hooks_create(srcdir, lnkdir, names):
    """
    Offer to create hook links if they are missing
    """
    srcndir = util.normalize_path(srcdir)
    lnkndir = util.normalize_path(lnkdir)

    src_l = [_ for _ in glob.glob(os.path.join(srcndir, "*"))
             if os.path.isfile(_)]

    if names == []:
        for hook in src_l:
            link = hook_exists(hook, lnkndir)
            if link:
                print("{0} already has link {1}"
                      ''.format(os.path.basename(hook),
                                link))
            else:
                print("{0} does not appear to have a link "
                      "in the link directory"
                      "".format(os.path.basename(hook)))
                answer = raw_input("Shall I add one? > ")
                if answer.strip().lower().startswith('y'):
                    os.symlink(hook,
                               os.path.join(lnkndir, os.path.basename(hook)))
    else:
        for name in names:
            path = os.path.join(srcndir, name)
            if path not in src_l:
                print("I don't see a hook script named {0} to link"
                      ''.format(name))
                continue

            link = hook_exists(path, lnkndir)
            if link:
                print("{0} already has link {1}"
                      ''.format(os.path.basename(path), link))
            else:
                os.symlink(path, os.path.join(lnkndir, os.path.basename(path)))


# -----------------------------------------------------------------------------
def gtx_depth(argl):
    """depth - report depth and age of a commit
    """
    prs = optparse.OptionParser()
    prs.add_option('-d',  '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    prs.add_option('-n',  '--dryrun',
                   action='store_true', default=False, dest='dryrun',
                   help='show what would happen')
    (opts, args) = prs.parse_args(argl)

    if opts.debug:
        pdb.set_trace()

    depth = 0
    found = False
    result = pexpect.run("git --no-pager log")
    for commit in result.split("\r\n\x1b[33mcommit"):
        # chash_l = re.findall(r"(commit)?\s+([0-9a-f]+)", commit)
        # chash = chash_l[0][1]
        # date_l = re.findall(r"Date:\s+([^\r\n]+)", commit)
        # date = date_l[0]

        for needle in args:
            if needle in commit:
                found = True
                print("commit %s" % commit.replace("\x1b[m", ""))
                print("===> Depth: %d" % depth)
                break

        depth += 1

    if not found:
        print("No commit found matching '%s'" % args)


# -----------------------------------------------------------------------------
def gtx_flix(argl):
    """flix - show '<<<<< HEAD' lines from current conflicts

    With the -e option, you can make flix throw you into an editor on each file
    that contains a conflict.

    any() is True if any of the listed conditions are True. Basically, it ORs
    all the conditions in the list passed to it.
    """
    prs = optparse.OptionParser()
    prs.add_option('-d',  '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    prs.add_option('-e',  '--edit',
                   action='store_true', default=False, dest='edit',
                   help='run an editor on each file with conflicts')
    prs.add_option('-g', '--glob',
                   action='store', default='*', dest='globstr',
                   help='only report on files matching the glob string')
    (opts, _) = prs.parse_args(argl)

    if opts.debug:
        pdb.set_trace()

    flist = []
    result = pexpect.run("git status --porcelain")
    for line in result.split("\n"):
        if any([line.startswith("?? "),
                line.startswith("D  "),
                line.startswith("R  "),
                line.strip() == '',
                ]):
            continue
        flist.append(line.strip()[3:])
    for fname in [_ for _ in flist               # noqa: ignore=F812
                  if fnmatch.fnmatch(_, opts.globstr)]:

        edit_this_one = False
        lnum = 0
        rble = open(fname, 'r')
        for line in rble:
            if '<<<<<<<' in line:
                print("%s[%d]: %s" % (fname, lnum, line.strip()))
                edit_this_one = True
            lnum += 1
        if edit_this_one and opts.edit:
            call_editor(fname)


# -----------------------------------------------------------------------------
def gtx_fl(argl=None):
    """fl - list files needing attention (eg, during a rebase)
    """
    result = pexpect.run("git status --porcelain")
    for line in result.split("\n"):
        if "??" in line or line.strip() == '':
            continue
        print line.split()[1]
        # print line.strip()[3:]


# -----------------------------------------------------------------------------
def gtx_progress(argl):
    """progress - show rebase progress

    usage: gtx progress refdir rebasedir


    """
    prs = optparse.OptionParser()
    prs.add_option('-d',  '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    (opts, args) = prs.parse_args(argl)

    if opts.debug:
        pdb.set_trace()

    ref = args[0]
    rebase = args[1]

    os.chdir(rebase)
    result = pexpect.run("git --no-pager log --no-color -1")
    commit = re.findall(r"commit\s+(\w+)", result)
    line = result.split("\r\n")
    needle = line[4].strip()

    os.chdir(os.path.join("..", ref))
    result = pexpect.run("gtx depth %s" % commit[0])
    if "No commit found" in result:
        result = pexpect.run("gtx depth -- \"%s\"" % needle)
    print result


# -----------------------------------------------------------------------------
def gtx_recover(argl):
    """recover - recover file content from HEAD into a missing 'added by them'

    This is for when we're rebasing and files git says are in conflict and need
    to be added to the index don't exist in the tree. This will recover such
    files from the previous commit and copy the content into the right place
    where git expects them.
    """
    prs = optparse.OptionParser()
    prs.add_option('-d',  '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    (opts, args) = prs.parse_args(argl)

    if opts.debug:
        pdb.set_trace()

    agenda = {}
    status = pexpect.run("git status --porc").strip().split("\r\n")

    # For each file to be handled, we expect a "D" record from where the file
    # was deleted and a "UA" record for where the file should be.
    for substr in args:
        hits = [_ for _ in status if substr in _]
        agenda[substr] = {}
        for entry in hits:
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
    prs = optparse.OptionParser()
    prs.add_option('-d',  '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    prs.add_option('-H', '--head',
                   action='store_true', default=False, dest='head',
                   help='resolve in favor of HEAD')
    prs.add_option('-c', '--commit',
                   action='store_true', default=False, dest='commit',
                   help='resolve in favor of commit')
    prs.add_option('-s', '--suffix',
                   action='store', default='.orig', dest='suffix',
                   help='suffix to append to original file(s)')
    (opts, _) = prs.parse_args(args)

    if opts.debug:
        pdb.set_trace()

    if opts.head and opts.commit:
        raise SystemExit("-H and -c are mutually exclusive")
    elif opts.head:
        resolve = 'head'
    elif opts.commit:
        resolve = 'commit'
    else:
        raise SystemExit("One of -H or -c are required")

    result = pexpect.run("git status --porcelain")
    for line in result.rstrip().split("\r\n"):
        (status, filename) = line.split(None, 1)
        if status in ["AA", "UU"]:
            resolve_file(resolve, filename, opts.suffix)


# -----------------------------------------------------------------------------
def resolve_file(which, filename, suffix):
    """
    Resolve one file
    @TEST
    """
    nname = filename + ".new"
    wble = open(nname, 'w')
    write = True
    with open(filename, 'r') as rble:
        for line in rble.readlines():
            if line.startswith("<<<<<<< HEAD"):
                write = (which == 'head')
                continue
            elif line.startswith("======="):
                write = (which == 'commit')
                continue
            elif line.startswith(">>>>>>>"):
                write = True
                continue
            elif write:
                wble.write(line)
    wble.close()

    if suffix != '':
        os.rename(filename, filename + suffix)
    os.rename(nname, filename)


# -----------------------------------------------------------------------------
def gtx_nochid(args):
    """nochid - report log entries that don't have a Change-Id
    """
    prs = optparse.OptionParser()
    prs.add_option('-d',  '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    (opts, _) = prs.parse_args(args)

    if opts.debug:
        pdb.set_trace()

    try:
        result = pexpect.run("git --no-pager log")
        current = ''
        for line in result.split("\n"):
            if line.startswith("\x1b[33mcommit "):
                line = re.sub(r"\x1b\[3*m", "", line)
                if current and "Change-Id:" not in current:
                    print("-----")
                    print current
                    print("===> subsequent %s" % line)
                current = line
            else:
                current += "\n" + line
        if "Change-Id:" not in current:
            print current
    except IOError as err:
        if "Broken pipe" not in str(err):
            raise


# -----------------------------------------------------------------------------
def gtx_rm_untrack(args):
    """rm_untrack - remove untracked files

    @TEST
    """
    prs = optparse.OptionParser()
    prs.add_option('-d',  '--debug',
                   action='store_true', default=False, dest='debug',
                   help='start the debugger')
    prs.add_option('-n',  '--dry-run',
                   action='store_true', default=True, dest='dryrun',
                   help='show what would happen')
    (opts, _) = prs.parse_args(args)

    if opts.debug:
        pdb.set_trace()

    for line in pexpect.run("git status --porcelain").strip().split("\r\n"):
        words = line.split()
        if words[0] == '??':
            print("os.unlink({0})".format(words[1]))
            if not opts.dryrun:
                os.unlink(words[1])


# -----------------------------------------------------------------------------
def contents(path):
    """
    Read a file and return its contents as an array of lines
    """
    with open(path, 'r') as rble:
        rval = rble.readlines()
    return rval


# -----------------------------------------------------------------------------
def call_editor(filename):
    """
    Run an editor on a file
    """
    editor = os.getenv("EDITOR")
    if editor is None:
        editor = pexpect.which("vim")
    if editor is None:
        editor = pexpect.which("vi")
    if editor is None:
        raise StandardError("Can't find an editor")
    os.system("%s %s" % (editor, filename))

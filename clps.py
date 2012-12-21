#!/usr/bin/env python

import getpass
from optparse import OptionParser
import os
import pdb
import pexpect
import re
import sys
import tpbtools
from testhelp import UnderConstructionError
import toolframe
import traceback as tb

"""
 + "clps -f <filename>" should load <filename>

 + "clps" (no args) should attempt to load a default file ($CLPS_FILENAME)
 
 + clps> clip -h  => exits when it should not

 + clps> show -p  => exits when it should not

 x If I say
      clps add -H abc.com -U johndoe

   I should get a prompt for a password and the entry should be added
   to my default password safe file.

 + in shell mode, "help" gets a traceback

 + I think help inside clps is blowing up on 'clps_prolog' or
   'clps_epilog'. Need to protect these from being dispatchable
   somehow.

 + An unrecognized subfunction exits when it should not

 - Need a way to remove old entries

 - it would be helpful to have each entry timestamped so we can tell
   ages and most recent

 - When save overwrites an existing file, the old version should be
   renamed with a timestamp

 - On a clip command, if more than one match is found and the user
   just hits Enter rather than typing a number, we get a traceback.

"""

# ---------------------------------------------------------------------------
def clps_prolog(args):
    default_filename = os.getenv('CLPS_FILENAME')
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under debugger')
    p.add_option('-f', '--filename',
                 action='store', default=None, dest='filename',
                 help='name of password safe to open on startup')

    # print("prolog: incoming args = %s" % args)
    pre_opts = []
    post_opts = []
    idx = 0
    while idx < len(args):
        if args[idx] == '-d':
            pre_opts.append(args[idx])
        elif args[idx] == '-f':
            pre_opts.append(args[idx])
            try:
                idx += 1
                pre_opts.append(args[idx])
            except IndexError:
                print("-f requires an argument")
        elif args[idx] == '-h':
            pre_opts.append(args[idx])
        else:
            post_opts.append(args[idx])
        idx += 1

    try:
        (o, a) = p.parse_args(pre_opts)
    except SystemExit:
        sys.exit(0)

    if o.debug: pdb.set_trace()
    if o.filename == None and default_filename != None:
        clps_load([default_filename])
    elif o.filename != None and o.filename != '':
        clps_load([o.filename])
        
    # print("prolog: return args = %s" % post_opts)
    
    return post_opts
    
# ---------------------------------------------------------------------------
def clps_add(args):
    """add - add a new entry to the password table

    + add -H <host> -u <user>
    + add -H <host> <user>
    + add -H <host>
    + add <host> -u <user>
    + add <host> <user>
    + add <host>
    + add -u <user>
    + add
    
    Missing information will be requested, so you can just type 'add'
    and let clps prompt you for all three pieces of info. clps will
    always prompt for password (and read it without echoing).
    """
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under debugger')
    p.add_option('-H', '--host',
                 action='store', default='', dest='hostname',
                 help='record a hostname')
    p.add_option('-u', '--username',
                 action='store', default='', dest='username',
                 help='record a username')
    try:
        (o, a) = p.parse_args(args)
    except SystemExit:
        return

    if o.debug: pdb.set_trace()
    
    try:
        hostname = username = ''
        if o.hostname != '':
            hostname = o.hostname
        if o.username != '':
            username = o.username
        if hostname == '' and 0 < len(a):
            hostname = a.pop(0)
        if username == '' and 0 < len(a):
            username = a.pop(0)
        if hostname == '':
            hostname = raw_input("Hostname: ")
        if username == '':
            username = raw_input("Username: ")

        password = getpass.getpass("Password: ")

        data_store(hostname, username, password)
    except:
        tb.print_exc()
        sys.exit()

# ---------------------------------------------------------------------------
def clps_clip(args):
    """clip - copy a password into the clipboard for pasting

    clip [-H|-u|-p] <regex>

    Search the list of password entries, applying the regex to
    hostnames, usernames, or passwords (or all three if no options are
    given). If one match is found, copy the password into the
    clipboard. If more than one match is found, list them and ask the
    user to select one to copy to the clipboard.
    """
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under debugger')
    p.add_option('-H', '--host',
                 action='store', default='', dest='hostname',
                 help='search on hostnames')
    p.add_option('-u', '--username',
                 action='store', default='', dest='username',
                 help='search on usernames')
    p.add_option('-p', '--password',
                 action='store', default='', dest='password',
                 help='search on passwords')
    try:
        (o, a) = p.parse_args(args)
    except SystemExit:
        return

    if o.debug: pdb.set_trace()

    result = data_lookup(o.hostname, o.username, o.password)
    if 0 == len(result):
        print("No match found")
    elif 1 == len(result):
        # print("copy password from result into clipboard")
        copy_to_clipboard(result[0][2])
    else:
        cdx = 1
        for entry in result:
            print(" %3d. %s / %s" % (cdx, entry[0], entry[1]))
            cdx += 1
            
        choice = raw_input("Please make a selection> ")
        copy_to_clipboard(result[int(choice) - 1][2])
        # print("copy password from result[int(choice)] into clipboard")

# ---------------------------------------------------------------------------
def clps_load(args):
    """load - read an encrypted file of password information

    load <filename>
    """
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under debugger')
    p.add_option('-p', '--plain',
                 action='store_true', default=False, dest='plaintext',
                 help='load plaintext, do not try to decrypt')
    try:
        (o, a) = p.parse_args(args)
    except SystemExit:
        return

    if o.debug: pdb.set_trace()
    
    if 1 == len(a):
        filename = a.pop(0)
    else:
        raise StandardError('load requires a filename')

    if o.plaintext:
        f = open(filename, 'r')
        for line in f.readlines():
            [h, u, p] = line.rstrip().split('!@!', 2)
            data_store(h, u, p)
        f.close()
    else:
        passphrase = getpass.getpass()
        f = os.popen("gpg -d --passphrase %s < %s 2>/dev/null"
                     % (passphrase, filename))
        for line in f.readlines():
            if line.strip() == '':
                continue
            [h, u, p] = line.rstrip().split('!@!', 2)
            data_store(h, u, p)
        f.close()

# ---------------------------------------------------------------------------
def clps_save(args):
    """save - write out an encrypted file of password information

    save <filename>
    """
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under debugger')
    try:
        (o, a) = p.parse_args(args)
    except SystemExit:
        return

    if o.debug: pdb.set_trace()
        
    if 1 == len(a):
        filename = a.pop(0)
    else:
        raise StandardError('save requires a filename')

    passphrase = getpass.getpass()
    f = os.popen('gpg -c --passphrase %s > %s' % (passphrase, filename), 'w')
    all = data_lookup('', '', '')
    for (h, u, p) in all:
        f.write('%s!@!%s!@!%s\n' % (h, u, p))
    f.close()

# ---------------------------------------------------------------------------
def clps_show(args):
    """show - display the password entries in the table

    show [-P] [<regex>]

    Without <regex>, show all entries. Without -P, show only host and
    usernames.
    """
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under debugger')
    p.add_option('-P', '--pwd',
                 action='store_true', default=False, dest='pwd',
                 help='show passwords')
    try:
        (o, a) = p.parse_args(args)
    except SystemExit:
        return
    
    if o.debug: pdb.set_trace()

    rgx = ''
    fmt = "%-25s %-25s %-25s"
    if 0 < len(a):
        rgx = a.pop(0)

    all = data_lookup('', '', '')
    for (h,u,p) in all:
        if o.pwd:
            if re.search(rgx, h) or re.search(rgx, u) or re.search(rgx, p):
                print(fmt % (h, u, p))
        else:
            if re.search(rgx, h) or re.search(rgx, u):
                print(fmt % (h, u, ""))

# ---------------------------------------------------------------------------
def copy_to_clipboard(value):
    p = os.popen("pbcopy", 'w')
    p.write(value)
    p.close()

# ---------------------------------------------------------------------------
def data_lookup(hostname, username, password):
    global data
    try:
        rval = []
        for (h, u, p) in data:
            hm = re.search(hostname, h)
            um = re.search(username, u)
            pm = re.search(password, p)
            if hm and um and pm:
                rval.append([h, u, p])
    except NameError:
        data = []
        rval = data
    return rval

# ---------------------------------------------------------------------------
def data_store(hostname, username, password):
    global data

    try:
        data.append([hostname, username, password])
    except NameError:
        data = []
        data.append([hostname, username, password])

# ---------------------------------------------------------------------------
class ClipTest(toolframe.unittest.TestCase):
    prompt = "clps> "
    cmdlist = ['add', 'clip', 'load', 'save', 'show', 'help']

    # -----------------------------------------------------------------------
    def setUp(self):
        if None != os.getenv('CLPS_FILENAME'):
            del os.environ['CLPS_FILENAME']

    # -----------------------------------------------------------------------
    def test_clip_by_host_multi(self):
        global data
        data = [['foobar.com', 'username', 'password'],
                ['sumatra.org', 'chairil', 'Bukittinggi'],
                ['java.org', 'khalida', 'Surabaya']]

        S = pexpect.spawn("clps")

        for item in data:
            S.expect(self.prompt)
            S.sendline("add -H %s -u %s" % (item[0], item[1]))
            S.expect("Password:")
            S.sendline(item[2])

        S.expect(self.prompt)
        S.sendline("clip -H \\.org")
        
        S.expect("Please make a selection> ")

        self.assertEqual('sumatra.org' in S.before, True)
        self.assertEqual('java.org' in S.before, True)

        S.sendline("2")
        # S.expect("Password for khalida@java.org copied to clipboard")
        S.expect(self.prompt)
        S.sendline("quit")
        S.expect(pexpect.EOF)

        S = pexpect.spawn("pbpaste")
        S.expect(pexpect.EOF)
        self.assertEqual('Surabaya' in S.before, True)
        
    # -----------------------------------------------------------------------
    def test_clip_by_host_one(self):
        global data
        data = [['foobar.com', 'username', 'password']]

        # clear the clipboard
        os.system("pbcopy < /dev/null")
        
        clps_clip(['clip', '-H', '.*bar.*'])
        S = pexpect.spawn('pbpaste')
        S.expect(pexpect.EOF)
        self.assertEqual('password' in S.before, True)
    
    # -----------------------------------------------------------------------
    def test_clip_by_pwd_multi(self):
        global data
        data = [['foobar.com', 'username', 'password'],
                ['sumatra.org', 'chairil', 'Bukittinggi'],
                ['java.org', 'khalida', 'Surabaya']]

        S = pexpect.spawn("clps")

        for item in data:
            S.expect(self.prompt)
            S.sendline("add -H %s -u %s" % (item[0], item[1]))
            S.expect("Password:")
            S.sendline(item[2])

        S.expect(self.prompt)
        S.sendline("clip -p .*r.*")
        
        S.expect("Please make a selection> ")

        self.assertEqual('foobar.com' in S.before, True)
        self.assertEqual('java.org' in S.before, True)

        S.sendline("1")

        S.expect(self.prompt)
        S.sendline("quit")
        S.expect(pexpect.EOF)

        S = pexpect.spawn("pbpaste")
        S.expect(pexpect.EOF)
        self.assertEqual('password' in S.before, True)
        
    # -----------------------------------------------------------------------
    def test_clip_by_pwd_one(self):
        global data
        data = [('foobar.com', 'username', 'password')]

        # clear the clipboard
        os.system("pbcopy < /dev/null")
        
        clps_clip(['clip', '-p', '.*sswo.*'])
        S = pexpect.spawn('pbpaste')
        S.expect(pexpect.EOF)
        self.assertEqual('password' in S.before, True)
    
    # -----------------------------------------------------------------------
    def test_clip_by_user_multi(self):
        global data
        data = [['foobar.com', 'username', 'password'],
                ['sumatra.org', 'chairil', 'Bukittinggi'],
                ['java.org', 'khalida', 'Surabaya']]

        S = pexpect.spawn("clps")

        for item in data:
            S.expect(self.prompt)
            S.sendline("add -H %s -u %s" % (item[0], item[1]))
            S.expect("Password:")
            S.sendline(item[2])

        S.expect(self.prompt)
        S.sendline("clip -u .*a[im].*")
        
        S.expect("Please make a selection> ")

        self.assertEqual('foobar.com' in S.before, True)
        self.assertEqual('sumatra.org' in S.before, True)

        S.sendline("2")

        S.expect(self.prompt)
        S.sendline("quit")
        S.expect(pexpect.EOF)

        S = pexpect.spawn("pbpaste")
        S.expect(pexpect.EOF)
        self.assertEqual('Bukittinggi' in S.before, True)
    
    # -----------------------------------------------------------------------
    def test_clip_by_user_one(self):
        global data

        # clear the clipboard
        os.system("pbcopy < /dev/null")

        data = [('foobar.com', 'username', 'password')]

        clps_clip(['clip', '-u', '.*serna.*'])
        S = pexpect.spawn('pbpaste')
        S.expect(pexpect.EOF)
        self.assertEqual('password' in S.before, True)
    
    # -----------------------------------------------------------------------
    def test_cmd_opt_h(self):
        S = pexpect.spawn("clps")
        S.expect(self.prompt)

        cmdl = [x for x in self.cmdlist if x != 'help']
        for cmd in cmdl:
            # print cmd
            S.sendline('%s -h' % cmd)
            S.expect(self.prompt)

            self.assertEqual('Usage:' in S.before, True)
            self.assertEqual('--debug' in S.before, True)
            self.assertEqual('0' in S.before, False)

        S.sendline('quit')
        S.expect(pexpect.EOF)
    
    # -----------------------------------------------------------------------
    def test_cmd_bad_opt(self):
        S = pexpect.spawn("clps")
        S.expect(self.prompt)

        cmdl = [x for x in self.cmdlist if x != 'help']
        for cmd in cmdl:
            # print cmd
            S.sendline('%s -x' % cmd)
            S.expect(self.prompt)

            self.assertEqual('Usage:' in S.before, True)
            self.assertEqual('no such option' in S.before, True)
            self.assertEqual('-x' in S.before, True)

        S.sendline('quit')
        S.expect(pexpect.EOF)
    
    # -----------------------------------------------------------------------
    def test_clps_opt_h(self):
        S = pexpect.spawn("clps -h")
        S.expect(pexpect.EOF)
        self.assertEqual('debug' in S.before, True)
        
    # -----------------------------------------------------------------------
    def test_copy_to_clipboard(self):
        test_value = 'Brobdinagian'
        copy_to_clipboard(test_value)
        S = pexpect.spawn("pbpaste")
        S.expect(pexpect.EOF)
        self.assertEqual(test_value in S.before, True)

    # -----------------------------------------------------------------------
    def test_dlup_by_host(self):
        global data

        data = [['hostname.com', 'username', 'password'],
                ['google.com', 'nameroon', 'broadsword']]

        # match more than one
        a = data_lookup(r'\.com', '', '')
        
        # match just one
        b = data_lookup('hostname.com', '', '')

        # match none
        c = data_lookup('nomatch', '', '')

        self.assertEqual(a, data)
        self.assertEqual(b, [data[0]])
        self.assertEqual(c, [])
        
    # -----------------------------------------------------------------------
    def test_dlup_by_hp(self):
        global data

        data = [['hostname.com', 'username', 'password'],
                ['google.com', 'nameroon', 'broadsword']]

        # match more than one
        a = data_lookup(r'\.com', '', 'sword')
        
        # match just one by hostname
        b = data_lookup('google.com', '', 'sword')

        # match just one by password
        c = data_lookup(r'\.com', '', 'broad')

        # match none by hostname
        d = data_lookup('squiggle', '', 'sword')

        # match none by password
        e = data_lookup(r'\.com', '', 'nomatch')

        self.assertEqual(a, data)
        self.assertEqual(b, [data[1]])
        self.assertEqual(c, [data[1]])
        self.assertEqual(d, [])
        self.assertEqual(e, [])
        
    # -----------------------------------------------------------------------
    def test_dlup_by_hpu(self):
        global data

        data = [['hostname.com', 'username', 'password'],
                ['google.com', 'nameroon', 'broadsword']]

        # match more than one
        a = data_lookup(r'\.com', '', 'sword')

        # match just one by hostname
        b = data_lookup('tname', 'name', 'sword')

        # match just one by password
        c = data_lookup(r'\.com', 'name', 'broad')

        # match just one by username
        d = data_lookup(r'\.com', 'rname', 'sword')

        # match none by hostname
        e = data_lookup('aardvark', 'name', 'sword')

        # match none by password
        f = data_lookup(r'o.*\.com', 'name', 'nomatch')

        # match none by username
        g = data_lookup(r'o.*\.com', 'nomatch', 'sword')

        self.assertEqual(a, data)
        self.assertEqual(b, [data[0]])
        self.assertEqual(c, [data[1]])
        self.assertEqual(d, [data[0]])
        self.assertEqual(e, [])
        self.assertEqual(f, [])
        self.assertEqual(g, [])
        
    # -----------------------------------------------------------------------
    def test_dlup_by_hu(self):
        global data

        data = [['hostname.com', 'username', 'password'],
                ['google.com', 'nameroon', 'broadsword']]

        # match more than one
        a = data_lookup(r'\.com', 'name', '')

        # match just one by hostname
        b = data_lookup('tname', 'name', '')

        # match just one by username
        c = data_lookup(r'\.com', 'roon', '')

        # match none by hostname
        d = data_lookup('aardvark', 'name', '')

        # match none by username
        e = data_lookup(r'o.*\.com', 'nomatch', '')

        self.assertEqual(a, data)
        self.assertEqual(b, [data[0]])
        self.assertEqual(c, [data[1]])
        self.assertEqual(d, [])
        self.assertEqual(e, [])
        
    # -----------------------------------------------------------------------
    def test_dlup_by_pu(self):
        global data

        data = [['hostname.com', 'username', 'password'],
                ['google.com', 'nameroon', 'broadsword']]

        # match more than one
        a = data_lookup('', 'name', 'sword')

        # match just one by password
        b = data_lookup('oog', 'name', 'broad')

        # match just one by username
        c = data_lookup('', 'ernam', 'sword')

        # match none by password
        d = data_lookup('', 'name', 'nomatch')

        # match none by username
        e = data_lookup('', 'nomatch', 'sword')

        self.assertEqual(a, data)
        self.assertEqual(b, [data[1]])
        self.assertEqual(c, [data[0]])
        self.assertEqual(d, [])
        self.assertEqual(e, [])
        
    # -----------------------------------------------------------------------
    def test_dlup_by_pwd(self):
        global data

        data = [['hostname.com', 'username', 'password'],
                ['google.com', 'nameroon', 'broadsword']]

        # match more than one
        a = data_lookup('', '', 'sword')
        
        # match just one
        b = data_lookup('', '', 'broad')

        # match none
        c = data_lookup('', '', 'nomatch')

        self.assertEqual(a, data)
        self.assertEqual(b, [data[1]])
        self.assertEqual(c, [])
        
    # -----------------------------------------------------------------------
    def test_dlup_by_user(self):
        global data

        data = [['hostname.com', 'username', 'password'],
                ['google.com', 'nameroon', 'broadsword']]

        # match more than one
        a = data_lookup('', 'name', '')
        
        # match just one
        b = data_lookup('', 'use', '')

        # match none
        c = data_lookup('', 'nomatch', '')

        self.assertEqual(a, data)
        self.assertEqual(b, [data[0]])
        self.assertEqual(c, [])
        
    # -----------------------------------------------------------------------
    def test_dstore_empty(self):
        global data

        data = []
        data_store('hostname.com', 'username', 'password')
        a = data_lookup('hostname.com', '', '')
        self.assertEqual(a, [['hostname.com', 'username', 'password']])
        
    # -----------------------------------------------------------------------
    def test_dstore_full(self):
        global data
        
        data = [['hostname.com', 'username', 'password'],
                ['google.com', 'nameroon', 'broadsword']]
        data_store('flack.org', 'sinbad', 'mermaid')
        a = data_lookup('', '', '')
        self.assertEqual(len(a), 3)
        self.assertEqual(data[0] in a, True)
        self.assertEqual(data[1] in a, True)
        self.assertEqual(['flack.org', 'sinbad', 'mermaid'] in a, True)
        
    # -----------------------------------------------------------------------
    def test_help_noarg(self):
        S = pexpect.spawn('clps')
        S.expect(self.prompt)
        S.sendline('help')

        which = S.expect([self.prompt, pexpect.EOF])
        if 0 == which:
            for cmd in self.cmdlist:
                self.assertEqual(cmd in S.before, True)
        else:
            self.fail('help failed')

        S.sendline('quit')
        S.expect(pexpect.EOF)

    # -----------------------------------------------------------------------
    def test_help_cmd(self):
        S = pexpect.spawn('clps')
        S.expect(self.prompt)
        S.sendline('help')

        S.expect(self.prompt)

        for cmd in self.cmdlist:
            S.sendline('help %s' % cmd)
            S.expect(self.prompt)
            x = '%s - ' % cmd
            self.assertEqual(x in S.before, True)

        S.sendline('quit')
        S.expect(pexpect.EOF)

    # -----------------------------------------------------------------------
    def test_load(self):
        data = [['foobar.com', 'username', 'password'],
                ['sumatra.org', 'chairil', 'Bukittinggi'],
                ['java.org', 'khalida', 'Surabaya'],
                ['jellico.net', 'severino', 'foo!@!bar']]

        filename = 'test_load.clps'
        passphrase = 'iChAb0d'
        f = open(filename, 'w')
        f = os.popen('gpg -c --passphrase %s > %s'
                     % (passphrase, filename),
                     'w')
        for item in data:
            # f.write('%s!@!%s!@!%s\n' % (item[0], item[1], item[2]))
            f.write('%s\n' % '!@!'.join(item))
        f.close()
        
        S = pexpect.spawn('clps')
        S.expect(self.prompt)
        S.sendline('load %s' % filename)

        S.expect("Password: ")
        S.sendline(passphrase)
        
        S.expect(self.prompt)
        S.sendline('show')

        S.expect(self.prompt)

        for item in data:
            self.assertEqual(item[0] in S.before, True)
            self.assertEqual(item[1] in S.before, True)
            self.assertEqual(item[2] in S.before, False)

        S.sendline('quit')
        S.expect(pexpect.EOF)

    # -----------------------------------------------------------------------
    def test_optionA_addshow(self):
        prompt = "clps> "
        S = pexpect.spawn("clps")

        S.expect(prompt)
        S.sendline("add host.org")

        S.expect("Username: ")
        S.sendline('anderson')
        
        S.expect("Password: ")
        S.sendline("snoopy")

        S.expect(prompt)
        S.sendline("show")

        S.expect(prompt)
        self.assertEqual("host.org" in S.before, True)
        self.assertEqual("anderson" in S.before, True)
        self.assertEqual("snoopy" not in S.before, True)

        S.sendline("quit")
        S.expect(pexpect.EOF)
        
    # -----------------------------------------------------------------------
    def test_optionAA_addshow(self):
        prompt = "clps> "
        S = pexpect.spawn("clps")

        S.expect(prompt)
        S.sendline("add host.org sally")

        S.expect("Password: ")
        S.sendline("snoopy")

        S.expect(prompt)
        S.sendline("show")

        S.expect(prompt)
        self.assertEqual("host.org" in S.before, True)
        self.assertEqual("sally" in S.before, True)
        self.assertEqual("snoopy" not in S.before, True)

        S.sendline("quit")
        S.expect(pexpect.EOF)
        
    # -----------------------------------------------------------------------
    def test_optionH_addshow(self):
        prompt = "clps> "
        S = pexpect.spawn("clps")

        S.expect(prompt)
        S.sendline("add -H host.org")

        S.expect("Username: ")
        S.sendline("Ben")

        S.expect("Password: ")
        S.sendline("snoopy")

        S.expect(prompt)
        S.sendline("show")

        S.expect(prompt)
        self.assertEqual("host.org" in S.before, True)
        self.assertEqual("Ben" in S.before, True)
        self.assertEqual("snoopy" not in S.before, True)

        S.sendline("quit")
        S.expect(pexpect.EOF)
        
    # -----------------------------------------------------------------------
    def test_optionHa_addshow(self):
        prompt = "clps> "
        S = pexpect.spawn("clps")

        S.expect(prompt)
        S.sendline("add -H host.org freddie")

        S.expect("Password: ")
        S.sendline("snoopy")

        S.expect(prompt)
        S.sendline("show")

        S.expect(prompt)
        self.assertEqual("host.org" in S.before, True)
        self.assertEqual("freddie" in S.before, True)
        self.assertEqual("snoopy" not in S.before, True)

        S.sendline("quit")
        S.expect(pexpect.EOF)
        
    # -----------------------------------------------------------------------
    def test_optionUH_addshow(self):
        prompt = "clps> "
        S = pexpect.spawn("clps")

        S.expect(prompt)
        S.sendline("add -u phineas -H wuzzles.org")

        S.expect("Password: ")
        S.sendline("snoopy")

        S.expect(prompt)
        S.sendline("show")

        S.expect(prompt)
        self.assertEqual("wuzzles.org" in S.before, True)
        self.assertEqual("phineas" in S.before, True)
        self.assertEqual("snoopy" not in S.before, True)

        S.sendline("quit")
        S.expect(pexpect.EOF)
        
    # -----------------------------------------------------------------------
    def test_optionU_addshow(self):
        prompt = "clps> "
        S = pexpect.spawn("clps")

        S.expect(prompt)
        S.sendline("add -u phineas")

        S.expect("Hostname: ")
        S.sendline("arg.org")

        S.expect("Password: ")
        S.sendline("snoopy")

        S.expect(prompt)
        S.sendline("show")

        S.expect(prompt)
        self.assertEqual("arg.org" in S.before, True)
        self.assertEqual("phineas" in S.before, True)
        self.assertEqual("snoopy" not in S.before, True)

        S.sendline("quit")
        S.expect(pexpect.EOF)
        
    # -----------------------------------------------------------------------
    def test_optionUa_addshow(self):
        prompt = "clps> "
        S = pexpect.spawn("clps")
        S.timeout = 5
        
        S.expect(prompt)
        S.sendline("add -u phineas abracadabra.com")

        S.expect("Password: ")
        S.sendline("snoopy")

        S.expect(prompt)
        S.sendline("show")

        S.expect(prompt)
        self.assertEqual("abracadabra.com" in S.before, True)
        self.assertEqual("phineas" in S.before, True)
        self.assertEqual("snoopy" not in S.before, True)

        S.sendline("quit")
        S.expect(pexpect.EOF)
        
    # -----------------------------------------------------------------------
    def test_prompt_addshow(self):
        S = pexpect.spawn("clps")

        S.expect(self.prompt)
        S.sendline("add")

        S.expect("Hostname: ")
        S.sendline("abc.org")

        S.expect("Username: ")
        S.sendline("jock")

        S.expect("Password: ")
        S.sendline("fruitful")

        S.expect(self.prompt)
        S.sendline("show")

        S.expect(self.prompt)
        self.assertEqual("abc.org" in S.before, True)
        self.assertEqual("jock" in S.before, True)
        self.assertEqual("fruitful" not in S.before, True)

        S.sendline("quit")
        S.expect(pexpect.EOF)
        
    # -----------------------------------------------------------------------
    def test_save(self):
        filename = "test_save.clps"
        data = [['foobar.com', 'username', 'password'],
                ['sumatra.org', 'chairil', 'Methuselah'],
                ['java.org', 'khalida', 'Surabaya']]
        S = pexpect.spawn("clps")
        for item in data:
            S.expect(self.prompt)
            S.sendline("add -H %s -u %s" % (item[0], item[1]))
            S.expect("Password:")
            S.sendline(item[2])

        S.expect(self.prompt)
        S.sendline('save %s' % filename)

        S.expect('Password: ')
        S.sendline('test_passphrase')
        
        S.expect(self.prompt)
        S.sendline('quit')

        S.expect(pexpect.EOF)

        self.assertEqual(os.path.exists(filename), True)

        C = tpbtools.contents(filename)
        for item in data:
            for element in item:
                self.assertEqual(element in ''.join(C), False)

    # -----------------------------------------------------------------------
    def test_show_all_nopass(self):
        data = [['foobar.com', 'username', 'password'],
                ['sumatra.org', 'chairil', 'Bukittinggi'],
                ['java.org', 'khalida', 'Surabaya']]

        S = pexpect.spawn("clps")
        for item in data:
            S.expect(self.prompt)
            S.sendline("add -H %s -u %s" % (item[0], item[1]))
            S.expect("Password:")
            S.sendline(item[2])

        S.expect(self.prompt)
        S.sendline('show')

        S.expect(self.prompt)
        for item in data:
            self.assertEqual(item[0] in S.before, True)
            self.assertEqual(item[1] in S.before, True)
            self.assertEqual(item[2] in S.before, False)

        S.sendline('quit')
        S.expect(pexpect.EOF)
        
    # -----------------------------------------------------------------------
    def test_show_all_wpass(self):
        data = [['foobar.com', 'username', 'password'],
                ['sumatra.org', 'chairil', 'Bukittinggi'],
                ['java.org', 'khalida', 'Surabaya']]

        S = pexpect.spawn("clps")
        for item in data:
            S.expect(self.prompt)
            S.sendline("add -H %s -u %s" % (item[0], item[1]))
            S.expect("Password:")
            S.sendline(item[2])

        S.expect(self.prompt)
        S.sendline('show -P')

        S.expect(self.prompt)
        for item in data:
            self.assertEqual(item[0] in S.before, True)
            self.assertEqual(item[1] in S.before, True)
            self.assertEqual(item[2] in S.before, True)

        S.sendline('quit')
        S.expect(pexpect.EOF)

    # -----------------------------------------------------------------------
    def test_show_rgx_nopass(self):
        data = [['foobar.com', 'username', 'password'],
                ['sumatra.org', 'chairil', 'Bukittinggi'],
                ['java.org', 'khalida', 'Surabaya']]

        S = pexpect.spawn("clps")
        for item in data:
            S.expect(self.prompt)
            S.sendline("add -H %s -u %s" % (item[0], item[1]))
            S.expect("Password:")
            S.sendline(item[2])

        S.expect(self.prompt)
        S.sendline('show \\.org')

        S.expect(self.prompt)
        xp = [[False, False, False],
              [True, True, False],
              [True, True, False]]
        for idx in range(0,3):
            for jdx in range(0,3):
                self.assertEqual(data[idx][jdx] in S.before,
                                 xp[idx][jdx])

        S.sendline('quit')
        S.expect(pexpect.EOF)

    # -----------------------------------------------------------------------
    def test_show_rgx_wpass(self):
        data = [['foobar.com', 'username', 'password'],
                ['sumatra.org', 'chairil', 'Bukittinggi'],
                ['java.org', 'khalida', 'Surabaya']]

        S = pexpect.spawn("clps")
        for item in data:
            S.expect(self.prompt)
            S.sendline("add -H %s -u %s" % (item[0], item[1]))
            S.expect("Password:")
            S.sendline(item[2])

        S.expect(self.prompt)
        S.sendline('show -P \\.org')

        S.expect(self.prompt)
        xp = [[False, False, False],
              [True, True, True],
              [True, True, True]]
        for idx in range(0,3):
            for jdx in range(0,3):
                self.assertEqual(data[idx][jdx] in S.before,
                                 xp[idx][jdx])

        S.sendline('quit')
        S.expect(pexpect.EOF)

# pdb.set_trace()
toolframe.tf_launch('clps', noarg='shell')

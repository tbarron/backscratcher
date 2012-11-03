#!/usr/bin/env python

import getpass
from optparse import OptionParser
import os
import pdb
import pexpect
import re
import sys
from testhelp import UnderConstructionError
import toolframe
import traceback as tb

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
    (o, a) = p.parse_args(args)

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
    (o, a) = p.parse_args(args)

    if o.debug: pdb.set_trace()

    result = data_lookup(o.hostname, o.username, o.password)
    if len(result) == 1:
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

def clps_load(args):
    """load - read an encrypted file of password information

    load <filename>
    """
    pass

def clps_save(args):
    """save - write out an encrypted file of password information

    save <filename>
    """
    pass

def clps_show(args):
    """show - display the password entries in the table

    show [-P] [<regex>]

    Without <regex>, show all entries. Without -P, show only host and usernames.
    """
    p = OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help='run under debugger')
    p.add_option('-P', '--pwd',
                 action='store_true', default=False, dest='pwd',
                 help='show passwords')
    (o, a) = p.parse_args(args)

    if o.debug: pdb.set_trace()

    all = data_lookup('', '', '')
    for (h,u,p) in all:
        if o.pwd:
            print("%s %s %s" % (h, u, p))
        else:
            print("%s %s" % (h, u))

def copy_to_clipboard(value):
    p = os.popen("pbcopy", 'w')
    p.write(value)
    p.close()

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

    # -----------------------------------------------------------------------
    def test_clip_by_host_one(self):
        global data
        # raise UnderConstructionError('under construction')
        pdb.set_trace()
        data = [['foobar.com', 'username', 'password']]

        clps_clip(['clip', '-H', '.*bar.*'])
        S = pexpect.spawn('pbpaste')
        S.expect(pexpect.EOF)
        self.assertEqual('password' in S.before, True)
    
    # -----------------------------------------------------------------------
    def test_clip_by_host_multi(self):
        # !@!
        raise UnderConstructionError('under construction')
    
    # -----------------------------------------------------------------------
    def test_clip_by_pwd_one(self):
        global data
        # raise UnderConstructionError('under construction')
        data = [('foobar.com', 'username', 'password')]

        clps_clip(['clip', '-H', '.*bar.*'])
        S = pexepct.spawn('pbpaste')
        S.expect(pexpect.EOF)
        self.assertEqual('password' in S.before, True)
    
    # -----------------------------------------------------------------------
    def test_clip_by_pwd_multi(self):
        # !@!
        raise UnderConstructionError('under construction')
    
    # -----------------------------------------------------------------------
    def test_clip_by_user_one(self):
        # !@!
        raise UnderConstructionError('under construction')
    
    # -----------------------------------------------------------------------
    def test_clip_by_user_multi(self):
        # !@!
        raise UnderConstructionError('under construction')
    
    # -----------------------------------------------------------------------
    def test_copy_to_clipboard(self):
        # !@!
        raise UnderConstructionError('under construction')
    
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
    def test_load(self):
        # !@!
        raise UnderConstructionError('under construction')
        
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
        prompt = "clps> "
        S = pexpect.spawn("clps")

        S.expect(prompt)
        S.sendline("add")

        S.expect("Hostname: ")
        S.sendline("abc.org")

        S.expect("Username: ")
        S.sendline("jock")

        S.expect("Password: ")
        S.sendline("fruitful")

        S.expect(prompt)
        S.sendline("show")

        S.expect(prompt)
        self.assertEqual("abc.org" in S.before, True)
        self.assertEqual("jock" in S.before, True)
        self.assertEqual("fruitful" not in S.before, True)

        S.sendline("quit")
        S.expect(pexpect.EOF)
        
    # -----------------------------------------------------------------------
    def test_save(self):
        # !@!
        raise UnderConstructionError('under construction')
        
    # -----------------------------------------------------------------------
    def test_show_all_nopass(self):
        # !@!
        raise UnderConstructionError('under construction')

    # -----------------------------------------------------------------------
    def test_show_all_wpass(self):
        # !@!
        raise UnderConstructionError('under construction')

    # -----------------------------------------------------------------------
    def test_show_rgx_nopass(self):
        # !@!
        raise UnderConstructionError('under construction')

    # -----------------------------------------------------------------------
    def test_show_rgx_wpass(self):
        # !@!
        raise UnderConstructionError('under construction')

toolframe.tf_launch('clps', noarg='shell')

#!/usr/bin/python
"""
fabricate stuff

For a list of things that can be fabricated,

   fab help 

Fab is a python-based make substitute for when a make program is not
available or make won't quite do what you want. The equivalent of
'Makefile' for fab is 'fabfile.py'.

In fabfile.py, you can include any python code you want. fab makes
some assumpstions about the structure of your code in fabfile.py:

 - fabfile.py entry points (equivalent to make targets) have names
   beginning with 'fab_' -- eg., fab_install, fab_clean, etc.

 - fabfile.py entry points accept a single argument which is a list of
   strings which may include options, suitable for parsing with an
   OptionParser().

 - each fabfile.py entry point routine begins with a __doc__ string,
   delimited by triple quotes. The first line of the __doc__ string
   provides a short oneline description which is displayed by 'fab
   help'. The second line is blank. The third line provides usage
   information. The fourth line is blank. The fifth line and following
   provide a detailed description of what the function does.

Copyright (C) 1995 - <the end of time>  Tom Barron
  tom.barron@comcast.net
  177 Crossroads Blvd
  Oak Ridge, TN  37830

This software is licensed under the CC-GNU GPL. For the full text of
the license, see http://creativecommons.org/licenses/GPL/2.0/

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import os
import re
import sys

if os.path.exists('fabfile.py'):
    from fabfile import *
    
# ---------------------------------------------------------------------------
def main(args):
    eval("%s_%s(args[2:])" % (prefix(), args[1]))
        
# ---------------------------------------------------------------------------
def fab_help(args):
    '''help - show this list
    
    usage: fab help [function-name]
    
    If a function name is given, show the functions __doc__ member.
    Otherwise, show a list of functions based on the first line of
    each __doc__ member.
    '''
    global d

    pfx = prefix()
    try:
        if '%s_%s' % (pfx, args[0]) in d:
            print eval('%s_%s.__doc__' % (pfx, args[0]))
            return
        
    except IndexError:
        for o in d:
            if '%s_' % pfx in o:
                x = eval('%s.__doc__' % o)
                f = x.split('\n')[0]
                print '   ' + f

# ---------------------------------------------------------------------------
def prefix():
    return 'fab'

# ---------------------------------------------------------------------------
global d
d = dir()

sname = sys.argv[0]
if sname.endswith('.py') and '-L' in sys.argv:
    pname = re.sub('.py$', '', sname)
    print("creating symlink: %s -> %s" % (pname, sname))
    os.symlink(sname, pname)
elif sname.endswith('.py') and __name__ == '__main__':
    unittest.main()
elif not sname.endswith('.py') and __name__ == '__main__':
    main(sys.argv)

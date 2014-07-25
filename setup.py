from distutils.core import setup
from distutils.sysconfig import get_python_lib
from distutils.file_util import copy_file
import glob
import os
import time

bscr_root = os.path.join(get_python_lib(), "bscr")
copy_file("README.md", "README")
scripts = ["align",
           "ascii",
           "bscr",
           "calc",
           "chron",
           "dt",
           "fl",
           "fx",
           "hd",
           "jcal",
           "list",
           "mag",
           "odx",
           "perrno",
           "workrpt",
           "xclean",
           ]
ep_d = {
    'console_scripts':
    ["%s = bscr.%s:main" % (x, x) for x in scripts]
    }

f = open(".bscr_version", 'r')
version = f.read().strip()
f.close()

# print scrlist
setup(name='backscratcher',
      version=version,
      packages=['bscr', 'bscr/test'],
      entry_points = ep_d,
      author="Tom Barron",
      author_email='tom.barron@comcast.net',
      url='https://github.com/tbarron/backscratcher/',
      data_files=[(bscr_root, [".bscr_version", "README"])]
      )

from distutils.core import setup
from distutils.sysconfig import get_python_lib
from distutils.file_util import copy_file
import glob
import os
import time

bscr_root = os.path.join(get_python_lib(), "bscr")
scrlist = glob.glob("bin/*")
copy_file("README.md", "README")
# print scrlist
setup(name='backscratcher',
      version='learn',
      packages=['bscr', 'bscr/test'],
      scripts=scrlist,
      author="Tom Barron",
      author_email='tom.barron@comcast.net',
      url='https://github.com/tbarron/backscratcher/',
      data_files=[(bscr_root, [".bscr_version", "README"])]
      )

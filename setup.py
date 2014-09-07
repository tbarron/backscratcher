from setuptools import setup
from setuptools import distutils
import glob
import os
import sys
import time

bscr_root = os.path.join(distutils.old_get_python_lib(), "bscr")
distutils.file_util.copy_file("README.md", "README")
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
           "pytool",
           "workrpt",
           "xclean",
           ]
ep_d = {
    'console_scripts':
    ["%s = bscr.%s:main" % (x, x) for x in scripts]
    }

exec(open(os.path.join(bscr_root, "version.py")).read())
# if not os.path.exists(".bscr_version"):
#     os.system("git describe > .bscr_version")
# f = open(".bscr_version", 'r')
# version = f.read().strip()
# f.close()

# print scrlist
setup(name='backscratcher',
      version=__version__,
      packages=['bscr', 'bscr/test'],
      entry_points = ep_d,
      author="Tom Barron",
      author_email='tom.barron@comcast.net',
      url='https://github.com/tbarron/backscratcher/',
      data_files=[(bscr_root, [".bscr_version", "README"])],
      install_requires=['pexpect == 3.3'],
      tests_require=['pep8==1.5.7',
                     'python-termstyle==0.1.10',
                     'virtualenv==1.11.6',
                     'wsgiref==0.1.2',
                     'pexpect==3.3']
      )

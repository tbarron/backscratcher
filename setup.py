from setuptools import setup
from setuptools import distutils
import glob
import os
import site
import sys
import time

# bscr_root = os.path.join(distutils.old_get_python_lib(), "bscr")
# bscr_root = os.path.join(os.path.dirname(site.__file__), "bscr")
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

exec(open(os.path.join("bscr", "version.py")).read())
setup(name='backscratcher',
      version=__version__,
      packages=['bscr', 'bscr/test'],
      entry_points = ep_d,
      author="Tom Barron",
      author_email='tom.barron@comcast.net',
      url='https://github.com/tbarron/backscratcher/',
      data_files=[('', ["README"])],
      install_requires=['pexpect == 3.3'],
      tests_require=['pep8==1.5.7',
                     'python-termstyle==0.1.10',
                     'virtualenv==1.11.6',
                     'wsgiref==0.1.2',
                     'pexpect==3.3']
      )

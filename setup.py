from distutils.core import setup
import glob
import time

scrlist = glob.glob("bin/*")
setup(name='backscratcher',
      version='learn',
      packages=['bscr', 'bscr/test'],
      scripts=scrlist,
      author="Tom Barron",
      author_email='tom.barron@comcast.net',
      url='https://github.com/tbarron/backscratcher/'
      )

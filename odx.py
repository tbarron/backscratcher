#!/usr/bin/python
"""
odx

Take as input a number. It can be hex (prefixed with '0x'), octal
(prefixed with '0'), or decimal (no prefix). The response will show
the same value in all three formats.

EXAMPLES

   $ odx 017     # (octal)
   017 -> 15 / 0xf / 017
   
   $ odx 95      # (decimal)
   95 -> 95 / 0x5f / 0137
   
   $ odx 0x33    # (hexadecimal)
   0x33 -> 51 / 0x33 / 063
   
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
import toolframe

def main(args):
    for str in args[1:]:
        if str.startswith("0x"):
            val = int(str, 16)
        elif str.startswith("0"):
            val = int(str, 8)
        else:
            val = int(str)

        print("%s -> 0%o / %d / 0x%x" % (str, val, val, val))
        
toolframe.ez_launch(main)

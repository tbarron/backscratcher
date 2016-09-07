"""
hexdump a file or data stream

Display the contents of <filename> in mixed hexadecimal / alphanumeric
format, 16 bytes to a line.

SYNOPSIS

 hd.pl <filename>

LICENSE

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
import optparse
import sys


# -----------------------------------------------------------------------------
def main(argv=None):
    """
    CLEP
    """
    if argv is None:
        argv = sys.argv

    prs = optparse.OptionParser(usage=usage())
    (_, args) = prs.parse_args(argv)

    if 0 < len(args[1:]):
        for filename in args[1:]:
            if filename == '-':
                hexdump(sys.stdin)
            else:
                rble = open(filename, 'r')
                hexdump(rble)
                rble.close()
    else:
        hexdump(sys.stdin)


# -----------------------------------------------------------------------------
def hexdump(rble, wble=sys.stdout):
    """
    Read *rble*, format the stream as a hexdump, and send it to *wble*.
    """
    data = rble.read()
    for idx in range(0, len(data), 16):
        for offs in range(0, min(len(data)-idx, 16)):
            if 0 == offs % 4:
                wble.write(" ")
            wble.write("%02x " % ord(data[idx+offs]))
        for offs in range(min(len(data)-idx, 16), 16):
            if 0 == offs % 4:
                wble.write(" ")
            wble.write("   ")
        wble.write("  ")
        for offs in range(0, min(len(data)-idx, 16)):
            if 0 == offs % 8:
                wble.write(" ")
            if data[idx+offs] < ' ' or 0x7f < ord(data[idx+offs]):
                wble.write(".")
            else:
                wble.write("%c" % data[idx+offs])
        for offs in range(min(len(data)-idx, 16), 16):
            if 0 == offs % 8:
                wble.write(" ")
            wble.write(" ")
        wble.write("\n")


# ---------------------------------------------------------------------------
def usage():
    """
    usage
    """
    return """hd

    Hexdump stdin or a file."""

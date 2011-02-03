#!/usr/bin/perl

=head1 NAME

odx - octal, decimal, hex display

=head1 SYNOPSIS

 odx 017
 odx 95
 odx 0x33

=head1 DESCRIPTION

The first argument is parsed as an octal number if it begins with a 0,
as a hexadecimal value if it begins with '0x', or as a decimal value
otherwise. Whatever the value is determined to be, it is displayed in
all three formats.

=head1 LICENSE

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

=cut

foreach $str (@ARGV)
{
   if ($str =~ /^0x/)
   {
      $val = hex($str);
   }
   elsif ($str =~ /^0/)
   {
      $val = oct($str);
   }
   else
   {
      $val = $str;
   }
   
   printf("%s -> %d / 0x%x / 0%o\n", $str, $val, $val, $val);
}

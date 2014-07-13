#!/usr/bin/perl
# ========================================================================
# replay
#
# @(#) xxx
#
# Syntax:
#   
#   
# History:
#  97-03-08    tb    created
#
# Notes:
#
# ========================================================================
use Getopt::Long;

$interval = 10;
GetOptions("-c!" => \$change,
           "-i=i" => \$interval);

$cmd = join( " ", @ARGV );
while (1)
{
   open(STUFF, "$cmd |");
   @stuff = <STUFF>;
   close(STUFF);
   $stuff = join(" ", @stuff);

   if ($change)
   {
      if ($stuff ne $oldstuff)
      {
         system( "clear" );
         print( "$cmd\n" );
         print( "$stuff\n");
         $oldstuff = $stuff;
      }
      sleep(1)
   }
   else
   {
      system( "clear" );
      print( "$cmd\n" );
      print( "$stuff\n");
      sleep( $interval );
   }
}

__END__

=head1 NAME

replay - monitor the output of a command

=head1 USAGE

 replay -c "<command>"
 replay [-i <time>] "<command>"

=head1 DESCRIPTION

Repeatedly display the output of a command or series of commands until
the user interrupts the program.

With the -c option, the output is updated when it changes. The command
is run once per second.

With the -i option, the output is updated every time <time> seconds
elapse.

With no option, the output is updated every 10 seconds.

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


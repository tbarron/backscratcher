#!/usr/bin/perl
# ===========================================================================
# summarize
#
# @(#) scan a file and ignore uninteresting stuff
#
# Syntax:
#   summary --uninteresting <filename> <infile1> <infile2> ...
#
# History:
#   2006-07-19    tpb    created
#
# ===========================================================================
=head1 NAME

summarize - scan a file and ignore uninteresting stuff

=head1 SYNOPSIS

 summary --uninteresting <filename> <infile1> <infile2> ...

=head1 DESCRIPTION

This program applies Marcus Ranum's "Artificial Ignorance" technique
to an arbitrary list of files. (Ranum, 1997)

The list of "uninteresting" regular expressions to be ignored are read
from <filename> and then applied to each of the input files in turn.

=head1 REFERENCES

Ranum, M. (1997). artificial ignorance: how-to guide. Retrieved
2006-07-19 from http://www.ranum.com/security/computer_security/index.html.

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

# ===========================================================================
use strict;
use Getopt::Long;

# ===========================================================================
sub main
{
   my ($filename, $in, @uninteresting);

   GetOptions("-uninteresting=s" => \$filename);

   @uninteresting = contents($filename);

   foreach $in (@ARGV)
   {
      summarize(\@uninteresting, $in);
   }
}

# ===========================================================================
sub contents
{
   my ($filename, $line, @rval);

   ($filename) = @_;

   open(IN, "< $filename");
   while ($line = <IN>)
   {
      chomp($line);
      push(@rval, $line);
   }
   close(IN);

   return @rval;
}

# ===========================================================================
sub ignore
{
   my ($ignore, $ignref, $line, $rgx);

   ($ignref, $line) = @_;

   $ignore = 0;
   foreach $rgx (@{$ignref})
   {
      if ($line =~ /$rgx/)
      {
         $ignore = 1;
         last;
      }
   }

   return $ignore;
}

# ===========================================================================
{
   my @ignoreList;
   my $ignoreListDefined;

# ---------------------------------------------------------------------------
sub register_ignorable
{
   push(@ignoreList, @_);
   $ignoreListDefined = 1;
}
}

# ===========================================================================
sub summarize
{
   my ($filename, $ignore, $ignref, $line, $rgx);

   ($ignref, $filename) = @_;

   open(IN, "< $filename");
   while ($line = <IN>)
   {
      print("$line") if (!ignore($ignref, $line));
   }
   close(IN);
}

# ===========================================================================
main();


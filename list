#!/usr/bin/perl
# ---------------------------------------------------------------------------
# list - arithmetic on lists (subtraction, union, intersection)
#
#    list <op> <cmdA> <cmdB>
#
# <op> - { minus | union | intersection }
# <cmdA> - a command (pipeline) to produce list A
# <cmdB> - a command (pipeline) to produce list B
# ---------------------------------------------------------------------------

$operation = $ARGV[0];
$Acmd = $ARGV[1];
$Bcmd = $ARGV[2];

if (($operation eq "") || ($Acmd eq "") || ($Bcmd eq ""))
{
   usage();
}

@A = generate_list($Acmd);
@B = generate_list($Bcmd);

eval("\@r = list_$operation(\\\@A, \\\@B)");
foreach $item (@r)
{
   print "$item\n";
}

# ---------------------------------------------------------------------------
sub generate_list
{
   my ($cmd, @rval);

   ($cmd) = @_;

   open(IN, "$cmd |");
   @rval = grep {s/[\r\n]*$//} <IN>;
   close(IN);
   return @rval;
}

# ---------------------------------------------------------------------------
sub list_minus
{
   my ($aref, $bref);

   ($bref, $aref) = @_;
   grep($MARK{$_}++, @{$aref});
   @rval = grep(!$MARK{$_}, @{$bref});
   return @rval;
}

# ---------------------------------------------------------------------------
sub list_union
{
   my ($aref, $bref);

   ($aref, $bref) = @_;
   push( @{$aref}, @{$bref} );
   return @{$aref};
}

# ---------------------------------------------------------------------------
sub list_intersection
{
   my ($aref, $bref);

   ($aref, $bref) = @_;
   grep($MARK{$_}++, @{$aref});
   @rval = grep($MARK{$_}, @{$bref});
   return @rval;
}

# ---------------------------------------------------------------------------
sub usage
{
   print("\n");
   print("   usage: list {minus|union|intersection}"
         . " '<command A>' '<command B>'\n");
   print("\n");
}

__END__

=head1 NAME

list - set arithmetic on lists (subtraction, union, intersection)

=head1 USAGE

 list minus "cmdA" "cmdB"         # remove cmdB list from cmdA list
 list union "cmdA" "cmdB"         # report the union of the lists
 list intersection "cmdA" "cmdB"  # report the intersection of the lists

=head1 DESCRIPTION

The program accepts an operation and two commands. Each of the
commands are assumed to produce a list of strings. The operation is
applied to the lists. Note that the result of the 'minus' operation
varies with the order of cmdA and cmdB while 'union' and
'intersection' are both commutative.

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


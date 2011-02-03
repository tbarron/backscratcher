#!/usr/bin/perl
# ===========================================================================
# History
# 2002-05-09   tpb  correct implementation of -v
# 2002-10-21   tpb  merged ~/bin/tps, /opt/bin/tps
#                   got -s <sig> working
# 2003-01-03   tpb  don't kill or report parent process or self
#                   non-zero exit code if no processes matched
# ===========================================================================
use Getopt::Long;
use Config;

$psopts = "-ef";
GetOptions("k!" => \$send_kill,
           "l!" => \$list_signals,
           "n!" => \$noexec,
           "h!" => \$send_hup,
           "t!" => \$terse,
           "v!" => \$reverse_match,
           "s=s" => \$signal,
           "p=s" => \$psopts);

defined $Config{sig_name} || die "No signals configured";
foreach $name (split(' ', $Config{sig_name}))
{
   $signo{$name} = $signum;
   $signame[$signum] = $name;
   $signum++;
}

if ($list_signals)
{
   $num = 0;
   foreach $name (@signame)
   {
      printf("%3d: %s (%3d)\n", $num, $signame[$num], $signo{$signame[$num]});
      $num++;
   }
   exit;
}

if ($send_kill && $send_hup)
{
   print("Options -k and -h are mutually exclusive\n");
   exit(1);
}
elsif ($send_kill && ($signal ne ""))
{
   print("Options -k and -s are mutually exclusive\n");
   exit(1);
}
elsif ($send_hup && ($signal ne ""))
{
   print("Options -s and -h are mutually exclusive\n");
   exit(1);
}
elsif (($signal ne "") && 
       (($signame[$signal] eq "") && ($signo{$signal} eq "")))
{
   print("Signal $signal is undefined\n");
   exit(1);
}

$exitcode = 1;
$ppid = getppid();
open(PS, "ps $psopts |");
$pshdr = <PS>;
while ($line = <PS>)
{
   chomp($line);

   if ($reverse_match)
   {
      $match = 1;
      foreach $criterion (@ARGV)
      {
         if (($line =~ /$$/) || ($line =~ /$ppid/) || ($line =~ /$criterion/))
         {
            $match = 0;
         }
      }
      if ($match)
      {
         $exitcode = 0;
         report("$line\n");
         conditional_signal($line);
      }
   }
   else
   {
      $matched_already = 0;
      foreach $criterion (@ARGV)
      {
         next if $matched_already;

         if (($line !~ /$$/) && ($line !~ /$ppid/) && ($line =~ /$criterion/))
         {
            $matched_already = 1;
            $exitcode = 0;
            report("$line\n");
            conditional_signal($line);
         }
      }
   }
}

close(PS);
exit($exitcode);

# ===========================================================================
sub conditional_signal
{
   my ($line) = @_;

   my ($pid) = ($line =~ /^\s*\w+\s+(\d+)\s/);
   if (($signal ne "") || $send_kill || $send_hup)
   {
      $signal = (($send_kill) ? $signame[$signo{KILL}] :
                 ($send_hup) ? $signame[$signo{HUP}] :
                 ($signal =~ /^[0-9]+$/) ? $signame[$signal] :
                 $signame[$signo{$signal}]);

      if ($noexec)
      {
         print("would do 'kill -$signal $pid'\n");
      }
      else
      {
         print("doing 'kill -$signal $pid'\n");
         kill("$signal", $pid);
      }
   }
}

# ===========================================================================
sub report
{
   my ($line) = @_;

   if (($pshdr ne "") && (!$terse))
   {
      print("$pshdr");
      $pshdr = "";
   }
   print("$line");
}

__END__

=head1 NAME

tps - turbo-ps

=head1 SYNOPSIS

 tps [-n] [-t] [-v] [-k] [-p <ps-options>] <regex> <regex> ...
 tps [-n] [-t] [-v] [-h] [-p <ps-options>] <regex> <regex> ...
 tps [-n] [-t] [-v] [-s <signal>] [-p <ps-options>] <regex> <regex> ...

=head1 DESCRIPTION

tps(1) issues the command "ps -ef" and from the output returned,
displays lines matching any of the <regex>s. The options passed to ps
are controlled by the B<-p> option.

If B<-k> is included on the tps command line, a KILL signal is sent to
the selected processes. If B<-h> is on the command line, a HUP signal
is sent. By using B<-s> <signal>, any arbitrary signal can be sent to
the processes.

If the B<-v> option is used, tps selects lines that do NOT match the
regex, like grep. If multiple regexes are provided, only lines that
match none of them are reported or signaled.

The B<-t> (terse) option suppressed the column header line that
otherwise appears at the top of tps' output.

To see what a set of options and <regex>s will do without actually
sending any signals, include B<-n> on the command line.

=head1 AUTHOR

tps (copyright 2002 Oak Ridge National Laboratory) was written by Tom
Barron (tbarron@ornl.gov).

=head1 SEE ALSO

ps(1)

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

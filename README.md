                            Backscratcher

"Every good work of software starts by scratching a developer's
 personal itch."
  - Eric Raymond

This is a collection of small programs I have developed over the years
to take care of various tasks on the computer. Perhaps the one I use
most is 'tps' (turbo-ps), which lets me grep the output of ps with
strings rather than pids.

Another one I use a lot is fx (effects). It can do a number of tricks
to issue a command on each of a collection of files, even commands
that ordinarily only operate on a single file.


    align.py
        Read a sequence of text lines and align their contents into
        columns.

    ascii.py
        Display the ASCII collating sequence.

    calc.py
        Simple calculator/expression evaluator.

    chron.py
        Timer. Can count up (like a stopwatch) or down (like a kitchen
        timer).

    clps.py
        Command Line Password Safe. Stores (host, user, password)
        tuples in an encrypted file, can copy a password to the
        clipboard for pasting into a password prompt without
        displaying it on the screen. Mac-specific, since it uses
        pbcopy and pbpaste.

    dt.py
        Easy date arithmetic.

    errno
        Feed it a number from errno.h, get back the symbolic name and
        meaning.

    fab.py
        Poor man's make.

    filter.py
    
    fl.py
        File manipulation.

    fx.py
        Command line effects.

    hd.py
        Hexdump.

    list.py (list.pl)
        Set arithmetic applied to lists generated by Unix commands.
    
    mag.py (magnitude)
        2384192384283 -> 2.17 Tb

    msh
        Start ssh with a control socket so that multiple sessions can
        piggyback over the same connection without repeated
        authentication.

    odx.py (odx.pl)
        Report the octal, decimal, and hexadecimal variants of a
        number.

    plwhich
        Which for the perl installation. Where does Data::Dumper live?

    ptidy
        Cleanup up emacs debris.

    pytool.py
        Generate python templates.

    replay.py (replay.pl)
        Run a command over and over and watch its output.

    rxlab
        Play with regular expressions.

    scanpath
        Where in my $PATH is foo?

    summarize.pl
        Apply "artificial ignorance" to a set of files.

    testhelp.py
        Testing utility routines.

    toolframe.py
        Easy launching for tool-style and simply python programs.

    tpbtools.py
        Utility routines.

    tps
        Find processes.

    truth_table
        Generate truth tables for an arbitrary number of variables.

    vipath
        Edit $PATH.

    wcal
        Wide cal. Three months side by side.

    workrpt.py
        Read my work log and generate a report.

    wxfr
        Bulk file transfer.

 
You may notice that some of these are written in only perl while
others have a python version and some are only in python. I learned
perl first and used it alongside the tcl-based expect tool until I
discovered python and realized that it provides pretty much everything
perl and expect do in a single tool. I'm not a performance wonk, I
just want to get the job done, so I didn't worry too much about
whether python is as fast or efficient as perl. I just jumped in.

So now I'm in the middle of converting all these programs to python.

Even more recently, I have started using Perl::Expect. So now I know
that perl can do expect-type stuff, too.

----------------------------

Moving tests down into directory test
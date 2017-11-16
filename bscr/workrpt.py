#!/usr/bin/python
"""
workrpt - report work times

 usage: workrpt   [-D/--doc]
                  [-v/--verbose]
                  [-f/--file input-file-name]
                  [-m/--match regexp]
                  [-w/--week f|c|M|T|W|t|F|S|s]
                  [-d/--day]
                  [-l/--last]
                  [-s/--start YYYY-MM-DD]
                  [-e/--end YYYY-MM-DD]
                  [-p/--pkg filename]
                  [-c/--copy dir]

    -D/--doc       displays this message
    -v/--verbose   output debugging info
    -f/--file      <input-file-name> is the name of the file to read
                     time information from
    -m/--match     report entries that match regexp
    -w/--week      reports a week beginning on
           f         last Thursday - HPSS rotation
           c         last Friday - CCS rotation
           M         last Monday
           T         last Tuesday
           W         last Wednesday
           t         last Thursday
           F         last Friday
           s         last Saturday
           S         last Sunday
    -d/--day       report for date <YYYY-MM-DD>
    -s/-start      report for week beginning <YYYY-MM-DD> or until end date
    -e/--end       report for week ending <YYYY-MM-DD> or from start date
    -p/--pkg       tarball this code to <filename>
    -c/--copy      copy this code to <dir>
"""
import os
import pdb
import re
import shutil
import StringIO
import sys
import time

from bscr import util as U

BSCR = U.package_module(__name__)


# ---------------------------------------------------------------------------
def main(argv=None):
    """
    Command line entry point (CLEP)
    """
    if argv is None:
        argv = sys.argv

    (opts, _) = make_option_parser(argv)
    if opts.debug:
        pdb.set_trace()

    if opts.help:
        wr_help()

    verbose(opts.verbose, True)
    if verbose():
        dump_options(opts)

    if opts.tarball != '' and opts.copy != '':
        raise BSCR.Error('--pkg and --copy are not compatible')
    elif opts.tarball != '' and opts.copy == '':
        package(sys.argv[0], opts.tarball)
    elif opts.tarball == '' and opts.copy != '':
        copy_me(sys.argv[0], opts.copy)

    try:
        (opts.start, opts.end) = interpret_options(opts)
    except Exception, e:
        print str(e)
        sys.exit(1)

    if opts.match_regexp:
        print write_report_regexp(opts)
    else:
        print write_report(opts)


# ---------------------------------------------------------------------------
def copy_me(source, dest):
    """
    Copy a file. This should probably be replaced with something from shutil.
    !@!DEPRECATE
    !@!untested
    """
    if not os.path.isdir(dest):
        dest = os.path.dirname(dest)
    stem = re.sub(r'\.pyc*', '', source)
    for src in [stem, stem + '.py']:
        print("{0} -> {1}".format(src, dest))
        shutil.copy(src, dest)
    sys.exit(0)


# ---------------------------------------------------------------------------
def day_offset(weektype):
    """
    Return the appropriate day number based on <weektype>.
    """
    offset = {'f': 3, 'c': 4, 'M': 0, 'T': 1, 'W': 2,
              't': 3, 'F': 4, 's': 5, 'S': 6, '': 3}
    return offset[weektype]


# ---------------------------------------------------------------------------
def default_input_filename():
    """
    Defines the default input file
    """
    rval = U.pj(os.getenv('HOME'),
                "Dropbox",
                "journal",
                time.strftime("%Y"),
                "WORKLOG")
    return rval


# ---------------------------------------------------------------------------
def dst(mark=0):
    """
    Daylight Saving Time? True or False. With no *mark* (i.e., mark of 0),
    return current status. Otherwise return status of epoch time *mark*.
    !@! untested
    """
    when = mark or time.time()
    tml = time.localtime(when)
    return tml[8]


# ---------------------------------------------------------------------------
def dst_adjusted_time():
    """
    DST adjustment
    """
    now = time.localtime()
    rval = time.time()
    if now[8] == 0:
        rval = rval - 3600
    return rval


# ---------------------------------------------------------------------------
def dump_struct(coll):
    """
    This routine is called when the verbose flag is used, to help with
    debugging
    """
    klist = coll.keys()
    klist.sort()
    for k in klist:
        jlist = coll[k].keys()
        jlist.sort()
        for j in jlist:
            print('%s/%s     %f' % (k, j, coll[k][j]))


# ---------------------------------------------------------------------------
def dump_options(opts):
    """
    Called to help with debugging when the verbose options is True
    """
    ignore_list = ['ensure_value', 'read_file', 'read_module']
    for item in dir(opts):
        if item not in ignore_list and not item.startswith('_'):
            print('dump_options: %s = %s' % (item, getattr(opts, item)))


# ---------------------------------------------------------------------------
def format_report(start, end, coll, testing=False):
    """
    Put the report together
    """
    if verbose():
        dump_struct(coll)
    rval = '%s - %s ' % (start, end) + '-' * 44 + '\n'
    gtotal = gtotal_fph = 0
    try:
        del coll['COB']
    except KeyError:
        pass
    klist = coll.keys()
    klist.sort()
    skip = ''
    try:
        for key in klist:
            if 'total' not in coll[key]:
                coll[key]['total'] = 0
            if ':' in key:
                if 47 < len(key.strip()):
                    dkey = key.strip()[0:44] + '...'
                else:
                    dkey = key.strip()
                rval = rval + '%s%-47s %8s\n' % ('   ',
                                                 dkey,
                                                 hms(coll[key]['length']))
                coll[key]['total'] += coll[key]['length']
            else:
                if verbose():
                    print "key = '%s'" % key
                    print "total = %d" % coll[key]['total']
                rval = rval + '%s%-30s %35s (%s)\n' % (skip,
                                                       key,
                                                       hms(coll[key]['total']),
                                                       fph(coll[key]['total']))
                skip = '\n'
            if ':' not in key:
                try:
                    incr = coll[key]['total']
                except KeyError as err:
                    timeclose(coll, key, time.time())
                    incr = coll[key]['total']
                gtotal += incr
                gtotal_fph += float(fph(incr))

    except KeyError as err:
        rval = rval + "%s on top level key '%s'\n" % (str(err), key)

    rval = rval + '\n%-30s %35s (%s)\n' % ('Total:', hms(gtotal),
                                           str(gtotal_fph))
    if testing:
        print rval

    return rval


# ---------------------------------------------------------------------------
def wr_help():
    """
    Display a usage message based on the module docstring
    """
    print __doc__
    sys.exit()


# ---------------------------------------------------------------------------
def hms(seconds):
    """
    Convert seconds to HH:MM:SS
    """
    minutes = int(seconds/60)
    seconds = seconds - 60 * minutes

    hours = int(minutes/60)
    minutes = minutes - 60 * hours

    return '%02d:%02d:%02d' % (hours, minutes, seconds)


# ---------------------------------------------------------------------------
def fph(seconds):
    """
    Convert seconds to hours
    """
    hours = float(seconds)/3600.0

    return '%3.1f' % (hours)


# ---------------------------------------------------------------------------
def intify(arg):
    """
    Turn everything in the list into an int
    """
    if isinstance(arg, list):
        rval = [int(item) for item in arg]
    else:
        rval = int(arg)
    return rval


# ---------------------------------------------------------------------------
def interpret_options(opts):
    """
    Parse the program options and set things up for the rest of the program.
    """
    if opts.lastweek and ((opts.start_ymd != '') or (opts.end_ymd != '')):
        raise BSCR.Error('--last and --start or --end are not compatible')
    elif (opts.weektype != '') and ((opts.start_ymd != '')
                                    or (opts.end_ymd != '')):
        raise BSCR.Error('--week and --start or --end are not compatible')
    elif (opts.since != '') and (opts.start_ymd != ''):
        raise BSCR.Error('--since and --start are not compatible')
    elif (re.search('^[fcMTWtFsS]$', opts.weektype)
          and (opts.start_ymd == '')
          and (opts.end_ymd == '')):
        if opts.lastweek:
            (start, end) = week_starting_last(day_offset(opts.weektype),
                                              -7 * 24 * 3600)
        else:
            (start, end) = week_starting_last(day_offset(opts.weektype), 0)

    elif (opts.start_ymd == '') and (opts.end_ymd != ''):
        (start, end) = week_ending(opts.end_ymd)
    elif (opts.start_ymd != '') and (opts.end_ymd == ''):
        (start, end) = week_starting(opts.start_ymd)
    elif (opts.start_ymd != '') and (opts.end_ymd != ''):
        start = opts.start_ymd
        end = opts.end_ymd
    elif (opts.since != ''):
        start = opts.since
        end = time.strftime("%Y.%m%d", time.localtime())
    else:
        (start, _) = week_starting_last(day_offset('M'), 0)
        end = time.strftime("%Y.%m%d", time.localtime())

    return (start, end)


# ---------------------------------------------------------------------------
def make_option_parser(argv):
    """
    Build a parser to understand the command line options.
    """
    c = U.cmdline([{'opts': ['-c', '--copy'],
                    'action': 'store',
                    'type': 'string',
                    'dest': 'copy',
                    'default': '',
                    'help': 'copy this code to <dir>',
                    },
                   {'opts': ['-d', '--day'],
                    'action': 'store_true',
                    'dest': 'dayflag',
                    'default': False,
                    'help': 'report each day separately',
                    },
                   {'opts': ['-e', '--end'],
                    'action': 'store',
                    'type': 'string',
                    'dest': 'end_ymd',
                    'default': '',
                    'help': 'end date for report YYYY.MMDD',
                    },
                   {'opts': ['-f', '--file'],
                    'action': 'store',
                    'type': 'string',
                    'dest': 'filename',
                    'default': default_input_filename(),
                    'help': 'timelog to read',
                    },
                   {'opts': ['-g', '--debug'],
                    'action': 'store_true',
                    'dest': 'debug',
                    'default': False,
                    'help': 'run the debugger',
                    },
                   {'opts': ['-l', '--last'],
                    'action': 'store_true',
                    # 'type': 'string',
                    'dest': 'lastweek',
                    'default': False,
                    'help': 'report the last week',
                    },
                   {'opts': ['-m', '--match'],
                    'action': 'store',
                    'type': 'string',
                    'dest': 'match_regexp',
                    'default': '',
                    'help': 'regexp to match',
                    },
                   {'opts': ['-s', '--start'],
                    'action': 'store',
                    'type': 'string',
                    'dest': 'start_ymd',
                    'default': '',
                    'help': 'start date for report YYYY.MMDD',
                    },
                   {'opts': ['-S', '--since'],
                    'action': 'store',
                    'dest': 'since',
                    'type': 'string',
                    'default': '',
                    'help': 'report date YYYY.MMDD through end of file',
                    },
                   {'opts': ['-w', '--week'],
                    'action': 'store',
                    'dest': 'weektype',
                    'type': 'string',
                    'default': '',
                    'help': 'one of [fcMTWtFsS]',
                    },
                   {'opts': ['-D', '--doc'],
                    'action': 'store_true',
                    'dest': 'help',
                    'default': False,
                    'help': 'show script documentation',
                    },
                   {'opts': ['-p', '--pkg'],
                    'action': 'store',
                    'type': 'string',
                    'dest': 'tarball',
                    'default': '',
                    'help': 'package this code to <filename>',
                    },
                   {'opts': ['-v', '--verbose'],
                    'action': 'store_true',
                    'dest': 'verbose',
                    'default': False,
                    'help': 'display debugging info',
                    },
                   ])
    (o, a) = c.parse(argv)
    return(o, a)


# ---------------------------------------------------------------------------
# def maketime(tm=[]):
#     """
#     With no *tm* (i.e., == []), return the current epoch time (time.time()).
#     With *mark*, use it as an arg to time.mktime() in a way that gives an
#     accurate dst result.
#     """
#     if tm:
#         x = list(tm)
#         x[3] = 12
#         x[4] = 0
#         x[5] = 0
#         x[8] = 0
#         z = time.mktime(x)
#         y = time.localtime(z)
#         x[8] = y.tm_isdst
#     return time.mktime(tm)


# ---------------------------------------------------------------------------
def next_tuesday():
    """
    Relative weekday
    """
    now = time.time()
    tml = time.localtime(now)
    delta = (1 + 7 - tml[6]) % 7    # !@!here
    then = now + delta * 24 * 3600
    return time.strftime("%Y.%m%d", time.localtime(then))


# ---------------------------------------------------------------------------
def next_day(ymd, fmt=None):
    """
    Day offset
    """
    if fmt is None:
        fmt = '%Y.%m%d'
    now = time.mktime(time.strptime(ymd, fmt))
    then = now + 24*3600
    return time.strftime(fmt, time.localtime(then))


# ---------------------------------------------------------------------------
def day_plus(offset):
    """
    Compute a day offset
    """
    now = time.time()
    then = now + offset*24*3600
    return then


# ---------------------------------------------------------------------------
def package(source, filename):
    """
    What!? Something about making a tarball? !@!DEPRECATE
    """
    print 'source = ', source
    print 'filename = ', filename
    tdir = os.path.dirname(source)
    flist = ['%s/workrpt' % tdir,
             '%s/workrpt.py' % tdir,
             default_input_filename()]
    cmd = 'tar zcvf %s %s' % (filename, ' '.join(flist))
    print cmd
    os.system(cmd)
    sys.exit(0)


# ---------------------------------------------------------------------------
def parse_timeline(line):
    """
    Break a line down into timestamp and activity. Date can be YYYY-mm-dd or
    YYYY.mmdd.
    """
    rval = None
    lfmt = (r'(\d{4})(-(\d{2})-(\d{2})|.(\d{2})(\d{2})) ' +
            r'(\d{2}):(\d{2}):(\d{2}) (.*)')
    line = re.sub('#.*', '', line)
    mat = re.search(lfmt, line)
    if mat:
        grp = mat.groups()
        if '-' in grp[1]:
            rval = [grp[0], grp[2], grp[3], grp[6], grp[7], grp[8], grp[9]]
        elif '.' in grp[1]:
            rval = [grp[0], grp[4], grp[5], grp[6], grp[7], grp[8], grp[9]]

    return rval


# ---------------------------------------------------------------------------
def parse_ymd(dayname):
    """
    Given a relative day reference or weekday name, compute the nearby
    subsequent ymd date that matches and return it as a list of three elements.
    """
    if dayname == 'yesterday':
        ymd = time.strftime("%Y.%m%d", time.localtime(time.time() - 24*3600))
    elif dayname == 'today':
        ymd = time.strftime("%Y.%m%d", time.localtime(time.time()))
    elif dayname == 'tomorrow':
        ymd = time.strftime("%Y.%m%d", time.localtime(time.time() + 24*3600))
    elif re.search(r'(mon|tues|wednes|thurs|fri|satur|sun)day', dayname):
        tml = time.localtime(time.time())
        wday = tml[6]
        wdn = weekday_num(dayname)
        delta = ((-6 - wday + wdn) % - 7) - 1   # !@!here
        # t = time.time() + (24 * 3600 * delta)
        tmark = day_plus(delta)
        ymd = time.strftime("%Y.%m%d", time.localtime(tmark))
    else:
        ymd = dayname

    [rval] = re.findall(r'(\d{2,4})[-.](\d{2})[-.]?(\d{2})', ymd)
    return list(rval)


# ---------------------------------------------------------------------------
def stringify(seq):
    """
    !@!DEPRECATED -- apparently unused
    """
    rval = []
    for item in seq:
        rval.append('%02d' % item)
    return rval


# ---------------------------------------------------------------------------
def tally(coll, start, end, t_tup):
    """
    Set the start time for an interval.
    """
    if t_tup is None or 7 != len(t_tup):
        return
    if not hasattr(tally, 'last'):
        tally.last = ''

    [year, mon, mday, hour, mint, sec, t_item] = t_tup
    date = '%s.%s%s' % (year, mon, mday)
    if (date < start) or (end < date):
        return

    when = time.mktime(intify([year, mon, mday, hour, mint, sec, 0, 0, dst()]))
    try:
        if tally.last != '':
            timeclose(coll, tally.last, when)
        coll[t_item]['start'] = when
    except KeyError:
        coll[t_item] = {}
        coll[t_item]['start'] = when

    tally.last = t_item
    return tally.last


# ---------------------------------------------------------------------------
def timeclose(coll, last, when, every=False):
    """
    Close a time interval, adding end - start to length. Delete 'start' and
    'end' members of the interval. If 'every' is True, scan the whole structure
    for time intervals needing closeout.
    """
    if every:
        klist = coll.keys()
        for key in klist:
            cat = category(key)
            if cat != key or ':' not in key:
                reset_category_total(coll, cat)

        if last != 'COB' and last is not None:
            coll[last]['end'] = when
            lapse = when - coll[last]['start']
            try:
                coll[last]['length'] = coll[last]['length'] + lapse
            except KeyError:
                coll[last]['length'] = lapse

        for key in klist:
            cat = category(key)
            if (cat != key or ':' not in key) and key != 'COB':
                try:
                    increment_category_total(coll, cat, coll[key]['length'])
                except KeyError, err:
                    print("timeclose: No %s member for key %s" %
                          (str(err), key))
                    raise

    elif last and last != 'COB':
        coll[last]['end'] = when
        lapse = when - coll[last]['start']
        try:
            coll[last]['length'] = coll[last]['length'] + lapse
        except KeyError:
            coll[last]['length'] = lapse
        del coll[last]['start']
        del coll[last]['end']


# ---------------------------------------------------------------------------
def reset_category_total(coll, cat):
    """
    Start over
    """
    if cat != '':
        try:
            coll[cat]['total'] = 0
        except KeyError:
            pass


# ---------------------------------------------------------------------------
def increment_category_total(coll, cat, lapse):
    """
    Accumulate some time
    """
    if cat != '':
        try:
            coll[cat]['total'] = coll[cat]['total'] + lapse
        except KeyError:
            coll[cat] = {}
            coll[cat]['total'] = lapse


# ---------------------------------------------------------------------------
def category(task):
    """
    Parse the task category from the task description.

    A task description looks like 'admin: liason'. The category for this
    task would be 'admin'. If the task description does not contain a colon,
    the category is the whole description. Eg., 'vacation' -> 'vacation'.
    """
    cat = ''
    try:
        [cat] = re.findall(r'([^:]+):?.*', task)
    except ValueError:
        cat = task

    if verbose():
        pass

    return cat


# ---------------------------------------------------------------------------
def verbose(value=None, update=False):
    """
    Control program verbosity.

    Set the global flag to <value> if <set> is true. Return the
    current flag value. Both arguments are optional so the current
    flag can be checked by calling verbose() with no arguments.
    """
    try:
        rval = verbose.verbosity
    except AttributeError:
        rval = verbose.verbosity = False
    if update:
        rval = verbose.verbosity = value
    return rval


# ---------------------------------------------------------------------------
def week_diff(start, fin):
    """
    Compute the number of days required to get from weekday *start* to weekday
    *fin*
    """
    rval = -1 * (((start + 6 - fin) % 7) + 1)
    return rval


# ---------------------------------------------------------------------------
def week_starting_last(weekday, offset, now=time.time()):
    """
    Return start and end dates for week beginning on most recent <weekday>.

    Return values are in %Y.%m%d format.

    <weekday> is in range(0:6), indicating Monday through Sunday.
    <offset> is a number of seconds to shift the result. Typically
    <offset> will be a number of days given as N * 24 * 3600.
    """
    tml = time.localtime(now)
    delta = (tml.tm_wday + 7 - weekday) % 7    # !@!here
    then = now - delta * 24 * 3600
    then = then + offset

    start = time.strftime("%Y.%m%d", time.localtime(then))
    end_time = then + 6 * 24 * 3600
    end = time.strftime("%Y.%m%d", time.localtime(end_time))
    return(start, end)


# ---------------------------------------------------------------------------
def week_starting(ymd):
    """
    Return start and end %Y.%m%d dates for the week starting on <ymd>.

    <ymd> is one of 'yesterday', 'today', 'tomorrow', 'monday', 'tuesday', etc.

    We set the start time four hours into the first day of the week so we don't
    have issues from being too close to midnight (eg, due to DST changing
    between the beginning and end of the week, etc.)
    """
    (year, mon, mday) = parse_ymd(ymd)
    start_time = time.mktime([int(year), int(mon), int(mday),
                              4, 0, 0, 0, 0, 0])
    end_time = start_time + 6 * 24 * 3600
    start = time.strftime('%Y.%m%d', time.localtime(start_time))
    end = time.strftime('%Y.%m%d', time.localtime(end_time))
    return(start, end)


# ---------------------------------------------------------------------------
def week_ending(ymd):
    """
    Return start and end %Y.%m%d dates for the week ending on <ymd>.

    <ymd> is one of 'yesterday', 'today', 'tomorrow', 'monday', 'tuesday', etc.

    We set the start time four hours into the first day of the week so we don't
    have issues from being too close to midnight (eg, due to DST changing
    between the beginning and end of the week, etc.)
    """
    (year, mon, mday) = parse_ymd(ymd)
    end_time = time.mktime([int(year), int(mon), int(mday),
                            4, 0, 0, 0, 0, 0])
    start_time = end_time - (6 * 24 * 3600)
    start = time.strftime('%Y.%m%d', time.localtime(start_time))
    end = time.strftime('%Y.%m%d', time.localtime(end_time))
    return(start, end)


# ---------------------------------------------------------------------------
def weekday_num(name):
    """
    Return the number of weekday <name>.
    """
    wday_d = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
              'friday': 4, 'saturday': 5, 'sunday': 6}
    return wday_d[name]


# ---------------------------------------------------------------------------
def process_line(coll, low, high, line):
    """
    Handle one line
    """
    last = tally(coll, low, high, parse_timeline(line))
    if last:
        try:
            if line < process_line.lastline:
                sys.exit('Dates or times out of order')
            else:
                process_line.lastline = line
        except AttributeError:
            process_line.lastline = line
    return last


# -----------------------------------------------------------------------------
def parse_epoch_task(line):
    """
    Parse a line into epoch time and task. Routine parse_timeline() returns
    None for a comment line or other line that doesn't match the timestamp,
    task format. Otherwise, it returns (year, month, day, hour, minute,
    second).
    """
    tup = parse_timeline()
    if tup is not None:
        #         (year, mon, day, hour, mnt, sec, payld) = tup
        #         when = int(time.mktime(intify([year, mon, day,
        #                                        hour, mnt, sec,
        #                                        0, 0, dst()])))
        when = int(time.mktime(intify(tup[0:-1] + (0, 0, dst()))))
        tup = (when, tup[-1])
    return tup


# -----------------------------------------------------------------------------
def begin(data, task, when):
    """

    """
    if task != 'COB':
        try:
            data[task]['start'] = when
        except KeyError:
            data[task] = {'start': when, 'length': 0}


# -----------------------------------------------------------------------------
def complete(data, prev, now):
    """
    In dict *data*, complete the time segment represented by *prev* at time
    index *now*
    """
    task = prev['task']
    if task != 'COB':
        data[task]['length'] += now - data[task]['start']
        data[task]['start'] = None


# -----------------------------------------------------------------------------
def ymd_epoch(ymd, end=False):
    """
    Given a date in %Y.%m%d format, return the corresponding epoch time.

    If *end* is False, return the beginning of the day. Otherwise, return the
    end of the day.
    """
    if end:
        when = '{0} 23:59:59'.format(ymd)
    else:
        when = '{0} 00:00:00'.format(ymd)
    return time.mktime(time.strptime(when, '%Y.%m%d %H:%M:%S'))


# -----------------------------------------------------------------------------
def filter_data_temporal(opts):
    """
    Select the data to be formatted from *opts*.filename based on *opts*.start,
    *opts*.end, and *opts*.match_regexp
    """
    cstart = ymd_epoch(opts.start)
    cend = ymd_epoch(next_day(opts.end))
    rval = []
    lastwhen = 0
    with open(opts.filename, 'r') as rbl:
        for line in rbl:
            tup = parse_epoch_task(line)
            if tup is None:
                continue
            (lwhen, ltask) = tup
            if lwhen < cstart:
                continue
            if cend < lwhen:
                continue
            rval.append(line)

            if lwhen < lastwhen:
                sys.exit("'{}' precedes '{}'")

            lastwhen = lwhen
            lline = line

    complete(rval, lline, time.time())


# -----------------------------------------------------------------------------
def filter_data_regexp(opts, data):
    """
    Select the data to be formatted from *opts*.filename based on *opts*.start,
    *opts*.end, and *opts*.match_regexp
    """
    rval = {}
    lline = {}
    for idx, line in enumerate(data):
        tup = parse_epoch_task(line)
        if tup is None:
            continue
        (lwhen, ltask) = tup
        if [] == re.findall(opts.match_regexp, ltask):
            data[idx] = "{} {}".format(ymdhms(lwhen), "COB")
        else:
            complete(rval, lline, lwhen)
            begin(rval, ltask, lwhen)

        lline['when'] = lwhen
        lline['task'] = ltask
        lline['text'] = line

    complete(rval, lline, time.time())


# -----------------------------------------------------------------------------
def format_report_x(data):
    """
    Format *data* into a report
    """
    pass


# -----------------------------------------------------------------------------
def sum_data(data):
    """
    Compute subtotals and total for *data*
    """
    pass


# -----------------------------------------------------------------------------
def generate_report(opts):
    """
    Generate a time report from *opts*.filename base on *opts*.match_regexp,
    *opts*.start, and *opts*.end
    """
    datl = filter_data_temporal(opts)
    datl = filter_data_regexp(opts, datl)
    datd = sum_data(datl)
    rval = format_report_x(datd)
    return rval


# -----------------------------------------------------------------------------
def write_report_regexp(opts, testing=False):
    """
    Generate a time report from <filename> based on <o.match_regexp>
    """
    filename = opts.filename
    start = ymd_epoch(opts.start)
    end = ymd_epoch(opts.end, end=True)
    dayflag = opts.dayflag
    if verbose():
        print "write_report: filename = '%s'" % filename
        print "write_report: start = '%s'" % start
        print "write_report: end = '%s'" % end
        print "write_report: dayflag = %s" % dayflag

    dat = {}
    rval = StringIO.StringIO()
    last = None
    with open(opts.filename, 'r') as rbl:
        for line in rbl:
            if not line[0:4].isdigit():
                continue

            (year, mon, day, hour, mnt, sec, payld) = parse_timeline(line)
            when = int(time.mktime(intify([year, mon, day,
                                           hour, mnt, sec,
                                           0, 0, dst()])))
            if when < start or end < when:
                continue

            if last:
                dat[last]['sum'] += when - dat[last]['start']
                dat[last]['start'] = 0
                last = None

            if re.findall(opts.match_regexp, payld):
                try:
                    dat[payld]['start'] = when
                except KeyError:
                    dat[payld] = {}
                    dat[payld]['start'] = when
                    dat[payld]['sum'] = 0
                last = payld

    for key in dat:
        if dat[key]['start'] != 0:
            dat[key]['sum'] += int(time.time()) - dat[key]['start']

    total = total_fph = 0
    rval.write("----- matching '{0}' -----\n".format(opts.match_regexp))
    for key in dat:
        duration = dat[key]['sum']
        total += duration
        total_fph += float(fph(duration))
        rval.write("{0:48}   {1} ({2})\n".format(key,
                                                 hms(duration),
                                                 fph(duration)))
    rval.write("\n")
    rval.write("{0:56}  {1} ({2})\n".format("Total:",
                                            hms(total),
                                            total_fph))

    return rval.getvalue()


# ---------------------------------------------------------------------------
def write_report(opts, testing=False):
    """
    Generate a time report from <filename> based on <start> and <end> dates.

    <dayflag> is a boolean indicating whether to write a single report
    for the entire time period between <start> and <end> or whether to
    write a mini-report for each day in the time period.
    """
    filename = opts.filename
    start = opts.start
    end = opts.end
    dayflag = opts.dayflag
    if verbose():
        print "write_report: filename = '%s'" % filename
        print "write_report: start = '%s'" % start
        print "write_report: end = '%s'" % end
        print "write_report: dayflag = %s" % dayflag

    rval = ''
    last = None
    if dayflag:
        day = start
        while day <= end:
            coll = {}
            rbl = open(filename, 'r')
            for line in rbl:
                last = process_line(coll, day, day, line)
            rbl.close()
            if last is not None and last in coll.keys():
                timeclose(coll, last, time.time(), True)
            rval = rval + format_report(day, day, coll, testing)
            day = next_day(day)
    else:
        coll = {}
        rbl = open(filename, 'r')
        for line in rbl:
            last = process_line(coll, start, end, line)
        rbl.close()
        if verbose():
            dump_struct(coll)
        timeclose(coll, last, time.time(), True)
        rval = format_report(start, end, coll, testing)
    return rval


# ---------------------------------------------------------------------------
def ymdhms(epoch):
    """
    Convert epoch time to %Y.%m%d %H:%M:%S and return it
    """
    return time.strftime("%Y.%m%d %H:%M:%S", time.localtime(epoch))

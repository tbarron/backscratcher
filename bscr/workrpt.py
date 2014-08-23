#!/usr/bin/python
'''
workrpt - report work times

 usage: workrpt   [-D/--doc]
                  [-v/--verbose]
                  [-f/--file input-file-name]
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
'''

import getopt
import optparse
import os
import pdb
import re
import sys
import time
import toolframe
import unittest
from bscr import util as U


# ---------------------------------------------------------------------------
def main(argv=None):
    """
    Command line entry point (CLEP)
    """
    if argv is None:
        argv = sys.argv

    (o, a) = makeOptionParser(argv)
    if o.debug:
        pdb.set_trace()

    if o.help:
        help()

    verbose(o.verbose, True)
    if verbose():
        dump_options(o)

    if o.tarball != '' and o.copy != '':
        raise Exception('--pkg and --copy are not compatible')
    elif o.tarball != '' and o.copy == '':
        package(sys.argv[0], o.tarball)
    elif o.tarball == '' and o.copy != '':
        copy_me(sys.argv[0], o.copy)

    try:
        (start, end) = interpret_options(o)
    except Exception, e:
        print str(e)
        sys.exit(1)

    write_report(o.filename, start, end, o.dayflag)


# ---------------------------------------------------------------------------
def copy_me(source, dest):
    """
    Copy a file. This should probably be replaced with something from shutil.
    !@!DEPRECATE
    """
    dir = os.path.dirname(source)
    flist = ['%s/workrpt' % dir, '%s/workrpt.py' % dir]
    for f in flist:
        cmd = "cp %s %s" % (f, dest)
        print cmd
        os.system(cmd)
    sys.exit(0)


# ---------------------------------------------------------------------------
def day_offset(weektype):
    '''
    Return the appropriate day number based on <weektype>.
    '''
    offset = {'f': 3, 'c': 4, 'M': 0, 'T': 1, 'W': 2,
              't': 3, 'F': 4, 's': 5, 'S': 6, '': 3}
    return offset[weektype]


# ---------------------------------------------------------------------------
def default_input_filename():
    """
    Defines the default input file
    """
    # rval = "%s/diary/journal/work/%s/WORKLOG" \
    #        % (os.getenv('HOME'), time.strftime('%Y', time.localtime()))
    # rval = time.strftime('/Volumes/ZAPHOD/journal/%Y/WORKLOG',
    #                      time.localtime())
    rval = U.pj(os.getenv('HOME'),
                "Dropbox",
                "journal",
                time.strftime("%Y"),
                "WORKLOG")
    return rval


# ---------------------------------------------------------------------------
def dst():
    """
    Daylight Saving Time? True or False
    """
    now = time.localtime(time.time())
    return now[8]


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
def dump_struct(C):
    """
    Dump the structure (duh!). Where/why is this used?
    """
    klist = C.keys()
    klist.sort()
    for k in klist:
        jlist = C[k].keys()
        jlist.sort()
        for j in jlist:
            print('%s/%s     %f' % (k, j, C[k][j]))


# ---------------------------------------------------------------------------
def dump_options(o):
    """
    Where/why is this used?
    """
    ignore_list = ['ensure_value', 'read_file', 'read_module']
    for item in dir(o):
        if item not in ignore_list and not item.startswith('_'):
            print('dump_options: %s = %s' % (item, getattr(o, item)))


# ---------------------------------------------------------------------------
def format_report(start, end, C, testing=False):
    """
    Put the report together
    """
    if verbose():
        dump_struct(C)
    rval = '%s - %s ' % (start, end) + '-' * 44 + '\n'
    gtotal = 0
    try:
        del C['COB']
    except:
        pass
    klist = C.keys()
    klist.sort()
    skip = ''
    try:
        for key in klist:
            if ':' in key:
                if 47 < len(key.strip()):
                    dkey = key.strip()[0:44] + '...'
                else:
                    dkey = key.strip()
                rval = rval + '%s%-47s %8s\n' % ('   ',
                                                 dkey,
                                                 hms(C[key]['length']))
            else:
                if verbose():
                    print "key = '%s'" % key
                    print "total = %d" % C[key]['total']
                rval = rval + '%s%-30s %35s (%s)\n' % (skip,
                                                       key,
                                                       hms(C[key]['total']),
                                                       fph(C[key]['total']))
                skip = '\n'
                try:
                    gtotal = gtotal + C[key]['total']
                except KeyError, e:
                    timeclose(C, key, time.time())
                    gtotal = gtotal + C[key]['total']

    except KeyError, e:
        rval = rval + "%s on top level key '%s'\n" % (str(e), key)

    rval = rval + '\n%-30s %35s (%s)\n' % ('Total:', hms(gtotal), fph(gtotal))
    if not testing:
        print rval

    return rval


# ---------------------------------------------------------------------------
def help():
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
def intify(list):
    """
    Turn everything in the list into an int
    """
    rval = [int(item) for item in list]
    return rval


# ---------------------------------------------------------------------------
def interpret_options(o):
    '''
    Parse the program options and set things up for the rest of the program.
    '''
    if o.lastweek and ((o.start_ymd != '') or (o.end_ymd != '')):
        raise StandardError('--last and --start or --end are not compatible')
    elif (o.weektype != '') and ((o.start_ymd != '') or (o.end_ymd != '')):
        raise StandardError('--week and --start or --end are not compatible')
    elif (o.since != '') and (o.start_ymd != ''):
        raise StandardError('--since and --start are not compatible')
    elif (re.search('^[fcMTWtFsS]$', o.weektype)
          and (o.start_ymd == '')
          and (o.end_ymd == '')):
        if o.lastweek:
            (start, end) = week_starting_last(day_offset(o.weektype),
                                              -7 * 24 * 3600)
        else:
            (start, end) = week_starting_last(day_offset(o.weektype), 0)

    elif (o.start_ymd == '') and (o.end_ymd != ''):
        (start, end) = week_ending(o.end_ymd)
    elif (o.start_ymd != '') and (o.end_ymd == ''):
        (start, end) = week_starting(o.start_ymd)
    elif (o.start_ymd != '') and (o.end_ymd != ''):
        start = o.start_ymd
        end = o.end_ymd
        # start = ymd(parse_ymd(o.start_ymd))
        # end = ymd(parse_ymd(o.end_ymd))
    elif (o.since != ''):
        start = o.since
        end = time.strftime("%Y.%m%d", time.localtime())
    else:
        (start, x) = week_starting_last(day_offset('M'), 0)
        end = time.strftime("%Y.%m%d", time.localtime())

    return (start, end)


# ---------------------------------------------------------------------------
# def last_monday():
#     # print 'last_monday:'
#     now = time.time()
#     tm = time.localtime(now)
#     delta = (tm[6] + 7 - 0) % 7     # !@!here
#     # delta = week_diff(tm[6], day_offset('M'))
#     then = now - delta * 24 * 3600
#     return then

# # ---------------------------------------------------------------------------
# def last_wednesday():
#     now = time.time()
#     tm = time.localtime(now)
#     delta = (tm[6] + 7 - 2) % 7   # !@!here
#     then = now - delta * 24 * 3600
#     return then


# ---------------------------------------------------------------------------
def makeOptionParser(argv):
    '''
    Build a parser to understand the command line options.
    '''
    p = optparse.OptionParser()
    p.add_option('-c', '--copy',
                 action='store', type='string', dest='copy', default='',
                 help='copy this code to <dir>')
    p.add_option('-d', '--day',
                 action='store_true', default=False, dest='dayflag',
                 help='report each day separately')
    p.add_option('-e', '--end',
                 action='store', dest='end_ymd', type='string', default='',
                 help='end date for report YYYY.MMDD')
    p.add_option('-f', '--file',
                 action='store', type='string', dest='filename',
                 default=default_input_filename(),
                 help='timelog to read')
    p.add_option('-g', '--debug',
                 action='store_true', dest='debug', default=False,
                 help='run the debugger')
    p.add_option('-l', '--last',
                 action='store_true', default=False, dest='lastweek',
                 help='report the last week')
    p.add_option('-s', '--start',
                 action='store', dest='start_ymd', type='string', default='',
                 help='start date for report YYYY.MMDD')
    p.add_option('-S', '--since',
                 action='store', dest='since', type='string', default='',
                 help='report date YYYY.MMDD through end of file')
    p.add_option('-w', '--week',
                 action='store', dest='weektype', type='string', default='',
                 help='one of [fcMTWtFsS]')
    p.add_option('-D', '--doc',
                 action='store_true', dest='help', default=False,
                 help='show script documentation')
    p.add_option('-p', '--pkg',
                 action='store', type='string', dest='tarball',
                 default='',
                 help='package this code to <filename>')
    p.add_option('-v', '--verbose',
                 action='store_true', dest='verbose', default=False,
                 help='display debugging info')
    (o, a) = p.parse_args(argv)
    return(o, a)


# ---------------------------------------------------------------------------
def next_tuesday():
    """
    Relative weekday
    """
    now = time.time()
    tm = time.localtime(now)
    delta = (1 + 7 - tm[6]) % 7    # !@!here
    then = now + delta * 24 * 3600
    return time.strftime("%Y.%m%d", time.localtime(then))


# ---------------------------------------------------------------------------
def next_day(ymd, format=None):
    """
    Day offset
    """
    if format is None:
        format = '%Y.%m%d'
    now = time.mktime(time.strptime(ymd, format))
    then = now + 24*3600
    return time.strftime(format, time.localtime(then))


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
    dir = os.path.dirname(source)
    flist = ['%s/workrpt' % dir,
             '%s/workrpt.py' % dir,
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
    m = re.search(lfmt, line)
    if m:
        x = m.groups()
        if '-' in x[1]:
            rval = [x[0], x[2], x[3], x[6], x[7], x[8], x[9]]
        elif '.' in x[1]:
            rval = [x[0], x[4], x[5], x[6], x[7], x[8], x[9]]

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
        dt = time.localtime(time.time())
        wd = dt[6]
        t = weekday_num(dayname)
        delta = ((-6 - wd + t) % - 7) - 1   # !@!here
        # t = time.time() + (24 * 3600 * delta)
        t = day_plus(delta)
        ymd = time.strftime("%Y.%m%d", time.localtime(t))
    else:
        ymd = dayname

    [rval] = re.findall(r'(\d{2,4})[-.](\d{2})[-.]?(\d{2})', ymd)
    xrval = []
    for q in rval:
        xrval.append(q)
    # print 'parse_ymd: returning', xrval
    return xrval


# ---------------------------------------------------------------------------
def stringify(list):
    """
    !@!DEPRECATED -- apparently unused
    """
    rval = []
    for item in list:
        rval.append('%02d' % item)
    return rval


# ---------------------------------------------------------------------------
def tally(C, start, end, Q):
    """
    Set the start time for an interval.
    """
    global last

    # print "tally: ----------------------------------------"
    # print "tally: ", Q

    if Q is None or 7 != len(Q):
        last = ''
        return

    [y, m, d, H, M, S, T] = Q
    date = '%s.%s%s' % (y, m, d)
    if (date < start) or (end < date):
        return

    # print 'tally: %s <?> %s <?> %s' % (start, date, end)
    # when = time.mktime(S, M, H, d, m-1, y-1900, 0, 0, dst())
    when = time.mktime(intify([y, m, d, H, M, S, 0, 0, dst()]))
    # print 'tally: when = %d' % when
    try:
        C[T]['start'] = when
    except KeyError:
        C[T] = {}
        C[T]['start'] = when

    try:
        if last != '':
            timeclose(C, last, when)
    except NameError:
        pass

    last = T
    return last


# ---------------------------------------------------------------------------
def timeclose(C, last, when, all=False):
    """
    Close a time interval, adding end - start to length. Delete
    'start' and 'end' members of the interval. If 'all' is True, scan
    the whole structure for time intervals needing closeout.
    """
    if all:
        klist = C.keys()
        for key in klist:
            cat = category(key)
            if cat != key or ':' not in key:
                reset_category_total(C, cat)

        if last != 'COB' and last is not None:
            C[last]['end'] = when
            lapse = when - C[last]['start']
            try:
                C[last]['length'] = C[last]['length'] + lapse
            except KeyError:
                C[last]['length'] = lapse

        for key in klist:
            cat = category(key)
            if (cat != key or ':' not in key) and key != 'COB':
                try:
                    increment_category_total(C, cat, C[key]['length'])
                except KeyError, e:
                    print("timeclose: No %s member for key %s" % (str(e), key))
                    raise

    else:
        C[last]['end'] = when
        lapse = when - C[last]['start']
        try:
            C[last]['length'] = C[last]['length'] + lapse
        except KeyError:
            C[last]['length'] = lapse
        del C[last]['start']
        del C[last]['end']

        # cat = category(last)
        # increment_category_total(C, cat, lapse)

    # return lapse


# ---------------------------------------------------------------------------
def reset_category_total(C, cat):
    """
    Start over
    """
    if cat != '':
        try:
            C[cat]['total'] = 0
        except KeyError:
            pass


# ---------------------------------------------------------------------------
def increment_category_total(C, cat, lapse):
    """
    Accumulate some time
    """
    if cat != '':
        try:
            C[cat]['total'] = C[cat]['total'] + lapse
        except KeyError:
            C[cat] = {}
            C[cat]['total'] = lapse


# ---------------------------------------------------------------------------
def category(task):
    '''
    Parse the task category from the task description.

    A task description looks like 'admin: liason'. The category for this
    task would be 'admin'. If the task description does not contain a colon,
    the category is the whole description. Eg., 'vacation' -> 'vacation'.
    '''
    cat = ''
    try:
        [cat] = re.findall(r'([^:]+):?.*', task)
    except ValueError:
        cat = task

    if verbose():
        # print 'category: catgory(%s) -> %s' % (task, cat)
        pass

    return cat


# ---------------------------------------------------------------------------
def verbose(value=None, set=False):
    '''
    Control program verbosity.

    Set the global flag to <value> if <set> is true. Return the
    current flag value. Both arguments are optional so the current
    flag can be checked by calling verbose() with no arguments.
    '''
    global verbosity
    if set:
        verbosity = value
    return verbosity


# ---------------------------------------------------------------------------
def week_diff(a, b):
    """
    !@!DERPRECATED -- apparently unused
    """
    # rval = (a + 7 - b) % 7
    rval = -1 * (((a + 6 - b) % 7) + 1)
    return rval


# ---------------------------------------------------------------------------
def week_starting_last(weekday, offset, now=time.time()):
    '''
    Return start and end dates for week beginning on most recent <weekday>.

    Return values are in %Y.%m%d format.

    <weekday> is in range(0:6), indicating Monday through Sunday.
    <offset> is a number of seconds to shift the result. Typically
    <offset> will be a number of days given as N * 24 * 3600.
    '''
    # now = time.time()
    tm = time.localtime(now)
    delta = (tm[6] + 7 - weekday) % 7    # !@!here
    then = now - delta * 24 * 3600
    then = then + offset

    start = time.strftime("%Y.%m%d", time.localtime(then))
    end_time = then + 6 * 24 * 3600
    end = time.strftime("%Y.%m%d", time.localtime(end_time))
    return(start, end)


# ---------------------------------------------------------------------------
def week_starting(ymd):
    '''
    Return start and end %Y.%m%d dates for the week starting on <ymd>.

    <ymd> is one of 'yesterday', 'today', 'tomorrow', 'monday', 'tuesday', etc.
    '''
    (y, m, d) = parse_ymd(ymd)
    start_time = time.mktime([int(y), int(m), int(d), 0, 0, 0, 0, 0, dst()])
    end_time = start_time + 6 * 24 * 3600
    start = time.strftime('%Y.%m%d', time.localtime(start_time))
    end = time.strftime('%Y.%m%d', time.localtime(end_time))
    return(start, end)


# ---------------------------------------------------------------------------
def week_ending(ymd):
    '''
    Return start and end %Y.%m%d dates for the week ending on <ymd>.

    <ymd> is one of 'yesterday', 'today', 'tomorrow', 'monday', 'tuesday', etc.
    '''
    (y, m, d) = parse_ymd(ymd)
    end_time = time.mktime([int(y), int(m), int(d), 0, 0, 0, 0, 0, dst()])
    start_time = end_time - 6 * 24 * 3600
    start = time.strftime('%Y.%m%d', time.localtime(start_time))
    end = time.strftime('%Y.%m%d', time.localtime(end_time))
    return(start, end)


# ---------------------------------------------------------------------------
def weekday_num(name):
    '''
    Return the number of weekday <name>.
    '''
    x = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
         'friday': 4, 'saturday': 5, 'sunday': 6}
    return x[name]


# ---------------------------------------------------------------------------
def write_report(filename, start, end, dayflag, testing=False):
    '''
    Generate a time report from <filename> based on <start> and <end> dates.

    <dayflag> is a boolean indicating whether to write a single report
    for the entire time period between <start> and <end> or whether to
    write a mini-report for each day in the time period.
    '''
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
            C = {}
            f = open(filename, 'r')
            for line in f:
                lastc = tally(C, day, day, parse_timeline(line))
                if lastc is not None:
                    last = lastc
            f.close()
            if last is not None and last in C.keys():
                timeclose(C, last, time.time(), True)
            rval = rval + format_report(day, day, C, testing)
            day = next_day(day)
    else:
        C = {}
        f = open(filename, 'r')
        for line in f:
            lastc = tally(C, start, end, parse_timeline(line))
            if lastc is not None:
                last = lastc
        f.close()
        if verbose():
            dump_struct(C)
        timeclose(C, last, time.time(), True)
        rval = format_report(start, end, C, testing)
    return rval


# ---------------------------------------------------------------------------
toolframe.ez_launch(__name__, main)

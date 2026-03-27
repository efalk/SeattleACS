#!/usr/bin/env python3
# -*- coding: utf8 -*-

import csv
import getopt
import re
import sys
import traceback

# These are used for both reading and writing, so import them
# now. Other plugins only imported on demand. This is especially important
# for the UpdateWwara script which only handles a WWARA imports.
from channel import Channel
from chirp import Chirp
from rtsys import RtSys

# See below for the ics217 subclasses responsible for formatting the
# output.

verbose = 0

def main(reader, usage):
    global verbose
    ifile = sys.stdin

    csvout = csv.writer(sys.stdout)
    writer = Chirp

    start = 1
    recFilter = {}
    try:
        (optlist, args) = getopt.getopt(sys.argv[1:], 'hbm:s:B:NR:lv',
            ['help', 'Chirp', 'RtSys', 'IC-92', 'Icom', 'sparse', 'skip'])
        for flag, value in optlist:
            if flag in ('-h', '--help'):
                print(usage)
                return 0
            elif flag == '-b':
                recFilter['bands'] = None if value == "all" else value
            elif flag == '-m':
                recFilter['modes'] = None if value == "all" else value
            elif flag == '-N':
                recFilter['newEntries'] = True
            elif flag == '-R':
                recFilter['regex'] = re.compile(value)
            elif flag == '-B':
                recFilter['banks'] = value
            elif flag == '--skip':
                recFilter['skip'] = True
            elif flag == '-s':
                start = getInt(value)
                if start is None:
                    print(f"-s '{value}' needs to be an integer", file=sys.stderr)
                    return 2
            elif flag == '-l':
                recFilter['longName'] = True
            elif flag == '--sparse':
                recFilter['sparse'] = True
            elif flag == '-v':
                verbose += 1
            elif flag == '--Chirp':
                writer = Chirp
            elif flag == '--RtSys':
                writer = RtSys
            elif flag == '--Icom':
                from icom import Icom
                writer = Icom
            elif flag == '--IC-92':
                from rt_ic92 import RtSysIc92
                writer = RtSysIc92
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        print(usage, file=sys.stderr)
        return 2

    if args:
        ifile = open(args[0],'r')
    csvin = csv.reader(ifile)

    return process(csvin, reader, csvout, writer, start, recFilter)

def findReader(csvin) -> Channel:
    """Examine a CSV file to determine which of several known formats
    it is. Return Channel object or None"""
    from ics217 import ics217
    from rr import rr
    from wwara import WWARA
    from nerd import NERD
    readers = [ics217, Chirp, RtSys, rr, Channel, WWARA, NERD]
    for line in csvin:
        if verbose >= 2:
            print(line, file=sys.stderr)
        for r in readers:
            if r.probe(line):
                return r
    return None

def round_down(n,r): return n-n%r
def round_up(n,r):   return round_down(n+r-1,r)

def process(csvin, reader, csvout, writer, start, recFilter):

    # If reader not specified, scan the input to determine the format.
    if not reader:
        reader = findReader(csvin)

    if not reader:
        raise Exception("Unable to determine input format")

    writer.header(csvout, recFilter)

    # The default numbering system is to pack output records tightly, with
    # strictly increasing record numbers. If "sparse" is set, we take the existing
    # record number (starting with 1) as an offset relative to "start".
    # Some records (e.g. ACS ICS 217) have leading or trailing letters, which
    # we need to remove to get the record number. If the leading character
    # changes, we take that as a signal to jump up to the next multiple of 50.
    sparse = recFilter.get('sparse')
    recno = 1
    maxrec = -1
    leader = None

    for line in csvin:
        if verbose >= 3:
            print(line, file=sys.stderr)
        recs = reader.parse(line, recFilter)
        if not recs:
            continue

        # Some plugins, i.e. wwara, can return a list instead of a single
        # record. The "sparse" option is not compatible with this feature.
        if isinstance(recs, list):
            sparse = False
        else:
            recs = [recs]
        for rec in recs:
            try:
                if verbose >= 2: print(rec, file=sys.stderr)
                if sparse and rec.Chan != None:
                    chan = rec.Chan
                    if not chan[0].isdigit():
                        if not leader: leader = chan[0]
                        elif chan[0] != leader:
                            leader = chan[0]
                            start = round_up(start + maxrec - 1, 50) + 1
                    recno = getInt(getDigits(chan), recno)
                if recno > maxrec: maxrec = recno
                writer.write(rec, csvout, start+recno-1, recFilter)
                recno += 1
            except Exception as e:
                # Parse failures are normal, don't report them; they just clutter
                # the output.
                if verbose:
                    print("Failed to write: ", rec, file=sys.stderr)
                    print(e, file=sys.stderr)
                    traceback.print_exc(5, sys.stderr)
                continue
    return 0


digits_re = re.compile(r'''\d+''')

def getDigits(s):
    if s.isdigit(): return s
    mo = digits_re.search(s)
    return mo.group() if mo else None

def getInt(s, dflt=None):
    try:
        return int(s)
    except:
        return dflt

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf8 -*-

import csv
import getopt
import re
import sys

import ics217
from Acs2Chirp import Chirp
from Acs2RtSys import RtSys
from Acs2Icom import Icom

# See below for the ics217 subclasses responsible for formatting the
# output.

verbose = 0

def main(reader, usage):
    global verbose
    ifile = sys.stdin
    #ifile = open('foo.csv','r')

    csvin = csv.reader(ifile)
    csvout = csv.writer(sys.stdout)
    writer = Chirp

    start = 1
    recFilter = {}
    try:
        (optlist, args) = getopt.getopt(sys.argv[1:], 'hb:s:B:NR:v',
            ['help', 'Chirp', 'RtSys', 'Icom'])
        for flag, value in optlist:
            if flag in ('-h', '--help'):
                print(usage)
                return 0
            elif flag == '-b':
                recFilter['bands'] = None if value == "all" else value
            elif flag == '-N':
                recFilter['newEntries'] = True
            elif flag == '-R':
                recFilter['regex'] = re.compile(value)
            elif flag == '-B':
                recFilter['banks'] = [value]
            elif flag == '-s':
                start = getInt(value)
                if start is None:
                    print(f"-s '{value}' needs to be an integer", file=sys.stderr)
                    return 2
            elif flag == '-v':
                verbose += 1
            elif flag == '--Chirp':
                writer = Chirp
            elif flag == '--RtSys':
                writer = RtSys
            elif flag == '--Icom':
                writer = Icom
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        print(usage, file=sys.stderr)
        return 2

    return process(csvin, reader, csvout, writer, start, recFilter)


def process(csvin, reader, csvout, writer, start, recFilter):
    writer.header(csvout, recFilter)

    # If the "Chan" property of a record is a legit integer, it's used
    # as the record number for the output (adjusted for start). Else, we
    # increment a counter.
    count = 1

    for line in csvin:
        if verbose >= 2:
            print(line, file=sys.stderr)
        rec = reader.parse(line, recFilter)
        if not rec:
            continue

        try:
            if verbose: print(rec, file=sys.stderr)
            if rec.Chan.isdigit(): count = int(rec.Chan)
            writer.write(rec, csvout, start+count-1, recFilter)
        except Exception as e:
            # Parse failures are normal, don't report them; they just clutter
            # the output.
            if verbose:
                print("Failed to write: ", rec, file=sys.stderr)
                print(e, file=sys.stderr)
            continue

        count += 1


def getInt(s, dflt=None):
    try:
        return int(s)
    except:
        return dflt


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf8 -*-

import csv
import getopt
import re
import sys

usage = f"""Convert CSV file from ACS 217 spreadsheet to format RT Systems uses

  {sys.argv[0]} < W7ACS_ICS-217A_20240131.csv > ACS_RT.csv

  Options:
        -b <band>       Any combination of the letters VULTDH, or "all"
                                V = VHF (2m band)
                                U = UHF (70cm band)
                                L = Low frequency (6m band)
                                T = 220 MHz band (1.25m band)
                                D = digital
                                H = Seattle Emergency Hubs GMRS
                            Default is all
        -N              Use the 'U..N' entries (default is don't use)
        -R <regex>      Use regex to select entries, e.g. 'V' or 'U..N'
        -s <n>          Start numbering at <n>; default is 1
        -B <bank>       Select bank for devices that use it (i.e. FT-60)
        -v              Increase verbosity
"""

# TODO: add an option to specify the output format. Currently, only "RtSys"
# exists.


# Convert CSV file from ACS 217 spreadsheet to format RT Systems uses for FT-60

import ics217

# See below for the ics217 subclasses responsible for formatting the
# output.

verbose = 0

def main(writer, usage=usage):
    global verbose
    ifile = sys.stdin
    #ifile = open('foo.csv','r')

    reader = csv.reader(ifile)
    csvout = csv.writer(sys.stdout)

    start = 1
    recFilter = {}
    try:
        (optlist, args) = getopt.getopt(sys.argv[1:], 'hb:s:B:NR:v', ['help'])
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
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        print(usage, file=sys.stderr)
        return 2

    return process(reader, ics217.ics217, csvout, writer, start, recFilter)


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

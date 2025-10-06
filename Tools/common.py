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

    bands = None
    count = 1
    bank = None
    newEntries = False
    regex = None
    try:
        (optlist, args) = getopt.getopt(sys.argv[1:], 'hb:s:B:NR:v', ['help'])
        for flag, value in optlist:
            if flag in ('-h', '--help'):
                print(usage)
                return 0
            elif flag == '-b':
                bands = None if value == "all" else value
            elif flag == '-N':
                newEntries = True
            elif flag == '-R':
                regex = re.compile(value)
            elif flag == '-B':
                bank = getInt(value)
            elif flag == '-s':
                count = getInt(value)
                if count is None:
                    print(f"-s '{value}' needs to be an integer", file=sys.stderr)
                    return 2
            elif flag == '-v':
                verbose += 1
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        print(usage, file=sys.stderr)
        return 2

    writer.header(csvout, bank)

    for line in reader:
        if verbose >= 2:
            print(line, file=sys.stderr)
        acsRec = ics217.parse(line, bands, newEntries, regex)
        if not acsRec:
            continue

        try:
            if verbose: print(acsRec, file=sys.stderr)
            writer.write(acsRec, csvout, count, bank)
        except Exception as e:
            # Parse failures are normal, don't report them; they just clutter
            # the output.
            if verbose:
                print("Failed to write: ", acsRec, file=sys.stderr)
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

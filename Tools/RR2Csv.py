#!/usr/bin/env python3
# -*- coding: utf8 -*-

usage = """Convert CSV file from Repeater Roundabout spreadsheet to format CHIRP uses

  RR2Chirp.py < all_rr_frequencies.csv > rr_chirp.csv

  Options:
        --Chirp         output for Chirp (default)
        --RT            output for RT Systems
        --Icom          output for Icom
        -B <bank>       Select bank for devices that use it (i.e. FT-60)
        -s <n>          Start numbering at <n>; default is 1
        -R <regex>      Use regex to select entries, e.g. 'V' or 'U..N'
        -v              verbose

Generates CSV files compatible with CHIRP software.  These files
should work with any radio, but if not, please contact Ed Falk,
KK7NNS au gmail.com directly and we'll figure it out.
"""

import csv
import getopt
import re
import signal
import sys

import common
from rr import rr
from chirp import Chirp
from rtsys import RtSys
from icom import Icom

verbose = 0

def main(reader, usage=usage):
    global verbose
    ifile = sys.stdin
    #ifile = open('all_rr_frequencies.csv','r')

    csvin = csv.reader(ifile)
    csvout = csv.writer(sys.stdout)
    writer = Chirp
    count = 1
    recFilter = {}

    regex = None
    try:
        (optlist, args) = getopt.getopt(sys.argv[1:], 'hs:B:R:v', ['help', 'Chirp', 'RtSys', 'Icom'])
        for flag, value in optlist:
            if flag in ('-h', '--help'):
                print(usage)
                return 0
            elif flag == '-R':
                regex = re.compile(value)
            elif flag == '-B':
                recFilter['banks'] = [value]
            elif flag == '-s':
                count = common.getInt(value)
                if count is None:
                    print(f"-s '{value}' needs to be an integer", file=sys.stderr)
                    return 2
            elif flag == '-v':
                verbose += 1
            elif flag == '--RtSys':
                writer = RtSys
            elif flag == '--Icom':
                writer = Icom
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        print(usage, file=sys.stderr)
        return 2

    common.process(csvin, reader, csvout, writer, count, recFilter)

if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(main(rr, usage))
  except KeyboardInterrupt as e:
    print(file=sys.stderr)
    sys.exit(1)

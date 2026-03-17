#!/usr/bin/env python3
# -*- coding: utf8 -*-

import csv
import errno
import getopt
import os
import signal
import string
import sys

import channel
from common import process
from chirp import Chirp
from rtsys import RtSys
from wwara import WWARA

usage = f"""Convert CSV file from ACS 217 spreadsheet to formats radios use

  {sys.argv[0]} < W7ACS_ICS-217A_20240131.csv > Chirp/acs.csv

  Options:
        --Chirp         Output for Chirp (default)
        --RtSys         Output for RT Systems
        -b <band>       Any combination of the letters VULTDH, or "all"
                                V = VHF (2m band)
                                U = UHF (70cm band)
                                L = Low frequency (6m band)
                                T = 220 MHz band (1.25m band)
                                D = digital
                                G = GMRS
                            Default is all
        -R <regex>      Use regex to select entries, e.g. 'V' or 'U..N'
        -s <n>          Start numbering at <n>; default is 1
        -B <banks>      Select banks for devices that use it (i.e. FT-60)
        --skip          Set the "scan skip" flag for all entries
        -v              Increase verbosity

Generates CSV files to be used as code plugs.  These files
should work with any radio, but if not, please contact Ed Falk,
KK7NNS au gmail.com directly and we'll figure it out.
"""


verbose = 0

def main(reader, usage):
    global verbose
    ifile = sys.stdin

    csvout = csv.writer(sys.stdout)
    writer = Chirp

    start = 1
    recFilter = {}
    try:
        (optlist, args) = getopt.getopt(sys.argv[1:], 'hb:s:B:R:v',
            ['help', 'Chirp', 'RtSys', 'skip'])
        for flag, value in optlist:
            if flag in ('-h', '--help'):
                print(usage)
                return 0
            elif flag == '-b':
                recFilter['bands'] = None if value == "all" else value
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
            elif flag == '-v':
                verbose += 1
            elif flag == '--Chirp':
                writer = Chirp
            elif flag == '--RtSys':
                writer = RtSys
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        print(usage, file=sys.stderr)
        return 2

    if args:
        ifile = open(args[0],'r')
    csvin = csv.reader(ifile)

    return process(csvin, reader, csvout, writer, start, recFilter)


if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(main(WWARA, usage))
  except KeyboardInterrupt as e:
    print(file=sys.stderr)
    sys.exit(1)

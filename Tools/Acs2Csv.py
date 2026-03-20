#!/usr/bin/env python3
# -*- coding: utf8 -*-

import csv
import errno
import getopt
import os
import signal
import string
import sys

usage = f"""Convert CSV file from ACS 217 spreadsheet to formats radios use

  {sys.argv[0]} [options] inputfile.csv > outputfile.csv

  Options:
    Input filtering:
        -b <bands>      Any combination of the letters VULTDH, or "all"
                                V = VHF (2m band)
                                U = UHF (70cm band)
                                L = Low frequency (6m band)
                                T = 220 MHz band (1.25m band)
                                D = digital
                                G = GMRS
                                H = Seattle Emergency Hubs GMRS
                            Default is all
        -m <modes>      Filter by mode. Any combination of the following:
                                A = AM
                                F = FM
                                L = lsb
                                U = usb
                                C = CW
                                D = DMR
                                S = DSTAR
                                V = Digital Voice (DV)
                                d = other digital
        -N              Use the 'U..N' entries (default is don't use)
        -R <regex>      Use regex to select entries, e.g. 'V' or 'U..N'

    Output format:
        --Chirp         Output for Chirp (default)
        --RtSys         Output for RT Systems
        --Icom          Output for Icom
        --IC-92         Output for Icom-92, RT Systems
        -l              Long names, for radios that can take them
        -s <n>          Start numbering at <n>; default is 1
        --sparse        Leave gaps in record numbers where
                        there are gaps in the input
        --skip          Set the "scan skip" flag for all entries
        -B <banks>      Select banks for devices that use it (i.e. FT-60)
        -v              Increase verbosity

Generates CSV files to be used as code plugs.  These files
should work with any radio, but if not, please contact Ed Falk,
KK7NNS au gmail.com directly and we'll figure it out.

This program recognizes the input formats used by AARL, Seattle ACS,
Chirp, RT Systems, and Repeater Roundabout. Contact the author if
you have another format you'd like to use; it's not hard.
"""

import common
import channel



if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(common.main(None, usage))
  except KeyboardInterrupt as e:
    print(file=sys.stderr)
    sys.exit(1)

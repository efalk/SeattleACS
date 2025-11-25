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

  {sys.argv[0]} < W7ACS_ICS-217A_20240131.csv > Chirp/acs.csv

  Options:
        --Chirp         Output for Chirp (default)
        --RT            Output for RT Systems
        --Icom          Output for Icom
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
        -B <banks>      Select banks for devices that use it (i.e. FT-60)
        -v              Increase verbosity

Generates CSV files to be used as code plugs.  These files
should work with any radio, but if not, please contact Ed Falk,
KK7NNS au gmail.com directly and we'll figure it out.
"""

import common
import channel
from ics217 import ics217



if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(common.main(ics217, usage))
  except KeyboardInterrupt as e:
    print(file=sys.stderr)
    sys.exit(1)

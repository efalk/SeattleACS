#!/usr/bin/env python3
# -*- coding: utf8 -*-

usage = """Convert CSV file from ACS 217 spreadsheet to the format Icom's programming software (such as CS-705) uses

  Acs2Icom.py < W7ACS_ICS-217A_20240131.csv > ACS_icom.csv

  Options:
        -b <band>       Any combination of the letters VULTDH, or "all"
                                V = VHF (2m band)
                                U = UHF (70cm band)
                                L = Low frequency (6m band)
                                T = 220 MHz band (1.25m band)
                                D = digital
                                H = Seattle Emergency Hubs GMRS
                            default is VU
        -s <n>          Start numbering at <n>; default is 1
        -v              verbose

Generates CSV files compatible with Icom radio software.
"""

import csv
import errno
import getopt
import os
import re
import signal
import string
import sys

import common
import ics217

class Icom(object):
    @staticmethod
    def header(csvout: csv.writer, bank: int):
        """Write out the header line for the CSV file."""
        csvout.writerow(["CH No","Name","Frequency","Dup","Offset","Tone","Repeater Tone","cToneFreq","DtcsCode","DtcsPolarity","Mode","TStep","Skip"])

    @staticmethod
    def write(icsrec: ics217, csvout: csv.writer, count: int, bank: int):
        """Write out one record. This may throw an exception if any of
        the ics-217 fields are not valid."""
        Chan = icsrec.Chan       # memory #, 0-based
        Config = icsrec.Config
        Name = icsrec.Name       # memory label
        Rxfreq = icsrec.Rxfreq       # RX freq
        Mode = icsrec.Mode
        Wide = icsrec.Txwid
        Txfreq = icsrec.Txfreq       # RX freq
        Txtone = icsrec.Txtone
        Rxtone = icsrec.Rxtone

        if not Txtone: Txtone = 'CSQ'
        if not Rxtone or Rxtone.startswith('TSQ'): Rxtone = Txtone

        # Derived values
        Offset = float(Txfreq) - float(Rxfreq)
        if Config == 'Simplex' or Txfreq == Rxfreq: 
            Duplex = ''
            OffsetValue = 0
        elif Offset > 0: 
            Duplex = 'DUP+'
            OffsetValue = round(abs(Offset), 1)
        else: 
            Duplex = 'DUP-'
            OffsetValue = round(abs(Offset), 1)
        
        # Default values - ignored if not used based on other fields
        RepeaterTone = '88.5Hz'
        cToneFreq = '88.5'
        DtcsCode = '23'

        # Handle tone settings
        if Txtone == 'CSQ':
            ToneMode = ''
            RepeaterTone = '88.5Hz'
        elif Txtone[0] == 'D':
            ToneMode = 'DTCS'
            DtcsCode = Txtone[1:]
        else:
            ToneMode = 'Tone'
            RepeaterTone = f"{Txtone}Hz"

        Comment = icsrec.getComment()

        # Format frequency without rounding, just remove trailing zeros
        freq = f"{float(Rxfreq):g}"

        # All ACS Frequencies are FM. Note that at least the IC-705 and CS-705 software don't support NFM.
        RadioMode = 'FM'

        # Create names matching Icom format - simplified
        # Extract first part of comment for simple name
        FirstPart = Comment.split(';')[0].strip() if Comment else ''
        SimpleName = f"{Name} {FirstPart}" if FirstPart else Name

        # Use sequential channel numbering
        ChannelNum = count

        # Strip commas from any names to avoid CSV quoting - The ICOM software can't handle it.
        SimpleName = SimpleName.replace(',', '')

        csvout.writerow([ChannelNum, SimpleName, freq, Duplex, OffsetValue, ToneMode, RepeaterTone, cToneFreq, DtcsCode, 'NN', RadioMode, 5, ''])


if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(common.main(Icom, usage))
  except KeyboardInterrupt as e:
    print(file=sys.stderr)
    sys.exit(1)

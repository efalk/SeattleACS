#!/usr/bin/env python3
# -*- coding: utf8 -*-

usage = """Convert CSV file from ACS 217 spreadsheet to format CHIRP uses

  Acs2Chirp.py < W7ACS_ICS-217A_20240131.csv > ACS_chirp.csv

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

Generates CSV files compatible with CHIRP software.  These files
should work with any radio, but if not, please contact Ed Falk,
KK7NNS au gmail.com directly and we'll figure it out.
"""

import csv
import errno
import getopt
import os
import signal
import string
import sys

import common
import ics217

class Chirp(object):
    @staticmethod
    def header(csvout: csv.writer, bank: int):
        """Write out the header line for the CSV file."""
        #print("Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneFreq,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE", file=ofile)
        csvout.writerow(["Location","Name","Frequency","Duplex","Offset","Tone","rToneFreq","cToneFreq","DtcsCode","DtcsPolarity","RxDtcsCode","CrossMode","Mode","TStep","Skip","Power","Comment","URCALL","RPT1CALL","RPT2CALL","DVCODE"])

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
        if Config == 'Simplex' or Txfreq == Rxfreq: Duplex = ''
        elif Offset > 0: Duplex = '+'
        else: Duplex = '-'

        rToneFreq = '88.5'
        cToneFreq = '88.5'  # Only used on cross mode
        RxDtcsCode = '023'
        CrossMode = 'Tone->Tone'

        # There are nine possibilities for Txtone/Rxtone
        # (Actually ten because you could have Tone->Tone with
        # different frequencies)
        if Txtone == 'CSQ':
            if Rxtone.startswith('CSQ'):
                ToneMode = ''
            elif Rxtone[0] == 'D':
                ToneMode = 'DTCS-R'
                RxDtcsCode = Rxtone[1:]
            else:
                rToneFreq = Rxtone
                ToneMode = 'TSQL-R'
        elif Txtone[0] == 'D':
            RxDtcsCode = Txtone[1:]
            if Rxtone.startswith('CSQ'):
                ToneMode = 'DTCS'   # Chirp doesn't seem to support this case
            elif Rxtone[0] == 'D':
                ToneMode = 'DTCS'
            else:
                rToneFreq = Rxtone
                ToneMode = 'Cross'
                CrossMode = 'DTCS->Tone'
        else:
            rToneFreq = cToneFreq = Txtone
            if Rxtone.startswith('CSQ'):
                ToneMode = 'Tone'   # Most common case
            elif Rxtone[0] == 'D':
                RxDtcsCode = Rxtone[1:]
                ToneMode = 'Cross'
                CrossMode = 'Tone->DTCS'
            else:
                if Rxtone == Txtone:
                    ToneMode = 'TSQL'
                else:
                    cToneFreq = Rxtone
                    ToneMode = 'Cross'

        Comment = icsrec.getComment()

        if Mode == 'F':
            if Wide == 'N': Wide = 'NFM'
            else: Wide = 'FM'
        elif Mode == 'A':
            if Wide == 'N': Wide = 'NAM'
            else: Wide = 'AM'
        elif Mode == 'D':
            Wide = 'DIG'
        else:
            if Wide == 'W': Wide = 'FM'
            elif Wide == 'N': Wide = 'NFM'

        # Output (Chirp):
        #  Location  Memory location, starting at 1
        #  Name      e.g. "PSRG"
        #  Frequency e.g. 146.960000
        #  Duplex        off, +, -, or <blank>
        #  Offset        e.g. 0.60000
        #  Txtone    <blank> Tone TSQL DTCS TSQL-R DTCS-R Cross
        #  rToneFreq
        #  cToneFreq
        #  DtcsCode  e.g. 023
        #  DtcsPolarity  e.g. NN
        #  RxDtcsCode    e.g. 023
        #  CrossMode    Tone->Tone Tone->DTCS DTCS->Tone DTCS-> ->DTCS ->Tone DTCS->DTCS
        #  Mode      WFM, FM, NFM
        #  TStep     e.g. 5.00
        #  Skip      <blank>, S
        #  Power     e.g. 5.0W
        #  Comment   any text
        #  URCALL    <blank>
        #  RPT1CALL  <blank>
        #  RPT2CALL  <blank>
        #  DVCODE    <blank>

        csvout.writerow([count, Name, Rxfreq, Duplex, f"{abs(Offset):.6f}", ToneMode, rToneFreq, cToneFreq, RxDtcsCode, 'NN', RxDtcsCode, CrossMode, Wide, 5.00, '', '5.0W', Comment, '', '', '', ''])


if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(common.main(Chirp, usage))
  except KeyboardInterrupt as e:
    print(file=sys.stderr)
    sys.exit(1)

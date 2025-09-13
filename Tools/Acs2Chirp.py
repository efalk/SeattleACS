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
    def header(ofile, bank):
        """Write out the header line for the CSV file."""
        print("Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneFreq,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE", file=ofile)

    @staticmethod
    def write(icsrec, ofile, count, bank):
        """Write out one record. This may throw an exception if any of
        the ics-217 fields are not valid."""
        Chan = icsrec.Chan       # memory #, 0-based
        Config = icsrec.Config  
        Name = icsrec.Name       # memory label
        Comment = icsrec.Comment  
        Rxfreq = icsrec.Rxfreq       # RX freq
        Wide = icsrec.Txwid
        Txfreq = icsrec.Txfreq       # RX freq
        Tone = icsrec.Txtone  
        Remarks = icsrec.Remarks  

        # Derived values
        Offset = float(Txfreq) - float(Rxfreq)
        if Config == 'Simplex' or Txfreq == Rxfreq: Duplex = ''
        elif Offset > 0: Duplex = '+'
        else: Duplex = '-'

        if Tone == 'CSQ':
            ToneMode = ''
            Tone = '88.5'
            Dtcs = '023'
        elif Tone.startswith('D'):
            ToneMode = 'DTCS'
            Dtcs = Tone[1:]
            Tone = '88.5'
        else:
            ToneMode = 'Tone'
            Dtcs = '023'

        if Comment and Remarks:
            Comment = Comment + '; ' + Remarks
        elif Remarks:
            Comment = Remarks

        if Wide == 'W': Wide = 'FM'
        elif Wide == 'N': Wide = 'NFM'

        # Output (Chirp):
        #  Location  Memory location, starting at 1
        #  Name      e.g. "PSRG"
        #  Frequency e.g. 146.960000
        #  Duplex        off, +, -, or <blank>
        #  Offset        e.g. 0.60000
        #  Tone      <blank> Tone TSQL DTCS TSQL-R DTCS-R Cross
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

        print(f"{count},{Name},{Rxfreq},{Duplex},{abs(Offset):.6f},{ToneMode},{Tone},{Tone},{Dtcs},NN,{Dtcs},Tone->Tone,{Wide},5.00,,5.0W,{Comment},,,,")


if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(common.main(Chirp, usage))
  except KeyboardInterrupt as e:
    print()
    sys.exit(1)

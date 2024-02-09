#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Convert CSV file from ACS 217 spreadsheet to format CHIRP uses

import csv
import errno
import getopt
import os
import signal
import string
import sys

import ics217

def main():
    reader = csv.reader(sys.stdin)

    print("Location,Name,Frequency,Duplex,Offset,Tone,rToneFreq,cToneFreq,DtcsCode,DtcsPolarity,RxDtcsCode,CrossMode,Mode,TStep,Skip,Power,Comment,URCALL,RPT1CALL,RPT2CALL,DVCODE")

    count = 1
    for l in reader:

        # Input (ACS 217):
        #  CH#, e.g. "V01"
        #  config: Repeater; Simplex
        #  name
        #  comment
        #  rx freq
        #  narrow/wide: W; N
        #  RX tone: always "CSQ" (carrier squelch, i.e. no tone)
        #  Tx Freq
        #  narrow/wide: W; N
        #  TX tone: e.g. 103.5
        #  Mode: A; MF; MP; D
        #  Remarks

        acsRec = ics217.parse(l)
        if not acsRec:
            continue

        Chan = acsRec.Chan       # memory #, 0-based
        Config = acsRec.Config  
        Name = acsRec.Name       # memory label
        Comment = acsRec.Comment  
        Rxfreq = acsRec.Rxfreq       # RX freq
        Wide = acsRec.Txwid
        Txfreq = acsRec.Txfreq       # RX freq
        Tone = acsRec.Txtone  
        Remarks = acsRec.Remarks  

        # Derived values
        try:
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

        except Exception as e:
            print("Failed to parse: ", l, file=sys.stdout)
            print(e, file=sys.stdout)
            continue

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

        #print(f"{count},{Rxfreq},{Txfreq},{Offset_s},{Mode},FM,{Name},Y,{ToneMode},{Tone},{Dtcs},Scan, 5 kHz, N, High,N,N,{Comment}")
        print(f"{count},{Name},{Rxfreq},{Duplex},{abs(Offset):.6f},{ToneMode},{Tone},{Tone},{Dtcs},NN,{Dtcs},Tone->Tone,{Wide},5.00,,5.0W,{Comment},,,,")

        count += 1



if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(main())
  except KeyboardInterrupt as e:
    print()
    sys.exit(1)

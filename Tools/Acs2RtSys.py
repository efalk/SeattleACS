#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Convert CSV file from ACS 217 spreadsheet to format RT Systems uses for FT-60

import csv
import errno
import getopt
import os
import signal
import string
import sys

import acs

def main():
    reader = csv.reader(sys.stdin)

    #print(",Receive Frequency,Transmit Frequency,Offset Frequency,Offset Direction,Operating Mode,Name,Show Name,Tone Mode,CTCSS,DCS,Skip,Step,Clock Shift,Tx Power,Tx Narrow,Pager Enable,Bank 1,Bank 2,Bank 3,Bank 4,Bank 5,Bank 6,Bank 7,Bank 8,Bank 9,Bank 10,Comment,")
    print(",Receive Frequency,Transmit Frequency,Offset Frequency,Offset Direction,Operating Mode,Name,Show Name,Tone Mode,CTCSS,DCS,Skip,Step,Clock Shift,Tx Power,Tx Narrow,Pager Enable,Comment,")

    count = 1
    for l in reader:
        acsRec = acs.parse(l)
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

        try:
            Offset = float(Txfreq) - float(Rxfreq)
            if Config == 'Simplex' or Txfreq == Rxfreq:
                Offset_s = ''
            elif abs(Offset) < 1.0:
                Offset_s = "%.0f kHz" % (abs(Offset)*1000.)
            else:
                Offset_s = "%.4f MHz" % abs(Offset)

            if Config == 'Simplex' or Txfreq == Rxfreq:
                Mode = "Simplex"
            elif Offset > 0:
                Mode = "Plus"
            else:
                Mode = "Minus"

            if Tone == 'CSQ':
                ToneMode = 'None'
                Tone = ''
                Dcs = ''
            elif Tone.startswith('D'):
                ToneMode = 'DCS'
                Dcs = Tone[1:]
                Tone = ''
            else:
                ToneMode = 'Tone'
                Dcs = ''

        except Exception as e:
            print("Failed to parse: ", l, file=sys.stdout)
            print(e)
            continue


#        if Config == 'Simplex' or Txfreq == Rxfreq: ToneMode = 'None'
#        elif Tone: ToneMode = 'Tone'
#        else: ToneMode = 'Dcs'

        if Comment and Remarks:
            Comment = Comment + '; ' + Remarks
        elif Remarks:
            Comment = Remarks

        # Output (RT QRZ1):
        #  Receive Frequency    e.g. 146.96000
        #  Transmit Frequency   e.g. 146.36000
        #  Offset Frequency     "600 kHz", "5.0000 MHz"
        #  Offset Direction,
        #  Operating Mode
        #  Name
        #  Tone Mode
        #  CTCSS
        #  Rx CTCSS
        #  DCS
        #  Rx DCS
        #  DCS Polarity,
        #  Tx Power
        #  Skip
        #  Busy Lockout
        #  Comment,

        print(f"{count},{Rxfreq},{Txfreq},{Offset_s},{Mode},FM,{Name},Y,{ToneMode},{Tone},{Dcs},Scan, 5 kHz, N, High,N,N,{Comment}")

        count += 1



if __name__ == '__main__':
    sys.exit(main())

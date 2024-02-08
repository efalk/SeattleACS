#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Convert CSV file from CHIRP to format RT Systems uses

import sys
import os
import string
import errno
import signal
import getopt

TSQL = {"None":"", "T Sql":"TSQL"}

def noHz(s):
    return s.rstrip(' kHz')

print(",Receive Frequency,Transmit Frequency,Offset Frequency,Offset Direction,Operating Mode,Name,Show Name,Tone Mode,CTCSS,Rx CTCSS,DCS,Skip,Step,Clock Shift,Tx Power,Tx Narrow,Pager Enable,Comment,")


for line in sys.stdin:
    l = line.rstrip()
    if l[0] in '#CL':
        continue
    l = l.split(',')

    #
    # Input (CHIRP):
    #  Location, Name, Frequency, Duplex, Offset, Tone, rToneFreq, cToneFreq, 
    #  DtcsCode, DtcsPolarity, RxDtcsCode, CrossMode, Mode, TStep, Skip, 
    #  Power, Comment, URCALL, RPT1CALL, RPT2CALL, DVCODE
    #  31, PSRG, 146.960000, off, 0.000000, , 88.5, 88.5, 023, NN, 023, Tone->Tone, FM, 5.00, , 5.0W, , , , , 
    #  53, SIMP01, 462.562500, , 0.000000, TSQL, 141.3, 141.3, 023, NN, 023, Tone->Tone, FM, 5.00, , 0.5W, , , , , 

    Chan = l[0]     # memory #, 0-based
    Name = l[1]     # memory label
    Freq = l[2]     # RX freq
    Duplex = l[3]   # <blank> + - split off
    Offset = l[4]   # offset, MHz *or* TX freq for "split"
    Tone = l[5]     # "Tone Mode" column: <blank> Tone, TSQL, DTCS, DCCS-R, TSQL-R, Cross
    Rtone = l[6]    # "Tone": repeater tone (TX)
    Ctone = l[7]    # "Tone Squelch": squelch tone (RX)
    DtcsCode = l[8]
    DtcsPol = l[9]
    RxDtcsCode = l[10]  # DTCS Polarity
    CrossMode = l[11]   # Tone->Tone, DTCS->, ->DTCS, DTCS->Tone, ->Tone, DTCS->DTCS, Tone->
    Mode = l[12]    # WFM, FM, NFM, AM, NAM, DV, USB, LSB, CW, RTTY, DIG, PKT, NCW, NCWR,
                    # CWR, P25, Auto, RTTYR, FSK, FSKR, DMR, DN
    TStep = l[13]   # Tuning Step, e.g. 5.0
    Skip = l[14]    # <blank> S
    Power = l[15]   # E.g. "5.0W"
    Comment = l[16]
    # File also includes URCALL, RPT1CALL, RPT2CALL, DVCODE which are not
    # shown in the app and which are all blank in my test file.

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

    if Duplex == '+':
        TxFreq = float(Freq) + float(Offset)
        OffsetDir = 'Plus'
    elif Duplex == '-':
        TxFreq = float(Freq) - float(Offset)
        OffsetDir = 'Minus'
    else:
        TxFreq = float(Freq)
        OffsetDir = 'Simplex'

    off2 = float(Offset)
    if off2 == 0.0:
        Offset = ''
    elif off2 > 1.0:
        Offset = Offset + " MHz"
    else:
        Offset = "%.0f kHz" % (off2*1000)

    if Tone == "":
        Tone = "None"
    elif Tone == "Tone":
        Tone = "Tone"
    elif Tone == "TSQL":
        Tone = "T Sql"
    elif Tone == "DTCS":
        Tone = "DCS"
    elif Tone == "DCS-R":
        Tone = "D Code"
    elif Tone == "TSQL-R":
        Tone = "T Sql"
    elif Tone == "Cross":
        if CrossMode == "Tone->Tone":
            Tone = "Tone"
        elif CrossMode == "Tone->DTCS":
            Tone = "T DCS"
        elif CrossMode == "DTCS->Tone":
            Tone = "D Tone"
        else:
            Tone = "Tone"
    else:
        if Duplex in "+-":
            Tone = "Tone"
        else:
            Tone = "None"

    narrow = "Y" if Mode == "NFM" else "N"

    print(f"{Chan},{Freq},{TxFreq:.4f},{Offset},{OffsetDir},FM,{Name},Y,{Tone},{Rtone},{Ctone},{DtcsCode},Scan,5 kHz,N,High,{narrow},N,{Comment}")


#   <ch>									1
#   Receive Frequency	146.9600
#   Transmit Frequency	146.3600
#   Offset Frequency	600 kHz
#   Offset Direction	Minus
#   Operating Mode		FM
#   Name			V01PSR
#   Show Name		Y
#   Tone Mode		Tone
#   CTCSS			103.5
#   DCS			<blank>
#   Skip			Scan
#   Step			5 kHz
#   Clock Shift		N
#   Tx Power		High
#   Tx Narrow		N
#   Pager Enable		N
#   Comment			PSRG; coordination; WW7PSR; Allstar 2462



    Chan = l[0]     # memory #, 0-based
    Name = l[1]     # memory label
    Freq = l[2]     # RX freq
    Duplex = l[3]   # <blank> + - split off
    Offset = l[4]   # offset, MHz *or* TX freq for "split"
    Tone = l[5]     # "Tone Mode" column: <blank> Tone, TSQL, DTCS, DCCS-R, TSQL-R, Cross
    Rtone = l[6]    # "Tone": repeater tone (TX)
    Ctone = l[7]    # "Tone Squelch": squelch tone (RX)
    DtcsCode = l[8]
    DtcsPol = l[9]
    RxDtcsCode = l[10]  # DTCS Polarity
    CrossMode = l[11]   # Tone->Tone, DTCS->, ->DTCS, DTCS->Tone, ->Tone, DTCS->DTCS, Tone->
    Mode = l[12]    # WFM, FM, NFM, AM, NAM, DV, USB, LSB, CW, RTTY, DIG, PKT, NCW, NCWR,
                    # CWR, P25, Auto, RTTYR, FSK, FSKR, DMR, DN
    TStep = l[13]   # Tuning Step, e.g. 5.0
    Skip = l[14]    # <blank> S
    Power = l[15]   # E.g. "5.0W"
    Comment = l[16]
    # File also includes URCALL, RPT1CALL, RPT2CALL, DVCODE which are not
    # shown in the app and which are all blank in my test file.

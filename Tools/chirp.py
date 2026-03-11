#!/usr/bin/env python3
# -*- coding: utf8 -*-


import csv
import decimal
import sys

import channel

class Chirp(channel.Channel):

    # INPUT SECTION

    @staticmethod
    def probe(line: list):
        """Examine line to see if the input is in Chirp format. Return
        None if not. Anything else is true."""
        return len(line) >= 17 and \
            line[1] == "Name" and \
            line[2] == "Frequency" and \
            line[3] == "Duplex" and \
            line[4] == "Offset" and \
            line[5] == "Tone" and \
            line[6] == "rToneFreq" and \
            line[7] == "cToneFreq" and \
            line[8] == "DtcsCode" and \
            line[9] == "DtcsPolarity"

    def __init__(this, line):
        """Create a Chirp object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""

        Chan = line[0]     # memory #, 0-based
        Name = line[1]     # memory label
        Freq = line[2]     # RX freq
        Duplex = line[3]   # <blank> + - split off
        Offset = line[4]   # offset, MHz *or* TX freq for "split"
        Tone = line[5]     # "Tone Mode" column: <blank> Tone, TSQL, DTCS, DCCS-R, TSQL-R, Cross
        Rtone = line[6]    # "Tone": repeater tone (TX)
        Ctone = line[7]    # "Tone Squelch": squelch tone (RX)
        DtcsCode = line[8]
        DtcsPol = line[9]
        RxDtcsCode = line[10]  # DTCS Polarity
        CrossMode = line[11]   # Tone->Tone, DTCS->, ->DTCS, DTCS->Tone, ->Tone, DTCS->DTCS, Tone->
        Mode = line[12]    # WFM, FM, NFM, AM, NAM, DV, USB, LSB, CW, RTTY, DIG, PKT, NCW, NCWR,
                           # CWR, P25, Auto, RTTYR, FSK, FSKR, DMR, DN
        TStep = line[13]   # Tuning Step, e.g. 5.0
        Skip = line[14]    # <blank> S
        Power = line[15]   # E.g. "5.0W"
        Comment = line[16]

        if Duplex == '+':
            pass
        elif Duplex == '-':
            Offset = '-' + Offset
        else:
            Offset = 0

        txtone = rxtone = ''
        if Tone == '':
            pass
        elif Tone == 'Tone':
            txtone = Rtone
        elif Tone == 'TSQL':
            txtone = rxtone = Rtone
        elif Tone == 'DTCS':
            txtone = rxtone = 'D' + DtcsCode
        elif Tone == 'TSQL-R':
            rxtone = Rtone
        elif Tone == 'DTCS-R':
            rxtone = 'D' + DtcsCode
        elif Tone == 'Cross':
            if CrossMode == 'Tone->Tone':       # TX rToneFreq; RX cToneFreq
                txtone = Rtone
                rxtone = Ctone
            elif CrossMode == 'Tone->DTCS':     # TX rToneFreq; RX DtcsCode
                txtone = Rtone
                rxtone = 'D' + DtcsCode
            elif CrossMode == 'DTCS->Tone':     # TX DtcsCode; RX rToneFreq
                txtone = 'D' + DtcsCode
                rxtone = Rtone
            elif CrossMode == 'DTCS->':         # TX DtcsCode
                txtone = 'D' + DtcsCode
            elif CrossMode == '->DTCS':         # RX DtcsCode
                rxtone = 'D' + DtcsCode
            elif CrossMode == '->Tone':         # RX rToneFreq
                rxtone = Rtone
            elif CrossMode == 'DTCS->DTCS':
                txtone = rxtone = 'D' + DtcsCode

        wide = 'W'
        if Mode.startswith('W'):
            Mode = Mode[1:]
        elif Mode.startswith('N'):
            wide = 'N'
            Mode = Mode[1:]

        super().__init__(None, Chan, None, Freq, Offset,
            Name, Comment, txtone, rxtone, Mode, wide, Power)


    @staticmethod
    def parse(line, recFilter, cls=None):
        """Given a list, most likely provided by the csv module, return
        an RtSys object or None if the list can't be parsed."""
        if not cls: cls = Chirp
        if len(line) < 17: return None
        # line[2] is RX freq; if that's blank or not a number, then
        # the entire record is invalid
        if not line[2]:
            return None
        try:
            rxfreq = float(line[2])
        except Exception as e:
            return None
        try:
            return cls(line)
        except Exception as e:
            print("Failed to parse: ", line, file=sys.stderr)
            print(e, file=sys.stderr)
            return None


    # OUTPUT SECTION

    @staticmethod
    def header(csvout: csv.writer, recFilter):
        """Write out the header line for the CSV file."""
        csvout.writerow(["Location","Name","Frequency","Duplex","Offset","Tone",
            "rToneFreq","cToneFreq","DtcsCode","DtcsPolarity","RxDtcsCode",
            "CrossMode","Mode","TStep","Skip","Power","Comment","URCALL",
            "RPT1CALL","RPT2CALL","DVCODE"])

    @staticmethod
    def write(rec: channel.Channel, csvout: csv.writer, count: int, recFilter):
        """Write out one record. This may throw an exception if any of
        the ics-217 fields are not valid."""
        Chan = rec.Chan       # memory #, 0-based
        Name = rec.Name       # memory label
        Rxfreq = rec.Rxfreq       # RX freq
        Mode = rec.Mode
        Wide = rec.Wide
        Txfreq = rec.Txfreq       # RX freq
        Txtone = rec.Txtone
        Rxtone = rec.Rxtone

        if not Txtone: Txtone = 'CSQ'
        if not Rxtone or Rxtone.startswith('TSQ'): Rxtone = Txtone

        # Derived values
        Offset = float(Txfreq) - float(Rxfreq)
        if Txfreq == Rxfreq: Duplex = ''
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

        Comment = rec.Comment

        if Mode == 'FM':
            if Wide == 'N': Wide = 'NFM'
            else: Wide = 'FM'
        elif Mode == 'AM':
            if Wide == 'N': Wide = 'NAM'
            else: Wide = 'AM'
        elif Mode == 'D':
            Wide = 'DIG'
        else:
            Wide = Mode
        # TODO: other modes? e.g. "MF" appears in the ACS database

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


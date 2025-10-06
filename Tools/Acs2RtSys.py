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

import common
import ics217

class RtSys(object):
    """This is the "generic" RT Systems code. It generates output that
    both Yaesu FT-60 and QRZ-1 are happy with. Other radios might
    want something different; we may make subclasses for those
    radios at some later date."""
    # Output schema is based on the Yaesu FT-60, without bank select
    # TODO: RxTone, RxDCS. For now, always set to CSQ.

    @staticmethod
    def header(csvout: csv.writer, bank: int):
        """Write out the header line for the CSV file."""
        if bank is not None and bank >= 1 and bank <= 10:
            Banks = [f"Bank {i}," for i in range(1,11)]
        else:
            Banks = []
        csvout.writerow(["n","Receive Frequency","Transmit Frequency","Offset Frequency","Offset Direction","Operating Mode","Name","Show Name","Tone Mode","CTCSS","DCS","Skip","Step","Clock Shift","Tx Power","Tx Narrow","Pager Enable"] + Banks + ["Comment"])

    @staticmethod
    def write(icsrec: ics217, csvout: csv.writer, count: int, bank: int):
        """Write out one record. This may throw an exception if any of
        the ics-217 fields are not valid."""
        # There are some derived values here, so we compute them now.
        Chan = icsrec.Chan       # memory #, 0-based
        Config = icsrec.Config
        Name = icsrec.Name       # memory label
        Rxfreq = icsrec.Rxfreq       # RX freq
        Wide = icsrec.Txwid
        Txfreq = icsrec.Txfreq       # RX freq
        Txtone = icsrec.Txtone
        Rxtone = icsrec.Rxtone
        if bank is not None and bank >= 1 and bank <= 10:
            Banks = ["N,"] * 10
            Banks[bank-1] = 'Y,'
        else:
            Banks = []

        if not Txtone: Txtone = 'CSQ'
        if not Rxtone or Rxtone.startswith('TSQ'): Rxtone = Txtone

        # Derived values
        Offset = float(icsrec.Offset)
        if Config == 'Simplex' or Txfreq == Rxfreq:
            Offset_s = ''
        elif abs(Offset) < 1.0:
            Offset_s = "%.0f kHz" % (abs(Offset)*1000.)
        else:
            Offset_s = "%.4f MHz" % abs(Offset)

        if Config == 'Simplex' or Txfreq == Rxfreq:
            OpMode = "Simplex"
        elif Offset > 0:
            OpMode = "Plus"
        else:
            OpMode = "Minus"

        CTCSS = ''
        DCS = ''

        # There are nine possibilities for Txtone/Rxtone
        # This radio doesn't support different Tx/Rx tones.
        if Txtone == 'CSQ':
            ToneMode = 'None'   # Rx tone or DCS not supported
        elif Txtone[0] == 'D':
            DCS = Txtone[1:]
            if Rxtone.startswith('CSQ'):
                ToneMode = 'DCS'
            elif Rxtone[0] == 'D':
                ToneMode = 'DCS'    # TODO: should this be 'D Code'?
            else:
                CTCSS = Rxtone
                ToneMode = 'D Tone'
        else:
            CTCSS = Txtone
            if Rxtone.startswith('CSQ'):
                ToneMode = 'Tone'   # Most common case
            elif Rxtone[0] == 'D':
                DCS = Rxtone[1:]
                ToneMode = 'T DCS'
            else:
                ToneMode = 'T Sql'

        Comment = icsrec.getComment()

        # <ch>                  1-1000                  column header is blank, column ignored
        # Receive Frequency     146.96000
        # Transmit Frequency    146.36000
        # Offset Frequency      600 kHz | 5.00000 MHz | (blank)
        # Offset Direction      Minus | Plus | Simplex
        # Operating Mode        FM | AM
        # Name                  e.g. PSRG
        # Show Name             Y
        # Tone Mode             None, Tone, DCS (others ignored for now)
        # CTCSS                 103.5
        # DCS                   023
        # Skip                  Scan
        # Step                  e.g. "5 kHz"
        # Clock Shift           N
        # Tx Power              High | Low
        # Tx Narrow             Y | N
        # Pager Enable          N
        # Comment               any string

        Wide = 'Y' if Wide=="N" else 'N'
        csvout.writerow([count, Rxfreq, Txfreq, Offset_s, OpMode, 'Auto', Name, 'Y' if Name else 'N', ToneMode, CTCSS, DCS, 'Scan', 'Auto', 'N', 'High', Wide, 'N'] + Banks + [Comment])

if __name__ == '__main__':
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    try:
      sys.exit(common.main(RtSys))
    except KeyboardInterrupt as e:
      print(file=sys.stderr)
      sys.exit(1)

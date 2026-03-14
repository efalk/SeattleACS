#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Convert CSV file from ACS 217 spreadsheet to format RT Systems uses for FT-60

import csv
import sys

import channel

class RtSys(channel.Channel):
    """This is the "generic" RT Systems code. It generates output that
    both Yaesu FT-60 and QRZ-1 are happy with. Other radios might
    want something different; we may make subclasses for those
    radios at some later date."""
    # Output schema is based on the Yaesu FT-60, with optional bank select
    # TODO: RxTone, RxDCS. For now, always set to CSQ.

    # INPUT SECTION

    hasBanks = False

    @staticmethod
    def probe(line: list):
        """Examine line to see if the input is in RT Systems format. Return
        None if not. Anything else is true."""
        isRt = len(line) >= 8 and \
            line[1] == "Receive Frequency" and \
            line[2] == "Transmit Frequency" and \
            line[3] == "Offset Frequency" and \
            line[4] == "Offset Direction" and \
            line[5] == "Operating Mode" and \
            line[6] == "Name" and \
            line[7] == "Show Name"
        if isRt and len(line) >= 18 and line[17] == "Bank 1":
            RtSys.hasBanks = True
        return isRt

    def __init__(this, recFilter: dict, line):
        """Create an RtSys object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""
        chan = line[0]
        rxfreq = line[1]
        txfreq = line[2]
        mode = line[5]
        name = line[6]
        toneMode = line[8]
        ctcss = line[9]
        dcs = line[10]
        power = line[14]
        narrow = line[15]
        if RtSys.hasBanks:
            banks = line[17:27]
            comment = line[27]
        else:
            banks = None
            comment = line[17]

        txtone = rxtone = ''
        if toneMode == 'None':
            pass
        elif toneMode == 'Tone':
            txtone = ctcss
        elif toneMode == 'T Sql':
            txtone = rxtone = ctcss
        elif toneMode == 'Rev CTCSS':   # Not supported
            pass
        elif toneMode == 'DCS':
            txtone = 'D' + dcs
        elif toneMode == 'D Code':      # Not sure what this is
            pass
        elif toneMode == 'T DCS':
            txtone = ctcss; rxtone = 'D' + dcs
        elif toneMode == 'D Tone':
            txtone = 'D' + DCS; rxtone = ctcss

        super().__init__(recFilter, None, chan, txfreq, rxfreq, None, name, comment,
            txtone, rxtone, mode, 'N' if narrow == 'Y' else 'W', power)

        this.banks = banks

    @staticmethod
    def parse(line, recFilter, cls=None):
        """Given a list, most likely provided by the csv module, return
        an RtSys object or None if the list can't be parsed."""
        if not cls: cls = RtSys
        if len(line) < 18: return None
        # line[1] is RX freq; if that's blank or not a number, then
        # the entire record is invalid
        if not line[1]:
            return None
        try:
            rxfreq = float(line[1])
            rval = cls(recFilter, line)
            return rval if rval.testFilter(recFilter) else None
        except Exception as e:
            print("Failed to parse: ", line, file=sys.stderr)
            print(e, file=sys.stderr)
            return None




    # OUTPUT SECTION

    @staticmethod
    def header(csvout: csv.writer, recFilter):
        """Write out the header line for the CSV file."""
        banks = recFilter.get('banks')
        if banks:
            Banks = [f"Bank {i}," for i in range(1,11)]
        else:
            Banks = []
        csvout.writerow(["n","Receive Frequency","Transmit Frequency","Offset Frequency","Offset Direction","Operating Mode","Name","Show Name","Tone Mode","CTCSS","DCS","Skip","Step","Clock Shift","Tx Power","Tx Narrow","Pager Enable"] + Banks + ["Comment"])

    @staticmethod
    def write(rec: channel.Channel, csvout: csv.writer, count: int, recFilter):
        """Write out one record. This may throw an exception if any of
        the ics-217 fields are not valid."""
        # There are some derived values here, so we compute them now.
        Chan = rec.Chan       # memory #, 0-based
        Name = rec.Name       # memory label
        Rxfreq = rec.Rxfreq       # RX freq
        Wide = rec.Wide
        Txfreq = rec.Txfreq       # RX freq
        Txtone = rec.Txtone
        Rxtone = rec.Rxtone
        Comment = rec.Comment
        Skip = '' if rec.Skip else 'Scan'

        derived = RtSys.Derived(rec, recFilter)
        Txtone = derived.Txtone
        Rxtone = derived.Rxtone
        Offset_s = derived.Offset
        OpMode = derived.OpMode
        ToneMode = derived.ToneMode
        banks = derived.banks

        CTCSS = derived.CTCSS
        DCS = derived.DCS

        # <ch>                  1-1000                  column header is blank, column ignored
        # Receive Frequency     146.96000
        # Transmit Frequency    146.36000
        # Offset Frequency      600 kHz | 5.00000 MHz | (blank)
        # Offset Direction      Minus | Plus | Simplex
        # Operating Mode        FM | AM; RtSystems also accepts "Auto".
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
        csvout.writerow([count, Rxfreq, Txfreq, Offset_s, OpMode, 'Auto', Name, 'Y' if Name else 'N', ToneMode, CTCSS, DCS, Skip, 'Auto', 'N', 'High', Wide, 'N'] + banks + [Comment])


    class Derived:
        """Represents the derived values used by RT Systems"""
        def __init__(self, rec: channel.Channel, recFilter):
            """Contains the following derived values:
                Txtone
                Rxtone
                Offset: e.g. "n.nnnn MHz" or "nnn kHz" or ''
                OpMode: "Simple", "Plus", "Minus"
                ToneMode: e.g. "None", "T Sql", "DCS", "D Tone", etc.
                CTCSS: e.g. "103.5"
                DCS: e.g. "D23"
            self.CTCSS = CTCSS
            self.DCS = DCS
            """
            # There are some derived values here, so we compute them now.
            Rxfreq = rec.Rxfreq
            Txfreq = rec.Txfreq
            Txtone = rec.Txtone
            Rxtone = rec.Rxtone

            if not Txtone: Txtone = 'CSQ'
            if not Rxtone or Rxtone.startswith('TSQ'): Rxtone = Txtone

            # Derived values
            Offset = float(rec.Offset)
            if Txfreq == Rxfreq:
                Offset_s = ''
            elif abs(Offset) < 1.0:
                Offset_s = "%.0f kHz" % (abs(Offset)*1000.)
            else:
                Offset_s = "%.4f MHz" % abs(Offset)

            if Txfreq == Rxfreq:
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

            banklist = recFilter.get('banks')
            if banklist:
                banks = ['N']*10
                try:
                    for bank in banklist.split(','):
                        banks[int(bank)-1] = 'Y'
                except exception as e:
                    print(e)
                    banks = []
            else:
                banks = []

            self.Txtone = Txtone
            self.Rxtone = Rxtone
            self.Offset = Offset_s
            self.OpMode = OpMode
            self.ToneMode = ToneMode
            self.CTCSS = CTCSS
            self.DCS = DCS
            self.banks = banks

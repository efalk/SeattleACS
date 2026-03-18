#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Parse lines from the ACS ICS-217 spreadsheet, e.g. W7ACS_ICS-217A_20230505.csv
# Likely only works for ICS-217 spreadsheets from ACS.
#
# Typical usage:
#
#    from ics217 import ics217
#
#    reader = csv.reader(sys.stdin)
#
#    for l in reader:
#        acsRec = ics217.parse(l)
#        if not acsRec:
#           continue            # this is fine; not all records contain data

# Schema (ACS 217):
#   0 CH#, e.g. "V01"
#   1 config: "Repeater" | "Simplex"
#   2 name, displayed by radio, e.g. "V01PSR"
#   3 comment, e.g. "PSRG" or "KC ARES Tiger"
#   4 Rx freq
#   5 narrow/wide: W, N
#   6 RX tone: "CSQ" or a frequency
#   7 Tx Freq, typically for repeater uplink
#   8 Tx narrow/wide: W, N
#   9 TX tone: "CSQ" or a Frequency e.g. 103.5
#  10 Mode: A, F, MF, MP, D; almost always "A"
#  11 Remarks, e.g. "Tactical; W7DX" or "simplex calling"


import re
import sys

import channel
from channel import csvget
from channel import callsign_re
from channel import callsign_l_re

class ics217(channel.Channel):
    """Represents one ACS ICS217 record. See above for list of fields."""

    # INPUT SECTION

    @staticmethod
    def probe(line: list):
        """Examine line to see if the input is in ACS format. Return
        None if not. Anything else is true."""
        return len(line) >= 11 and \
            line[2] == "Display Name" and \
            line[3] == "Channel/Repeater Name" and \
            line[4] == "RX Freq" and \
            line[5] == "N/W" and \
            line[7] == "TX Freq"

    def __init__(this, recFilter: dict, line):
        """Create an ics217 object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""
        chan, config, name, comment, rxfreq, wide, rxtone, txfreq, \
            txwid, txtone, mode, remarks = line[:12]
        # Just a quick sanity check
        if config == 'Simplex' and txfreq != rxfreq:
            print(f'Warning: Channel {chan}, {name}, Simplex rxfreq {rxfreq} does not match txfreq {txfreq}', file=sys.stderr)
            txfreq = rxfreq
        super().__init__(recFilter, None, chan, txfreq, rxfreq, None,
            name, comment, txtone, rxtone, mode, wide, "High")
        this.Config = config
        this.Txwid = txwid
        this.Remarks = remarks
        # For Mode "A", guess AM vs FM
        # Otherwise, all ACS frequencies are FM
        if this.Mode == 'A':
            this.Mode = 'FM' if float(this.Rxfreq) >= 50.0 else 'AM'
        elif this.Mode != 'D':
            this.Mode = 'FM'
        this.Comment = this.getComment()
        if recFilter.get('longName'):
            this.Name = this.getName2()

    def __repr__(this):
        return f'''ics217({repr(this.Chan)}, {repr(this.Config)}, {repr(this.Name)}, {repr(this.Comment)}, {repr(this.Rxfreq)}, {repr(this.Wide)}, {repr(this.Rxtone)}, {repr(this.Txfreq)}, {repr(this.Txwid)}, {repr(this.Txtone)}, {repr(this.Mode)}, {repr(this.Remarks)})'''

    def __str__(this):
        return f'''{csvget(this.Chan)},{csvget(this.Config)},{csvget(this.Name)},{csvget(this.Comment)},{csvget(this.Rxfreq)},{csvget(this.Wide)},{csvget(this.Rxtone)},{csvget(this.Txfreq)},{csvget(this.Txwid)},{csvget(this.Txtone)},{csvget(this.Mode)},{csvget(this.Remarks)}'''

    def getComment(this):
        """Return a reasonable comment for this item; incorporate the
        channel id, comment, and remarks."""
        try:
            c = []
            if this.Chan not in this.Name: c.append(this.Chan + ': ')
            if this.Comment and this.Remarks:
                c.extend([this.Comment, '; ', this.Remarks])
            elif this.Comment:
                c.append(this.Comment)
            elif this.Remarks:
                c.append(this.Remarks)
            return ''.join(c)
        except Exception as e:
            print(this, e, file=sys.stderr)
            return this.Comment

    def getName(this):
        """Override superclass, we'll get to this later."""
        return this.Name

    def getName2(this):
        """Return a reasonable name for this item; incorporate the
        name, comment, and remarks."""
        # Let's see if we can find a call sign buried in the comment or
        # remarks.
        # Call this after calling getComment()
        # If the name is entirely digits, but a callsign can be found in the
        # comment, use that instead.
        if this.Name.isdigit():
            mo = callsign_re.search(this.Comment)
            if mo:
                this.Name = mo.group()
        name = super().getName()
        # ACS 217 entries usually contain the channel # as part of the name.
        # If not, add it.
        if not name.startswith(this.Chan):
            name = this.Chan + ' ' + name
        return name

    @staticmethod
    def parse(line, recFilter, cls=None):
        """Given a list, most likely provided by the csv module, return
        an ics217 object or None if the list can't be parsed."""
        if not cls: cls = ics217
        prefixes = recFilter.get('bands')
        newEntries = recFilter.get('newEntries', False)
        regex = recFilter.get('regex')
        if len(line) < 12: return None
        # line[4] is RX freq; if that's blank, then the entire record is invalid
        if not line[0] or (prefixes and line[0][0] not in prefixes) or not line[4]:
            return None
        if not regex and line[0].endswith('N') ^ newEntries:
            return None
        if regex and not regex.match(line[0]):
            return None
        try:
            return cls(recFilter, line)
        except Exception as e:
            print("Failed to parse: ", line, file=sys.stderr)
            print(e, file=sys.stderr)
            return None



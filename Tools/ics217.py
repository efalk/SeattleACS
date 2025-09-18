#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Parse lines from the ACS ICS-217 spreadsheet, e.g. W7ACS_ICS-217A_20230505.csv
# Likely only works for ICS-217 spreadsheets from ACS.
#
# Typical usage:
#
#    import ics217
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
#  10 Mode: A, MF, MP, D; almost always "A"
#  11 Remarks


import sys

import channel
from channel import csvget

class ics217(channel.Channel):
    """Represents one ICS217 record. See above for list of fields."""
    def __init__(this, line):
        """Create an ics217 object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""
        this.Group = None
        this.Chan = line[0]     # memory #, 0-based
        this.Config = line[1]
        this.Name = line[2]     # memory label
        this.Comment = line[3]
        this._Rxfreq = line[4]     # RX freq
        this.Wide = line[5]
        this.Rxtone = line[6]
        this._Txfreq = line[7]     # TX freq
        this.Txwid = line[8]
        this.Txtone = line[9]
        this.Mode = line[10]
        this.Remarks = line[11]
        this._Offset = None

    def __repr__(this):
        return f'''ics217({repr(this.Chan)}, {repr(this.Config)}, {repr(this.Name)}, {repr(this.Comment)}, {repr(this.Rxfreq)}, {repr(this.Wide)}, {repr(this.Rxtone)}, {repr(this.Txfreq)}, {repr(this.Txwid)}, {repr(this.Txtone)}, {repr(this.Mode)}, {repr(this.Remarks)})'''

    def __str__(this):
        return f'''{csvget(this.Chan)},{csvget(this.Config)},{csvget(this.Name)},{csvget(this.Comment)},{csvget(this.Rxfreq)},{csvget(this.Wide)},{csvget(this.Rxtone)},{csvget(this.Txfreq)},{csvget(this.Txwid)},{csvget(this.Txtone)},{csvget(this.Mode)},{csvget(this.Remarks)}'''

    def getComment(this):
        """Return a reasonable comment for this item"""
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
            raise

def parse(line, prefixes='VULTDH', newEntries=False, cls=None):
    """Given a list, most likely provided by the csv module, return
    an ics217 object or None if the list can't be parsed."""
    if not cls: cls = ics217
    if len(line) < 12: return None
    # line[4] is RX freq; if that's blank, then the entire record is invalid
    if not line[0] or (prefixes and line[0][0] not in prefixes) or not line[4]:
        return None
    if line[0].endswith('N') ^ newEntries:
        return None
    try:
        return cls(line)
    except Exception as e:
        print("Failed to parse: ", line, file=sys.stdout)
        print(e, file=sys.stdout)
        return None



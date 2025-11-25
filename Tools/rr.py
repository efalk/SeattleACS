#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Parse lines from the Repeater Roundabout spreadsheet.
#
# Typical usage:
#
#    from rr import rr
#
#    reader = csv.reader(sys.stdin)
#
#    for l in reader:
#        rec = rr.parse(l)
#        if not rec:
#           continue            # this is fine; not all records contain data

# Schema:
#   0 RR#, starts with 1
#   1 Callsign, e.g. WW7PSR
#   2 Output (rxfreq) (MHz), e.g. 146.96
#   3 Offset (MHz), e.g. -0.6
#   4 Tone (Hz), e.g. 103.5
#   5 RepeaterBook ID, often blank
#   6 Location, e.g. "Capitol Hill, Seattle, WA"
#   7 Mode, FM, NBFM, etc.
#   8 Group, e.g. Snohomish County Auxiliary Communications Service
#   9 Website, e.g. https://wa7dem.info
#  10 RepeaterBook State ID, typically blank
#  11 Latitude, e.g. 47.75619
#  12 Longitude, e.g. -122.34575


import sys

import channel
from channel import csvget

class rr(channel.Channel):
    """Represents one Repeater Roundabout record. See above for list of fields."""
    def __init__(this, line):
        """Create an rr object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""
        mode = line[7]
        wide = 'W'
        if mode.startswith('NB'):
            mode = mode[2:]
            wide = 'N'
        super().__init__(None, line[0], None, line[2], line[3],
            line[1], line[5], line[4], 'CSQ', mode, wide, 'high')
        this.Remarks = line[6]
        this.Group = line[8]
        this.Website = line[9]
        this.State = line[10]
        this.Lat = line[11]
        this.Lon = line[12]
        this.Comment = this.getComment()

    def __repr__(this):
        mode = this.Mode if this.Wide == 'W' else 'NB'+this.Mode
        return f'''rr({repr(this.Chan)}, {repr(this.Name)}, {repr(this.Txfreq)}, {repr(this.Offset)}, {repr(this.Txtone)}, {this.Comment}, {this.Remarks}, {mode}, {repr(this.Group)}, {repr(this.Website)}, {repr(this.State)}, {repr(this.Lat)}, {repr(this.Lon)})'''

    def __str__(this):
        mode = this.Mode if this.Wide == 'W' else 'NB'+this.Mode
        return f'''{csvget(this.Chan)}, {csvget(this.Name)}, {csvget(this.Txfreq)}, {csvget(this.Offset)}, {csvget(this.Txtone)}, {csvget(this.Comment)}, {csvget(this.Remarks)}, {mode}, {csvget(this.Group)}, {csvget(this.Website)}, {csvget(this.State)}, {csvget(this.Lat)}, {csvget(this.Lon)}'''

    def getComment(this):
        """Return a reasonable comment for this item"""
        try:
            c = []
            if this.Comment: c.append(this.Comment)
            if this.Remarks: c.append(this.Remarks)
            return ';'.join(c)
        except Exception as e:
            print(this, e, file=sys.stderr)
            raise

    @staticmethod
    def parse(line, recFilter, cls=None):
        """Given a list, most likely provided by the csv module, return
        an rr object or None if the list can't be parsed."""
        if not cls: cls = rr
        if len(line) < 13: return None
        # line[0] is channel number; if missing or not a number, reject
        if not line[0].isdigit(): return None
        regex = recFilter.get('regex')
        if regex and not regex.match(line[1]):
            return None
        try:
            return cls(line)
        except Exception as e:
            print("Failed to parse: ", line, file=sys.stderr)
            print(e, file=sys.stderr)
            return None

def strNeg(s):
    return s[1:] if s[0] == '-' else '-'+s

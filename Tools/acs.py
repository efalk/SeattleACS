#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Parse lines from the ACS 217 spreadsheet, e.g. W7ACS_ICS-217A_20230505.csv
#
# Typical usage:
#
#    import acs
#
#    reader = csv.reader(sys.stdin)
#
#    for l in reader:
#        acsRec = acs.parse(l)
#        if not acsRec:
#           continue            # this is fine; not all records contain data

# Schema (ACS 217):
#   0 CH#, e.g. "V01"
#   1 config: Repeater, Simplex
#   2 name
#   3 comment
#   4 rx freq
#   5 narrow/wide: W, N
#   6 RX tone: "CSQ" or a frequency
#   7 Tx Freq
#   8 narrow/wide: W, N
#   9 TX tone: "CSQ" or a Frequency e.g. 103.5
#  10 Mode: A, MF, MP, D; almost always "A"
#  11 Remarks


import sys

class Acs(object):
    def __init__(this, line):
        """Create an Acs object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""
        this.Chan = line[0]     # memory #, 0-based
        this.Config = line[1]
        this.Name = line[2]     # memory label
        this.Comment = line[3]
        this.Rxfreq = line[4]     # RX freq
        this.Rxwid = line[5]
        this.Rxtone = line[6]
        this.Txfreq = line[7]     # RX freq
        this.Txwid = line[8]
        this.Txtone = line[9]
        this.Mode = line[10]
        this.Remarks = line[11]
    def __repr__(this):
        return f'''Acs("{this.Chan}", "{this.Config}", "{this.Name}", "{this.Comment}", "{this.Rxfreq}", "{this.Rxwid}", "{this.Rxtone}", "{this.Txfreq}", "{this.Txwid}", "{this.Txtone}", "{this.Mode}", "{this.Remarks}"'''


def parse(line):
    """Given a list, most likely provided by the csv module, return an Acs object or
    None if the list can be parsed."""
    if len(line) < 12: return None
    if not line[0] or line[0][0] not in "VUL": return None
    try:
        return Acs(line)
    except Exception as e:
        print("Failed to parse: ", line, file=sys.stdout)
        print(e, file=sys.stdout)
        return None

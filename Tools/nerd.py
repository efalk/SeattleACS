#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Parse lines from the New England Repeater Directory
# https://www.nerepeaters.com/
#
# Typical usage:
#
#    from nerd import NERD
#
#    reader = csv.reader(sys.stdin)
#
#    for l in reader:
#        acsRec = NERD.parse(l)
#        if not acsRec:
#           continue            # this is fine; not all records contain data

# Schema:
#   0 FREQ             29.6800     # repeater output, i.e. downlink, i.e. radio input
#   1 OFFSET           +/-/*/S     # See below for standard values
#   2 ST               MA
#   3 CITY             Vernon
#   4 MODES            FM, NFM, DMR, D-STAR, NXDN, P25, YSF (Yaesu Fusion).
#   5 CALL             W7RNB; includes url to sponsor if available
#   6 CODE IN          107.2, CC4, NAC 293, etc. Blank for CSQ
#   7 CODE OUT         ditto
#   8 STATUS           usually blank; may be Local, OFF, etc.
#   9 COUNTY           Middlesex
#  10 ?                Not clear; usually blank, sometimes a number like "4136"
#  11 VOIP             e.g. "E 4260", "A 2350", etc. Usually blank
#  12 LINKS/COMMENTS   Any text, may contain input frequency if OFFSET is '*'
#  13 Last Update      yyyy/mm/dd or blank

# Note for that the database shown when you click a band on the web site,
# the field order is FREQ, OFS, ST, CITY, CALL, MODE, CODE IN, CODE OUT,
#  STATUS, COUNTY, VOIP, LINKS/COMMENTS, Last Update.
# For the raw database, the order is as shown above.

# This database assumes standard offsets and so only lists +/-. If a repeater
# uses a nonstandard offset, then OFS willbe '*' and the uplink frequency will
# Be listed in the comment. Look for '*Input: ddd.ddd'
# Standard offsets are:
#  10M = 100 kHz
#  6M = 1 MHz
#  2M = 600 kHz
#  222MHz = 1.6 MHz
#  440 MHz = 5 MHz
#  902 MHz = 25 MHz
#  1.2 GHz = 12 MHz

from decimal import Decimal
import re
import sys

import channel

_modenames = ('NFM', 'FM', 'NAM', 'AM', 'DMR', 'D-STAR', 'NXDN', 'P25', 'YSF')

class NERD(channel.Channel):
    """Represents one ACS ICS217 record. See above for list of fields."""

    # INPUT SECTION (there is no output section)

    cache = []        # Optional cached first record

    @staticmethod
    def probe(line: list):
        """Examine line to see if the input is in Chirp format. Return
        None if not. Anything else is true."""
        # OK, this is kind of ugly. As downloaded from NERD, the
        # database has no header line. The best we can do is examine
        # the first line of the database and see if it's reasonably
        # parseable as an entry from the NERD database. If it is, then
        # we have to hold on to it so that the parse() function can
        # return it later.
        #
        # Rules: First field is a float. Second field is empty or one of
        # +/-/*. Third field is empty or exactly two capital letters.

        if len(line) < 13:
            return None

        try:
            freq = float(line[0])
        except:
            return None

        if line[1] not in ('','+','-','*'):
            return None

        if not re.match('([A-Z][A-Z])?$', line[2]):
            return None

        NERD.cache = NERD.parse(line, {})
        return not not NERD.cache

    def __init__(this, recFilter: dict, line: list, mode: str = None):
        """Create a NERD object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""
        # Unpack the line
        # Remember that freq is the downlink frequency
        # Don't have high hopes here; the input database is a clusterfuck
        # of random formatting, such as mode="P25YSFD-STARM17NXDNDMR"
        rxfreq, ofs, st, city, modes, call, codeIn, codeOut, status, _, _, _, \
            comment = line[:13]

        txfreq = _getTxfreq(rxfreq, ofs, comment)

        # parse() will figure out the mode and pass it in for most cases.
        if not mode:
            if not modes:
                mode = 'FM' if float(rxfreq) > 100.0 else 'AM'
            else:
                mode = modes.split('/')[0]

        codeIn = _getCode(mode, codeIn)
        codeOut = _getCode(mode, codeOut)

        wide = 'W'
        if mode in ('NFM','NAM'):
            wide = 'N'
            mode = mode[1:]

        comment = NERD.getComment(comment, city, st, status)

        super().__init__(recFilter, None, None, txfreq, rxfreq, None,
            call, comment, codeIn, codeOut, mode, wide, None)

    @staticmethod
    def getComment(comment, city, st, status):
        """Return a reasonable comment for this item; incorporate the
        comment, city, and state"""
        c = []
        if comment:
            c.append(comment)
        if st not in comment:
            try:
                if city:
                    if comment:
                        c.append('; ')
                    c.append(city)
                    if st:
                        c.append(', ')
                        c.append(st)
            except Exception as e:
                print(this, e, file=sys.stderr)
        if status:
            c.append(' (' + status + ')')
        return ''.join(c)

    @staticmethod
    def parse(line, recFilter, cls=None):
        """Given a list, most likely provided by the csv module, return
        a list of NERD objects or None if the record can't be parsed. Note
        that this function may return a list of results for multi-mode
        repeaters."""
        if not cls: cls = NERD

        rval = NERD.cache
        NERD.cache = []

        # First chance to filter cached items
        if rval:
            rval = list(filter(lambda r: r.testFilter(recFilter), rval))

        # line[0] is RX freq; if that's blank, then the entire record is invalid
        if len(line) < 13 or not line[0]:
            return rval
        try:
            rxfreq = float(line[0])
        except Exception as e:
            return rval

        # See what modes this repeater supports
        # If there are exceptions here, they will bubble up and
        # be reported as appropriate.
        # example: "P25YSFD-STARM17NXDNDMR"
        modestr = line[4].strip()
        modes = []
        if modestr:
            for name in _modenames:
                if name in modestr:
                    modes.append(name)
                    if name == modestr: break
            if 'FM' in modes and 'NFM' in modes: modes.remove('FM')
            if 'AM' in modes and 'NAM' in modes: modes.remove('AM')
        if not modes:
            rec = cls(recFilter, line)
            if rec.testFilter(recFilter):
                rval.append(rec)
        else:
            for mode in modes:
                rec = cls(recFilter, line, mode)
                if rec.testFilter(recFilter):
                    rval.append(rec)
        return rval

_input_re = re.compile('\*Input: (\d+\.\d*)')

def _getTxfreq(rxfreq, ofs, comment):
    """Get the txfreq that pairs with this offset flag. May need
    to search the comment for this information."""
    if not ofs or ofs == 'S':   # Simplex
        return rxfreq
    if ofs in '+-':
        offset = _getStandardOffset(float(rxfreq))
        if ofs == '-': offset = -offset
        return str(Decimal(rxfreq) + offset)
    if ofs == '*':          # non-standard; extract from comment
        mo = _input_re.search(comment)
        if mo:
            return mo.group(1)
    return rxfreq

def _getStandardOffset(rxfreq: float) -> float:
    """Make a best guess as to the appropriate offset frequency."""
    if rxfreq < 30.0: return Decimal('0.1')      # 10m and lower
    if rxfreq < 100.0: return Decimal('1.0')     # 6m
    if rxfreq < 150.0: return Decimal('0.6')     # 2m
    if rxfreq < 300.0: return Decimal('1.6')     # 1.25m
    if rxfreq < 500.0: return Decimal('5.0')     # 70cm and gmrs
    if rxfreq < 1000.0: return Decimal('25.0')   # 902 MHz
    return Decimal('12.0')                       # everything beyond

_re_ctcss = re.compile('\d+\.\d|D\d\d\d')
_re_dmr = re.compile('CC\d+')
_re_p25 = re.compile('NAC ?\d+')
_re_nxdn = re.compile('RAN\d+')
_mode_res = {'AM':_re_ctcss, 'NAM':_re_ctcss, 'FM':_re_ctcss, 'NFM':_re_ctcss,
    'DMR':_re_dmr, 'P25':_re_p25, 'NXDN':_re_nxdn}

def _getCode(mode: str, codes: str) -> str:
    """Examine the mode and codes string, and extract the code
    relevant for that mode."""
    # MODES: FM, NFM, DMR, D-STAR, NXDN, P25, YSF (Yaesu Fusion).
    if not mode or not codes: return ''
    if mode in _mode_res:
        mo = _mode_res[mode].search(codes)
        return mo.group() if mo else ''
    # Last resort, if there's only one subfield in codes, just
    # return that, else ''
    return codes if '/' not in codes else ''

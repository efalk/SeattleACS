#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Parse lines from the WWARA spreadsheet, e.g. WWARA-rptrlist-20260311.csv
# Western Washington Amateur Radio Association
# https://www.wwara.org/coordinations/coordination-data-files/
#
# Typical usage:
#
#    from wwara import WWARA
#
#    reader = csv.reader(sys.stdin)
#
#    for l in reader:
#        rec = WWARA.parse(l)
#        if not rec:
#           continue            # this is fine; not all records contain data

# Schema:
#  FC_RECORD_ID     1005
#  SOURCE           WWARA
#  OUTPUT_FREQ      29.6800     # repeater output, i.e. downlink, i.e. radio input
#  INPUT_FREQ       29.5800
#  STATE            WA
#  CITY             Lookout Mtn
#  LOCALE           WASHINGTON- NORTHWEST
#  CALL             W7RNB
#  SPONSOR          5CountyEmCommGrp
#  CTCSS_IN         110.9
#  CTCSS_OUT        110.9
#  DCS_CDCSS
#  DTMF
#  LINK
#  FM_WIDE          Y
#  FM_NARROW        N
#  DSTAR_DV         N
#  DSTAR_DD         N
#  DMR              N
#  DMR_COLOR_CODE
#  FUSION           N
#  FUSION_DSQ
#  P25_PHASE_1      N
#  P25_PHASE_2      N
#  P25_NAC
#  NXDN_DIGITAL     N
#  NXDN_MIXED       N
#  NXDN_RAN
#  ATV              N
#  DATV             N
#  RACES            N
#  ARES             N
#  WX               N
#  URL
#  LATITUDE         48.6875
#  LONGITUDE        -122.3625
#  EXPIRATION_DATE  2026-02-28
#  COMMENT




import sys

import channel
from channel import csvget

class WWARA(channel.Channel):
    """Represents one WWARA record. See above for list of fields."""

    # INPUT SECTION (there is no output section)

    @staticmethod
    def probe(line: list):
        """Examine line to see if the input is in Chirp format. Return
        None if not. Anything else is true."""
        return len(line) >= 38 and \
            line[0] == "FC_RECORD_ID" and \
            line[1] == "SOURCE" and \
            line[2] == "OUTPUT_FREQ" and \
            line[3] == "INPUT_FREQ"

    def __init__(this, recFilter: dict, line):
        """Create a WWARA object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""
        # Unpack the line
        fc_record_id, source, output_freq, input_freq, state, city, \
            locale, call, sponsor, ctcss_in, ctcss_out, dcs_cdcss, dtmf, \
            link, fm_wide, fm_narrow, dstar_dv, dstar_dd, dmr, \
            dmr_color_code, fusion, fusion_dsq, p25_phase_1, p25_phase_2, \
            p25_nac, nxdn_digital, nxdn_mixed, nxdn_ran, atv, datv, \
            races, ares, wx, url, latitude, longitude, expiration_date, comment \
                = line[:38]

        mode = 'FM' if float(input_freq) > 100.0 else 'AM'
        wide = 'W'
        if dstar_dv == 'Y' or dstar_dd == 'Y': mode = 'DSTAR'
        elif dmr == 'Y': mode = 'DMR'
        elif nxdn_digital == 'Y' or nxdn_mixed == 'Y': mode = 'NXDN'
        elif p25_phase_1 == 'Y' or p25_phase_2 == 'Y': mode = 'P25'
        elif fusion == 'Y': mode = 'FUSION'
        elif fm_wide == 'Y': wide = 'W'
        elif fm_narrow == 'Y': wide = 'N'
        wide = 'W' if fm_wide == 'Y' or fm_narrow == '' else 'N'
        comment = WWARA.getComment(fc_record_id, city, state, call, races, ares, url,
            latitude, longitude, comment)

        super().__init__(recFilter, None, None, input_freq, output_freq, None,
            call, comment, ctcss_out, ctcss_in, mode, wide, "High")

    @staticmethod
    def getComment(fc_record_id, city, state, call, races, ares, url, latitude, longitude, comment):
        """Return a reasonable comment for this item; incorporate the
        city, state, comment, and other fields."""
        try:
            c = []
            if city: c.append(city); c.append(', ')
            if state: c.append(state); c.append(' ')
            if races != 'N' or ares != 'N':
                ra = []
                if races != 'N': ra.append("RACES")
                if ares != 'N': ra.append("ARES")
                c.append('('+','.join(ra)+')')
            if url: c.append(url)
            if latitude or longitude:
                c.append('; ')
                if latitude: c.append(latitude)
                c.append(',')
                if longitude: c.append(longitude)
            if comment:
                c.append('; ')
                c.append(comment)
            return ''.join(c)
        except Exception as e:
            print(this, e, file=sys.stderr)
            return comment

    @staticmethod
    def parse(line, recFilter, cls=None):
        """Given a list, most likely provided by the csv module, return
        a list of WWARA objects or None if the record can't be parsed. Note
        that this function may return a list of results for multi-mode
        repeaters."""
        if not cls: cls = WWARA
        if len(line) < 38: return None
        # line[3] is RX freq; if that's blank, then the entire record is invalid
        if not line[3]:
            return None
        try:
            rxfreq = float(line[3])
        except Exception as e:
            return None
        rval = []
        # See what modes this repeater supports
        _, _, _, _, _, _, _, _, _, _, _, _, _, \
            _, fm_wide, fm_narrow, dstar_dv, dstar_dd, dmr, \
            dmr_color_code, fusion, _, p25_phase_1, p25_phase_2, \
            p25_nac, nxdn_digital, nxdn_mixed, nxdn_ran, atv, datv, \
            _, _, _, _, _, _, _, _ = line[:38]

        def addRecord(rval, flags, mode):
            if 'Y' in flags:
                try:
                    rec = cls(recFilter, line)
                    if rec.testFilter(recFilter):
                        rec.Mode = mode
                        rval.append(rec)
                        return True
                except Exception as e:
                    print("Failed to parse: ", line, file=sys.stderr)
                    print(e, file=sys.stderr)
                return False

        addRecord(rval, fm_wide + fm_narrow, 'FM')
        addRecord(rval, dstar_dv + dstar_dd, 'DSTAR')
        if addRecord(rval, dmr, 'DMR'):
            rval[-1].Comment += f' (color={dmr_color_code})'
        # fusion, _,
        if addRecord(rval, p25_phase_1 + p25_phase_2, 'P25'):
            rval[-1].Comment += f' (nac={p25_nac})'
        addRecord(rval, nxdn_digital + nxdn_mixed, 'NXDN')
        # nxdn_ran
        addRecord(rval, atv, 'ATV')
        addRecord(rval, datv, 'DATV')
        return rval



#!/usr/bin/env python3
# -*- coding: utf8 -*-

usage = """Convert CSV file from ACS 217 spreadsheet to format RT Systems uses

  Acs2RtSys.py < W7ACS_ICS-217A_20240131.csv > ACS_RT.csv

  Options:
        -b <band>       Any combination of the letters VULTD
                                V = VHF (2m band)
                                U = UHF (70cm band)
                                L = Low frequency (6m band)
                                T = 220 MHz band (1.25m band)
                                D = digital
                            Default is VU
        -s <n>          Start numbering at <n>; default is 1

Currently generates output csv files that have been tested with Yaesu FT-60,
Yaesu FT-5, and Explorer QRZ-1. These files should work with RT Systems software
for any device, but if not, please contact Ed Falk, KK7NNS au gmail.com directly
and we'll figure it out.
"""

# TODO: add an option to specify the output format. Currently, only "RtSys"
# exists.


# Convert CSV file from ACS 217 spreadsheet to format RT Systems uses for FT-60

import csv
import errno
import getopt
import os
import signal
import string
import sys

import ics217

# See below for the ics217 subclasses responsible for formatting the
# output.

def main():
    ifile = sys.stdin

    reader = csv.reader(ifile)

    bands = 'VU'
    count = 1
    output = RtSys
    try:
        (optlist, args) = getopt.getopt(sys.argv[1:], 'hb:s:', ['help'])
        for flag, value in optlist:
            if flag in ('-h', '--help'):
                print(usage)
                return 0
            elif flag == '-b':
                bands = value
            elif flag == '-s':
                try:
                    count = int(value)
                except ValueError:
                    print(f"-s '{value}' needs to be an integer", file=sys.stderr)
                    return 2
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        print(usage, file=sys.stderr)
        return 2

    output.header(sys.stdout)

    for l in reader:
        acsRec = ics217.parse(l, bands)
        if not acsRec:
            continue

        try:
            output.write(acsRec, sys.stdout, count)
        except Exception as e:
            # Parse failures are normal, don't report them; they just clutter
            # the output.
            #print("Failed to parse: ", l, file=sys.stderr)
            #print(e, file=sys.stderr)
            continue

        count += 1


class RtSys(object):
    """This is the "generic" RT Systems code. It generates output that
    both Yaesu FT-60 and QRZ-1 are happy with. Other radios might
    want something different; we may make subclasses for those
    radios at some later date."""
    # Output schema is based on the Yaesu FT-60, without bank select
    # TODO: RxTone, RxDCS. For now, always set to CSQ.
    @staticmethod
    def header(ofile):
        """Write out the header line for the CSV file."""
        print(",Receive Frequency,Transmit Frequency,Offset Frequency,Offset Direction,Operating Mode,Name,Show Name,Tone Mode,CTCSS,DCS,Skip,Step,Clock Shift,Tx Power,Tx Narrow,Pager Enable,Comment,", file=ofile)

    @staticmethod
    def write(icsrec, ofile, count):
        """Write out one record. This may throw an exception if any of
        the ics-217 fields are not valid."""
        # There are some derived values here, so we compute them now.
        Chan = icsrec.Chan       # memory #, 0-based
        Config = icsrec.Config
        Name = icsrec.Name       # memory label
        Comment = icsrec.Comment
        Rxfreq = icsrec.Rxfreq       # RX freq
        Wide = icsrec.Txwid
        Txfreq = icsrec.Txfreq       # RX freq
        Tone = icsrec.Txtone
        Remarks = icsrec.Remarks

        Offset = float(Txfreq) - float(Rxfreq)
        if Config == 'Simplex' or Txfreq == Rxfreq:
            Offset_s = ''
        elif abs(Offset) < 1.0:
            Offset_s = "%.0f kHz" % (abs(Offset)*1000.)
        else:
            Offset_s = "%.4f MHz" % abs(Offset)

        if Config == 'Simplex' or Txfreq == Rxfreq:
            Mode = "Simplex"
        elif Offset > 0:
            Mode = "Plus"
        else:
            Mode = "Minus"

        if Tone.startswith('CSQ'):
            ToneMode = 'None'
            Tone = ''
            Dcs = ''
        elif Tone.startswith('D'):
            ToneMode = 'DCS'
            Dcs = Tone[1:]
            Tone = ''
        else:
            ToneMode = 'Tone'
            Dcs = ''

        if Comment and Remarks:
            Comment = Comment + '; ' + Remarks
        elif Remarks:
            Comment = Remarks

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

        print(f"{count},{Rxfreq},{Txfreq},{Offset_s},{Mode},Auto,{Name},{'Y' if Name else 'N'},{ToneMode},{Tone},{Dcs},Scan,Auto,N,High,{'Y' if Wide=="N" else 'N'},N,{Comment}", file=ofile)


if __name__ == '__main__':
    sys.exit(main())

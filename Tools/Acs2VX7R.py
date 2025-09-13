#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Convert CSV file from ACS 217 spreadsheet to format RT Systems uses for VX-7R

import csv
import sys

import ics217
import common

class VX7R(object):
    """This generats the CSV file that a VX-7R uses."""
    # Output schema is based on the Yaesu VX-7R
    # TODO: RxTone, RxDCS. For now, always set to CSQ.
    @staticmethod
    def header(csvout: csv.writer, bank: int):
        """Write out the header line for the CSV file."""
        # Ignore bank; this radio doesn't use it
        csvout.writerow(["#","Tag","Freq","Mode","Scn Md","Step","Masked","RPT SH","Shift","TS/DCS","Tone","DCS","TX Pwr","Dev","Clk Sh","Icon"])

    @staticmethod
    def write(icsrec: ics217, csvout: csv.writer, count: int, bank: int):
        """Write out one record. This may throw an exception if any of
        the ics-217 fields are not valid."""
        # There are some derived values here, so we compute them now.
        Config = icsrec.Config
        Rxfreq = icsrec.Rxfreq       # RX freq
        Txfreq = icsrec.Txfreq       # TX freq
        Shift = float(Txfreq) - float(Rxfreq)

        if Config == 'Simplex' or Txfreq == Rxfreq:
            Shift_s = ''
        else:
            Shift_s = "%.1f" % abs(Shift)

        Chan = icsrec.Chan       # memory #, 0-based
        Tag = icsrec.Name       # memory label
        Mode = icsrec.Txwid + "FM"
        RptSh = "SIMP" if Config == "Simplex" else \
                "RPT+" if Shift > 0 else "RPT-"
        Tone = icsrec.Txtone

        if Tone.startswith('CSQ'):
            TSDCS = 'OFF'
            Tone = ''
            Dcs = ''
        elif Tone.startswith('D'):
            TSDCS = 'DCS'
            Dcs = Tone[1:]
            Tone = ''
        else:
            TSDCS = 'TONE'
            Dcs = ''

        csvout.writerow([count, Tag, Rxfreq, Mode, 'Off', '5 kHz', 'False', RptSh, Shift_s, TSDCS, Tone, Dcs,'MAX', 'NORM', 'OFF', 13])

if __name__ == '__main__':
    sys.exit(common.main(VX7R))

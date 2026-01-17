#!/usr/bin/env python3
# -*- coding: utf8 -*-

# This is the base class for holding radio programming
# info.
#
# Channel class holds the following values:
#
#  group
#    Not commonly used. Some radios, e.g. TK-780, divide the
#    channels into groups. Normally leave this unset.
#
#  channel
#    The channel number. Caller is responsible for making sure
#    this works for the radio in question. ACS 217 files have channel
#    numbers like "V01" or "U22" so obviously the software is going to
#    have to provide its own numbering when writing out the CSV files.
#
#  txfreq
#    Transmit frequency, Hz. Specify as a string; it will be
#    converted if necessary
#
#  rxfreq
#    Receive frequency, Hz. Specify as a string; it will be
#    converted if necessary
#
#  offset
#    difference between txfreq and rxfreq: txfreq-rxfreq
#
#    It's not necessary to set all of txfreq, rxfreq, and offset.
#    For simplex, just set one of txfreq or rxfreq (or set them both
#    to the same value). For duplex, set two and the third will be
#    derived if needed.
#
#  name
#
#  comment
#
#  txtone
#    numeric CTCSS tone or Dnnn. Unset implies "CSQ".
#
#  rxtone
#    numeric CTCSS tone or Dnnn. Unset implies "CSQ".
#
#  mode: AM, FM, etc.
#
#  wide: 'W', 'N'
#
#  power:
#    Prefer a number representing watts. "high", "med", "low"
#    if necessary. Subclasses that write out CSV files are
#    responsible for converting if necessary.

import sys
import decimal

# Schema:
#   0 group, usually blank
#   1 CH#
#   2 txfreq
#   3 rxfreq
#   4 offset
#   5 name
#   6 comment
#   7 txtone
#   8 rxtone
#   9 mode
#  10 wide
#  11 power


def csvget(value):
    """Return numeric value in a form suitable for a csv file"""
    if value is None: return ''
    value = str(value)
    if '"' in value: value = value.replace('"', '\\"')
    if ',' in value: value = '"' + value + '"'
    return value


class Channel(object):
    """Create one channel object. Caller is responsible for ensuring that
    txfreq and rxfreq are both valid. If offset is not provided, it will
    be computed from txfreq and rxfreq. All other fields must be provided."""
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        group, channel, txfreq, rxfreq, offset, \
            name, comment, txtone, rxtone, mode, wide, power = args
        if offset is None:
            try:
                tf = decimal.Decimal(txfreq)
                rf = decimal.Decimal(rxfreq)
                offset = str(tf - rf)
            except:
                pass    # no helping it
        if txfreq is None:
            try:
                rf = decimal.Decimal(rxfreq)
                off = decimal.Decimal(offset)
                txfreq = str(rf + off)
            except:
                pass    # no helping it
        if rxfreq is None:
            try:
                tf = decimal.Decimal(txfreq)
                off = decimal.Decimal(offset)
                rxfreq = str(tf - off)
            except:
                pass    # no helping it

        self.Group = group
        self.Chan = channel
        self.Txfreq = txfreq
        self.Rxfreq = rxfreq
        self.Offset = offset
        self.Name = name
        self.Comment = comment
        self.Txtone = txtone
        self.Rxtone = rxtone
        self.Mode = mode
        self.Wide = wide
        self.Power = power

    def __repr__(self):
        return f'''Channel({repr(self.Group)}, {repr(self.Chan)}, {repr(self.Txfreq)}, {repr(self.Rxfreq)}, {repr(self.Offset)}, {repr(self.Name)}, {repr(self.Comment)}, {repr(self.Txtone)}, {repr(self.Rxtone)}, {repr(self.Mode)}, {repr(self.Wide)}, {repr(self.Power)})'''

    @staticmethod
    def FromValues(line):
        """Given a list, most likely provided by a csv module, return
        a channel object or None if the list can't be parsed."""
        if len(line) < 12:
            return None
        try:
            return Channel(*line)
        except Exception as e:
            print(f"Failed to parse input: {e}", file=sys.stderr)
            return None

    def ToValues(self):
        """Convert to a list of values."""
        return [self.Group,
                self.Chan,
                self.Txfreq,
                self.Rxfreq,
                self.Offset,
                self.Name,
                self.Comment,
                self.Txtone,
                self.Rxtone,
                self.Mode,
                self.Wide,
                self.Power]

    @staticmethod
    def parse(line, recFilter, cls=None):
        """Given a list, most likely provided by the csv module, return
        an ics217 object or None if the list can't be parsed."""
        if not cls: cls = Channel
        regex = recFilter.get('regex')
        if len(line) < 12: return None
        if regex and not regex.match(line[1]):
            return None
        # line[4] must be a valid rx frequency
        if not line[4]:
            return None
        try:
            rxfreq = float(line[4])
        except:
            return None
        try:
            return cls(line)
        except Exception as e:
            print("Failed to parse: ", line, file=sys.stderr)
            print(e, file=sys.stderr)
            return None


# ---- program


usage = f"""Convert CSV file from ACS 217 spreadsheet to formats radios use

  {sys.argv[0]} < W7ACS_ICS-217A_20240131.csv > Chirp/acs.csv

  Options:
        --Chirp         Output for Chirp (default)
        --RtSys         Output for RT Systems
        --Icom          Output for Icom
        --IC-92         Output for Icom-92, RT Systems
        -R <regex>      Use regex to select entries from "channel" (2nd) column
        -s <n>          Start numbering at <n>; default is 1
        -B <banks>      Select banks for devices that use it (i.e. FT-60)
        -v              Increase verbosity

Generates CSV files to be used as code plugs.  These files
should work with any radio, but if not, please contact Ed Falk,
KK7NNS au gmail.com directly and we'll figure it out.
"""



if __name__ == '__main__':
  import common
  import signal
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(common.main(Channel, usage))
  except KeyboardInterrupt as e:
    print(file=sys.stderr)
    sys.exit(1)



# chan = Channel(None, "3", "146.9", "146.3", "-0.6",
#         "PSRG", "This is a comment", "103.5", None, 'W', '5W')
# print(chan)
# print(f"  {chan.Txfreq}  {chan.Rxfreq}  {chan.Offset}")
# print(chan.ToValues())
# l = chan.ToValues()
# chan2 = Channel.FromValues(l)
# print(chan2)

# 
# chan = Channel(None, "3", "146.9", "146.3", None,
#         "PSRG", "This is a comment", "103.5", None, 'W', '5W')
# print(chan)
# print(f"  {chan.Txfreq}  {chan.Rxfreq}  {chan.Offset}")
# 
# chan = Channel(None, "3", "146.9", None, "-0.6",
#         "PSRG", "This is a comment", "103.5", None, 'W', '5W')
# print(chan)
# print(f"  {chan.Txfreq}  {chan.Rxfreq}  {chan.Offset}")
# 
# chan = Channel(2, "3", "146.9", "146.3", "-0.6",
#         "PSRG", "This is a comment", "103.5", None, 'W', '5W')
# print(chan)
# print(f"  {chan.Txfreq}  {chan.Rxfreq}  {chan.Offset}")
# 
# chan = Channel(2, "3", "146.9", "146.3", "-0.6",
#         "PSRG", None, "103.5", None, 'W', '5W')
# print(chan)
# print(f"  {chan.Txfreq}  {chan.Rxfreq}  {chan.Offset}")
# 

# print(csvget("foo"))
# print(csvget("foo bar"))
# print(csvget("foo, bar"))
# print(csvget(None))
# print(csvget(''))
# print(csvget("that's all"))
# print(csvget('that"s all'))

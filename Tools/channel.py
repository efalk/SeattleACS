#!/usr/bin/env python3
# -*- coding: utf8 -*-

# This is the base class for holding radio programming
# info.
#
# Channel class holds the following values:
#
#  Group
#    Not commonly used. Some radios, e.g. TK-780, divide the
#    channels into groups. Normally leave this unset.
#
#  Channel
#    The channel number. Caller is responsible for making sure
#    this works for the radio in question. ACS 217 files have channel
#    numbers like "V01" or "U22" so obviously the software is going to
#    have to provide its own numbering when writing out the CSV files.
#
#  Txfreq
#    Transmit frequency, Hz. Specify as a string; it will be
#    converted if necessary
#
#  Rxfreq
#    Receive frequency, Hz. Specify as a string; it will be
#    converted if necessary
#
#  Offset
#    difference between txfreq and rxfreq: txfreq-rxfreq
#
#    It's not necessary to set all of txfreq, rxfreq, and offset.
#    For simplex, just set one of txfreq or rxfreq (or set them both
#    to the same value). For duplex, set two and the third will be
#    derived if needed.
#
#  Name
#
#  Comment
#
#  Txtone
#    numeric CTCSS tone or Dnnn.
#
#  Rxtone
#    numeric CTCSS tone or Dnnn.
#
#  Mode: AM, FM, etc.
#
#  Wide: 'W', 'N'
#
#  Power:
#    Prefer a number representing watts. "high", "med", "low"
#    if necessary. Subclasses that write out CSV files are
#    responsible for converting if necessary.
#
#  Skip:
#    This channel should not be included in scans

import re
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

callsign_re = re.compile(r'''[A-Z]+\d[A-Z]+(-\d+)?''')  # callsign with optional -nn
callsign_l_re = re.compile(r'''[A-Z]+\d[A-Z]+-\d+''')   # callsign with non-optional -nn

def csvget(value):
    """Return numeric value in a form suitable for a csv file"""
    if value is None: return ''
    value = str(value)
    if '"' in value: value = value.replace('"', '\\"')
    if ',' in value: value = '"' + value + '"'
    return value


class Channel(object):
    """Channel data base class. Can parse a generic format."""

    # INPUT SECTION (there is no output section)

    @staticmethod
    def probe(line: list):
        """Examine line to see if the input is in Chirp format. Return
        None if not. Anything else is true."""
        return len(line) >= 12 and \
            line[0] == "group" and \
            line[1] == "chan" and \
            line[2] == "txfreq" and \
            line[3] == "rxfreq" and \
            line[4] == "offset" and \
            line[5] == "name" and \
            line[6] == "comment" and \
            line[7] == "txtone" and \
            line[8] == "rxtone" and \
            line[9] == "mode" and \
            line[10] == "wide" and \
            line[11] == "power"


    def __init__(self, recFilter: dict, *args):
        """Create one channel object. Caller is responsible for ensuring that
        txfreq and rxfreq are both valid. If offset is not provided, it will
        be computed from txfreq and rxfreq. All other fields must be provided."""
        if len(args) == 1:
            args = args[0]
        group, channel, txfreq, rxfreq, offset, \
            name, comment, txtone, rxtone, mode, wide, power = args
        if not txfreq:
            if offset:
                try:
                    rf = decimal.Decimal(rxfreq)
                    off = decimal.Decimal(offset)
                    txfreq = str(rf + off)
                except:
                    pass    # no helping it
            else:
                txfreq = rxfreq
        if not rxfreq:
            if offset:
                try:
                    tf = decimal.Decimal(txfreq)
                    off = decimal.Decimal(offset)
                    rxfreq = str(tf - off)
                except:
                    pass    # no helping it
            else:
                rxfreq = txfreq
        if not offset:
            try:
                tf = decimal.Decimal(txfreq)
                rf = decimal.Decimal(rxfreq)
                offset = str(tf - rf)
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
        self.Skip = 'skip' in recFilter
        if recFilter.get('longName'):
            self.Name = self.getName()

    def __repr__(self):
        return f'''Channel({repr(self.Group)}, {repr(self.Chan)}, {repr(self.Txfreq)}, {repr(self.Rxfreq)}, {repr(self.Offset)}, {repr(self.Name)}, {repr(self.Comment)}, {repr(self.Txtone)}, {repr(self.Rxtone)}, {repr(self.Mode)}, {repr(self.Wide)}, {repr(self.Power)})'''

    def getName(this):
        """Return a reasonable long-form name for this item; incorporate the
        name and comment."""
        # If the name field is not a call sign and a call sign can be
        # found in the comment, append that call sign to the name. If
        # call sign with a dash, e.g. KK7ABC-10 is found, prefer that
        # to a simple call sign.
        #print(f"name:{this.Name}, comment:{this.Comment}")
        mo_l = callsign_l_re.search(this.Comment)
        mo = callsign_re.search(this.Comment)
        if not this.Name:
            # No name at all, look for a callsign in the comment, else the first
            # word of the comment, else nothing.
            if mo_l:
                return mo_l.group()
            if mo:
                return mo.group()
            if this.Comment:
                return this.Comment.split()[0]
            return this.Name
        elif callsign_l_re.search(this.Name):     # Can't really improve on this
            return this.Name
        elif callsign_re.search(this.Name):
            # Callsign but no dash; look for one with a dash in the comment
            if mo_l:
                return this.Name + ' ' + mo_l.group()
            else:
                return this.Name
        else:
            # No callsign in the name, look for one in the comment
            if mo_l:
                return this.Name + ' ' + mo_l.group()
            if mo:
                return this.Name + ' ' + mo.group()
            else:
                return this.Name


    @staticmethod
    def parse(line, recFilter, cls=None):
        """Given a list, most likely provided by the csv module, return
        an ics217 object or None if the list can't be parsed."""
        if not cls: cls = Channel
        regex = recFilter.get('regex')
        if len(line) < 12: return None
        if regex and not regex.match(line[1]):
            return None
        # At least one of rxfreq, txfreq must be provided
        if not line[2] and not line[3]:
            return None
        try:
            txfreq = float(line[2])
        except:
            try:
                rxfreq = float(line[3])
            except:
                return None
        try:
            rval = cls(recFilter, line)
            return rval if rval.testFilter(recFilter) else None
        except Exception as e:
            print("Failed to parse: ", line, file=sys.stderr)
            print(e, file=sys.stderr)
            return None

    bandList = ((1.8,54.0,'L'), (144.0,148.0,'V'), (219.0,225.0,'T'),
        (420.0,450.0,'U'), (462.55,467.725,'G'))

    def testFilter(self, recFilter):
        """Confirm that this record passes the filter."""
        bands = recFilter.get('bands')
        if bands:   # VULTGH
            found = False
            if 'H' in bands: bands += 'G'   # H and G are the same band
            rxfreq = float(self.Rxfreq)
            for band in Channel.bandList:
                if rxfreq >= band[0] and rxfreq <= band[1]:
                    found = True
                    if band[2] not in bands: return False
                    break
            if not found:       # not in any of our bands; should not happen
                return False
        return True

# ---- program


usage = f"""Convert CSV file to formats radios use

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

Input file format:

A CSV file with the following columns:

  group       sub-group within radio; typically empty
  channel     channel #
  txfreq      transmit (uplink) frequency, MHz
  rxfreq      recieve (downlink) frequency, MHz
  offset      difference between uplink, downlink, MHz
  name        display name in radio
  comment     comment
  txtone      CTCSS tone or DCS code for tx, may be nn.n, Dnn, or empty
  rxtone      CTCSS tone or DCS code for rx, usually empty for CSQ
  mode        AM, FM, M=digital voice, D=data, etc.
  wide        W/N
  power       watts or "HIGH" or "LOW". May be blank.

At least one of txfreq or rxfreq must be provided; if one is missing,
but offset is provided, the other is computed. If offset is missing
or zero, then txfreq and rxfreq are equal.
If offset is not provided, it is computed as txfreq-rxfreq
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

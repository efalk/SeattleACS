#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cgi
import csv
import glob
import io
import os
import sys

sys.path.append('../Tools')

import common
from chirp import Chirp
from rtsys import RtSys
from icom import Icom

# Explanation: running a test server on my system, the CWD as seen
# by this script is "CodePlugORama". When run under production,
# it's "CodePlugORama/cgi-bin".
# In both cases, the generated error html is based in CodePlugORama/cgi-bin
# and hrefs need to start with "../"

_topdir = "" if os.path.isdir("Sources") else "../"
_sourcedir = _topdir + "Sources"

_sources = {'ACS ICS 217': 'W7ACS_ICS-217A_WORKING.csv',
    'ACS Winlink list': 'winlink.csv',
    'Repeater Roundabout': 'RepeaterRoundabout.csv',
    'Seattle emergency hubs': 'hub_GMRS.csv',
    'Medical Services Team': 'ww7mst.csv',
    'WWARA': 'WWARA-rptrlist-*.csv',
    'GMRS': 'gmrs.csv',
    'MURS': 'murs.csv',
    'Upload …': None}

_bands = {'hf':'L', 'vhf':'V', 'vhf2':'T', 'uhf':'U', 'gmrs':'G', 'digital':'D'}

_modes = {'FM':'F', 'AM':'A', 'LSB':'L', 'USB':'U', 'CW':'C', 'DMR':'D', 'DSTAR':'S',
    'PKT':'d', 'P25':'d', 'NXDN':'d', 'ATV':'d', 'DATV':'d', 'DIG':'d', }   # TODO: these modes

_writers = { "Chirp":Chirp, "RT Systems":RtSys, "Icom":Icom}

_names = { "Chirp":'Chirp', "RT Systems":'RtSys', "Icom":'Icom'}

def main():
    form = cgi.FieldStorage()

    # Debug only
    #print('Content-Type: text/plain; charset=utf-8')
    #print()
    #print(os.getcwd())

    #print(f"cwd = {os.getcwd()}")
    #print(f"topdir = {_topdir}")
    #print(f"sourcedir = {_sourcedir}")
    #print()

    # Select the source
    try:
        source = form.getvalue('source')
        #print(source)
        if not source: die("Invalid form submission")
        ifile = getInputFile(source, form)
    except NameError as e:
        die(f"Invalid form submission\n{e}")

    # Check for filter options
    recFilter = {}

    if form.getvalue('bandFilter'):
        #print("bandfilter yes")
        bands = []
        for k in _bands.keys():
            if form.getvalue(k):
                bands.append(_bands[k])
        bands = ''.join(bands)
        #print(f"bands: {bands}")
        if bands: recFilter['bands'] = bands

    if form.getvalue('modeFilter'):
        #print("modefilter yes")
        modes = []
        for k in _modes.keys():
            if form.getvalue(k):
                modes.append(_modes[k])
        modes = ''.join(modes)
        #print(f"modes: {modes}")
        if modes: recFilter['modes'] = modes

    writer = Chirp
    outputFormat = form.getvalue('outputFormat')
    writer = _writers[outputFormat]
    #print(f"format: {outputFormat}")
    #print(f"writer: {writer}")

    start = form.getvalue('start')
    try:
        start = int(start)
    except:
        start = 1

    if form.getvalue('longNames'):
        recFilter['longName'] = True
        #print("long names")

    if form.getvalue('sparse'):
        recFilter['sparse'] = True
        #print("sparse")

    if form.getvalue('skip'):
        recFilter['skip'] = True
        #print("sparse")

    #print()
    #print('----')
    #for key in form.keys():
        #print(f"{key}: {form.getvalue(key)}")


    #print()
    #print('----')
    # And go
    csvin = csv.reader(ifile)

    reader = common.findReader(csvin)
    if not reader:
        filename = form['fileInput'].filename
        print(_errorUnknownFormat % filename)
        return 0

    csvout = csv.writer(sys.stdout)

    # OK, we've done all the sanity checks we can, time to spit out
    # the results.

    # TODO: incorporate some more metadata into the filename?
    # Source? Timestamp?
    outputName = 'CodePlugORama_' + _names[form.getvalue('outputFormat')]
    print('Content-Type: text/csv; charset=utf-8')
    print(f'Content-Disposition: attachment; filename="{outputName}.csv"')
    print()
    try:
        common.process(csvin, reader, csvout, writer, start, recFilter)
    except common.ProcessException as e:
        print("Fatal:", e)
        return 3
    return 0

def getInputFile(source: str, form: cgi.FieldStorage):
    if source not in _sources: die("Invalid form submission")
    ifilename = _sources[source]
    if ifilename:
        ifilename = os.path.join(_sourcedir, _sources[source])
        if '*' in ifilename:
            l = glob.glob(ifilename)
            if not l:
                die("Internal error: source db not found")
            ifilename = l[0]
        try:
            return open(ifilename, "r")
        except Exception as e:
            die(f"Internal error: {e}")
    else:
        fileInput = form['fileInput']
        return io.TextIOWrapper(fileInput.file, encoding='utf-8', errors='ignore')


def die(message):
    print('Content-Type: text/plain; charset=utf-8')
    print('Status: 400 invalid input')
    print()
    print(message)
    sys.exit(3)

_errorUnknownFormat = rf"""Content-Type: text/html; charset=utf-8')
Status: 400 unknown format

<!DOCTYPE HTML>
<html lang="en">
<head>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<META name="viewport" content="width=500, initial-scale=1">
<title>Welcome to Code Plug O'Rama</title>

<link rel=StyleSheet href="../style.css" type="text/css">
</head>

<body>
  <div id="page-wrap">
    <header>
      <div class="welcome">
	<p align=center> Welcome to Code Plug O'Rama</p>
      </div>
    </header>
  <div class="page-content">
<p>Unfortunately, I was unable to determine the format of the input
file "%s".
Please make sure that the header line is intact and that the input
file is in one of the formats listed in <a
href="../help.html#accepted-formats" target="CodePlugHelp">Accepted Formats</a>.</p>

</div>	<!-- wrap-content -->
</div>	<!-- page-wrap -->

</body>
</html>
"""

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt as e:
        print()
        sys.exit(1)
    except Exception as e:
        print("Failed, error", e, sys.stderr)
        print("Failed, error", e)
        sys.exit(3)

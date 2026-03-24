#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cgi
import csv
import io
import os
import sys

sys.path.append('../Tools')

import common
from chirp import Chirp
from rtsys import RtSys
from icom import Icom

SOURCEDIR = "../Sources"    # Depends on your server.

_sources = {'ACS ICS 217': 'W7ACS_ICS-217A_WORKING.csv',
    'ACS Winlink list': 'winlink.csv',
    'Repeater Roundabout': 'RepeaterRoundabout.csv',
    'Seattle emergency hubs': 'hub_GMRS.csv',
    'WWARA': 'WWARA-rptrlist-20260317.csv',
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

    # Select the source
    try:
        source = form.getvalue('source')
        #print(source)
        if not source: die("Invalid form submission")
        ifile = getInputFile(source, form)
        #print(ifile)
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

    # TODO: incorporate some more metadata into the filename?
    outputName = 'CodePlugORama_' + _names[form.getvalue('outputFormat')]
    print('Content-Type: text/csv; charset=utf-8')
    print(f'Content-Disposition: attachment; filename="{outputName}.csv"')
    print()

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

    #print()
    #print('----')
    #for key in form.keys():
        #print(f"{key}: {form.getvalue(key)}")


    #print()
    #print('----')
    # And go
    csvin = csv.reader(ifile)
    csvout = csv.writer(sys.stdout)
    common.process(csvin, None, csvout, writer, start, recFilter)
    return 0

def getInputFile(source: str, form: cgi.FieldStorage):
    if source not in _sources: die("Invalid form submission")
    ifilename = os.path.join(SOURCEDIR, _sources[source])
    if ifilename:
        try:
            return open(ifilename, "r")
        except Exception as e:
            die(f"Internal error: {e}")
    fileInput = form['fileInput']
    return io.TextIOWrapper(fileInput.file, encoding='utf-8', errors='ignore')


def die(message):
    print('Content-Type: text/plain; charset=utf-8')
    print('Status: 400 invalid input')
    print()
    print(message)
    sys.exit(0)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt as e:
        print()
        sys.exit(1)

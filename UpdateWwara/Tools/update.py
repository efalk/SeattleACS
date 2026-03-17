#!/usr/bin/env python3
# -*- coding: utf8 -*-

import csv
import errno
import glob
import os
import re
import shutil
import signal
import sys
import zipfile

from ezt import Template

verbose = 0

def main():
    global verbose

    # Step 1: update the database

    try:
        os.mkdir("New")
    except OSError as e:
        pass  # already exists; let it go

    curl("https://www.wwara.org/DataBaseExtract.zip", "New/DataBaseExtract.zip")

    zfile = zipfile.ZipFile("New/DataBaseExtract.zip", 'r')
    zfile.extractall("New")
    zfile.close()

    filename = glob.glob("New/WWARA-rptrlist*.csv")
    if not filename:
        print("WWARA-rptrlist*.csv not found in archive", file=sys.stderr)
        return 3
    filename = os.path.basename(filename[0])

    if os.path.exists(filename):
        # Nothing to do
        return 0

    if not os.path.exists("Chirp"):
        os.mkdir("Chirp")

    if not os.path.exists("RtSys"):
        os.mkdir("RtSys")

    rval = os.system(f'./Tools/Wwara2Csv.py --Chirp "New/{filename}" > Chirp/wwara_chirp.csv')
    if rval:
        print("Generate Chirp failed", file=sys.stderr)
        return 3

    rval = os.system(f'./Tools/Wwara2Csv.py --RtSys "New/{filename}" > RtSys/wwara_rt.csv')
    if rval:
        print("Generate RT Sys failed", file=sys.stderr)
        return 3

    csvfiles = glob.glob('*.csv')
    for file in csvfiles:
        os.unlink(file)

    os.rename(os.path.join("New", filename), filename)

    # Step 2: update the web page

    data = {}
    mo = re.match(r'''WWARA-rptrlist-(\d\d\d\d)(\d\d)(\d\d).csv''', filename)
    if not mo:
        print(f"Error: unable to extract date from \"{filename}\"")
        return 2

    data["year"] = mo.group(1)
    data["month"] = mo.group(2)
    data["day"] = mo.group(3)

    template = Template("index.ezt")

    ofile = open("index.html", "w")
    template.generate(ofile, data)

    return 0


import urllib.request

def curl(src, dst):
    with urllib.request.urlopen(src) as ifile, open(dst,'wb') as ofile:
        shutil.copyfileobj(ifile, ofile)


if __name__ == '__main__':
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    try:
        sys.exit(main())
    except KeyboardInterrupt as e:
        sys.exit(1)
    except Exception as e:
        print("Killed by exception", file=sys.stderr)
        raise
    finally:
        shutil.rmtree("New")

